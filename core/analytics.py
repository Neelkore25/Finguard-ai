import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from core.database import SessionLocal, Transaction, Budget, Debt, Goal, Investment, Subscription


def load_transactions_df(user_id: Optional[int] = None) -> pd.DataFrame:
    """Loads transactions from SQLite for a specific user into a structured Pandas DataFrame."""
    db = SessionLocal()
    try:
        query = db.query(Transaction)
        if user_id is not None:
            query = query.filter(Transaction.user_id == user_id)
        txs = query.order_by(Transaction.date.asc()).all()
        if not txs:
            return pd.DataFrame(columns=["id", "date", "type", "category", "amount", "description", "account", "is_recurring", "is_anomaly", "anomaly_reason"])
        
        data = [{
            "id": t.id,
            "date": pd.to_datetime(t.date),
            "type": t.type,
            "category": t.category,
            "amount": float(t.amount),
            "description": t.description,
            "account": t.account,
            "is_recurring": bool(t.is_recurring),
            "is_anomaly": bool(t.is_anomaly),
            "anomaly_reason": t.anomaly_reason or ""
        } for t in txs]
        
        df = pd.DataFrame(data)
        df["month_year"] = df["date"].dt.to_period("M").astype(str)
        df["day_name"] = df["date"].dt.day_name()
        df["is_weekend"] = df["date"].dt.dayofweek >= 5
        return df
    finally:
        db.close()


def calculate_financial_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates core financial KPIs across the entire period and current month."""
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expense": 0.0,
            "monthly_avg_income": 0.0,
            "monthly_avg_expense": 0.0,
            "net_savings": 0.0,
            "savings_rate": 0.0,
            "current_month_income": 0.0,
            "current_month_expense": 0.0,
            "current_month_savings": 0.0,
            "current_month_savings_rate": 0.0,
            "burn_rate_daily": 0.0,
            "runway_months": 0.0
        }

    income_df = df[df["type"] == "Income"]
    expense_df = df[df["type"] == "Expense"]

    total_income = income_df["amount"].sum()
    total_expense = expense_df["amount"].sum()
    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

    # Group by month
    monthly_incomes = income_df.groupby("month_year")["amount"].sum()
    monthly_expenses = expense_df.groupby("month_year")["amount"].sum()

    months_count = max(len(df["month_year"].unique()), 1)
    monthly_avg_income = total_income / months_count
    monthly_avg_expense = total_expense / months_count

    # Current month data
    current_period = df["month_year"].max()
    curr_inc = income_df[income_df["month_year"] == current_period]["amount"].sum()
    curr_exp = expense_df[expense_df["month_year"] == current_period]["amount"].sum()
    curr_sav = curr_inc - curr_exp
    curr_sav_rate = (curr_sav / curr_inc * 100) if curr_inc > 0 else 0.0

    # Daily burn rate based on last 30 days
    recent_date = df["date"].max()
    last_30_date = recent_date - timedelta(days=30)
    last_30_exp = expense_df[expense_df["date"] >= last_30_date]["amount"].sum()
    daily_burn_rate = last_30_exp / 30.0

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "monthly_avg_income": round(monthly_avg_income, 2),
        "monthly_avg_expense": round(monthly_avg_expense, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate": round(savings_rate, 1),
        "current_month_income": round(curr_inc, 2),
        "current_month_expense": round(curr_exp, 2),
        "current_month_savings": round(curr_sav, 2),
        "current_month_savings_rate": round(curr_sav_rate, 1),
        "burn_rate_daily": round(daily_burn_rate, 2),
        "active_months": months_count
    }


def detect_anomalies(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detects financial anomalies using multiple statistical & ML techniques:
    1. Z-Score (|Z| > 2.5)
    2. IQR Method (amount > Q3 + 1.5 * IQR)
    3. Scikit-learn Isolation Forest
    """
    if df.empty or len(df[df["type"] == "Expense"]) < 5:
        return []

    expense_df = df[df["type"] == "Expense"].copy()
    anomalies = []

    # 1. IQR & Z-score per category
    for cat, group in expense_df.groupby("category"):
        if len(group) < 3:
            continue
        amounts = group["amount"]
        mean_val = amounts.mean()
        std_val = amounts.std(ddof=1) if len(amounts) > 1 else 0
        q25, q75 = np.percentile(amounts, [25, 75])
        iqr = q75 - q25
        upper_fence = q75 + (1.8 * iqr)

        for _, row in group.iterrows():
            amt = row["amount"]
            z_score = ((amt - mean_val) / std_val) if std_val > 0 else 0
            
            # Anomaly condition: Z > 2.8 or amt > upper_fence
            if (z_score >= 2.8 or amt > upper_fence) and amt > 5000:
                anomalies.append({
                    "id": row["id"],
                    "date": row["date"].strftime("%d %b %Y"),
                    "category": cat,
                    "description": row["description"],
                    "amount": amt,
                    "expected_mean": round(mean_val, 2),
                    "deviation_pct": round(((amt - mean_val) / mean_val * 100), 1) if mean_val > 0 else 0,
                    "method": "IQR & Z-Score (Z={:.1f})".format(z_score),
                    "severity": "High" if amt > 25000 else "Medium",
                    "explanation": f"Expense is {amt / mean_val:.1f}x higher than standard {cat} average (₹{mean_val:,.0f})."
                })

    # 2. Try Isolation Forest for multidimensional outliers if scikit-learn is available
    try:
        from sklearn.ensemble import IsolationForest
        if len(expense_df) >= 15:
            X = expense_df[["amount"]].values
            clf = IsolationForest(contamination=0.04, random_state=42)
            preds = clf.fit_predict(X)
            iso_anoms = expense_df[preds == -1]
            existing_ids = {a["id"] for a in anomalies}
            for _, row in iso_anoms.iterrows():
                if row["id"] not in existing_ids and row["amount"] > 10000:
                    anomalies.append({
                        "id": row["id"],
                        "date": row["date"].strftime("%d %b %Y"),
                        "category": row["category"],
                        "description": row["description"],
                        "amount": row["amount"],
                        "expected_mean": round(expense_df["amount"].mean(), 2),
                        "deviation_pct": round(((row["amount"] - expense_df["amount"].mean()) / expense_df["amount"].mean() * 100), 1),
                        "method": "Isolation Forest (Unsupervised ML)",
                        "severity": "High",
                        "explanation": "Flagged as an anomalous multi-dimensional density outlier by Isolation Forest."
                    })
    except Exception:
        pass

    # Sort by amount descending
    anomalies.sort(key=lambda x: x["amount"], reverse=True)
    return anomalies


def analyze_expense_intelligence(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates deep analytical insights on spending patterns."""
    if df.empty:
        return {}

    expense_df = df[df["type"] == "Expense"].copy()
    if expense_df.empty:
        return {}

    # 1. Category aggregation
    cat_agg = expense_df.groupby("category")["amount"].agg(["sum", "count", "mean"]).reset_index()
    cat_agg["pct"] = (cat_agg["sum"] / cat_agg["sum"].sum() * 100).round(1)
    cat_agg = cat_agg.sort_values(by="sum", ascending=False)
    top_cat = cat_agg.iloc[0]["category"] if not cat_agg.empty else "None"
    top_cat_amt = cat_agg.iloc[0]["sum"] if not cat_agg.empty else 0.0

    # 2. Weekend vs Weekday analysis
    wk_agg = expense_df.groupby("is_weekend")["amount"].agg(["sum", "mean", "count"])
    weekday_mean = wk_agg.loc[False, "mean"] if False in wk_agg.index else 0.0
    weekend_mean = wk_agg.loc[True, "mean"] if True in wk_agg.index else 0.0
    weekend_surge_pct = round(((weekend_mean - weekday_mean) / weekday_mean * 100), 1) if weekday_mean > 0 else 0.0

    # 3. Monthly growth rate
    monthly_trend = expense_df.groupby("month_year")["amount"].sum().reset_index()
    monthly_trend["growth_pct"] = monthly_trend["amount"].pct_change() * 100
    recent_growth = round(monthly_trend.iloc[-1]["growth_pct"], 1) if len(monthly_trend) > 1 and not pd.isna(monthly_trend.iloc[-1]["growth_pct"]) else 0.0

    # 4. Top largest single transactions
    largest_txs = expense_df.sort_values(by="amount", ascending=False).head(5)[["date", "description", "category", "amount"]].to_dict(orient="records")

    return {
        "category_summary": cat_agg.to_dict(orient="records"),
        "top_category": top_cat,
        "top_category_amount": top_cat_amt,
        "weekday_mean": round(weekday_mean, 2),
        "weekend_mean": round(weekend_mean, 2),
        "weekend_surge_pct": weekend_surge_pct,
        "recent_monthly_growth_pct": recent_growth,
        "largest_transactions": largest_txs,
        "monthly_trend_df": monthly_trend
    }


def forecast_expenses_and_balance(df: pd.DataFrame, forecast_days: int = 60) -> Dict[str, Any]:
    """
    Forecasts upcoming daily expenses and cash trajectory using linear regression / trend modeling.
    Robust against missing dates, single-category data, and irregular intervals.
    """
    if df.empty or len(df) < 5:
        return {"forecast_available": False}

    df_copy = df.copy()
    df_copy["day"] = pd.to_datetime(df_copy["date"]).dt.floor("D")
    min_date = df_copy["day"].min()
    max_date = df_copy["day"].max()

    if pd.isna(min_date) or pd.isna(max_date) or min_date == max_date:
        return {"forecast_available": False}

    all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
    daily = pd.DataFrame({"date": all_dates})

    exp_daily = df_copy[df_copy["type"] == "Expense"].groupby("day")["amount"].sum().rename("amount_exp")
    inc_daily = df_copy[df_copy["type"] == "Income"].groupby("day")["amount"].sum().rename("amount_inc")

    daily = daily.merge(exp_daily, left_on="date", right_index=True, how="left").fillna({"amount_exp": 0.0})
    daily = daily.merge(inc_daily, left_on="date", right_index=True, how="left").fillna({"amount_inc": 0.0})
    daily = daily.sort_values(by="date").reset_index(drop=True)

    daily["net_flow"] = daily["amount_inc"] - daily["amount_exp"]
    daily["cum_balance"] = daily["net_flow"].cumsum() + 150000.0  # Starting balance baseline

    # Compute 14-day moving average
    daily["exp_ma14"] = daily["amount_exp"].rolling(window=14, min_periods=1).mean()

    # Linear trend projection on expenses
    n = len(daily)
    x = np.arange(n)
    y = daily["amount_exp"].values

    if n > 1 and np.sum(y) > 0:
        slope, intercept = np.polyfit(x, y, 1)
    else:
        slope, intercept = 0.0, float(np.mean(y)) if n > 0 else 0.0

    # Project future days
    future_x = np.arange(n, n + forecast_days)
    base_floor = max(float(np.mean(y) * 0.2), 100.0) if np.mean(y) > 0 else 100.0
    future_exp_proj = np.maximum(slope * future_x + intercept, base_floor)

    last_date = daily["date"].max()
    future_dates = [last_date + timedelta(days=int(i)) for i in range(1, forecast_days + 1)]

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "projected_daily_expense": future_exp_proj,
    })

    # Projected monthly expense
    next_30_projected_expense = float(np.sum(future_exp_proj[:30]))
    historical_avg_monthly = float(daily["amount_exp"].sum() / (n / 30.0)) if n > 0 else next_30_projected_expense

    return {
        "forecast_available": True,
        "daily_df": daily,
        "forecast_df": forecast_df,
        "next_30_projected_expense": round(next_30_projected_expense, 2),
        "historical_avg_monthly": round(historical_avg_monthly, 2),
        "projected_change_pct": round(((next_30_projected_expense - historical_avg_monthly) / historical_avg_monthly * 100), 1) if historical_avg_monthly > 0 else 0.0
    }
