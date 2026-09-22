# 🛡️ FinGuard AI — AI-Powered Personal Finance & Financial Risk Intelligence Platform

FinGuard AI is a comprehensive, demo-ready financial intelligence platform designed for individuals and analysts. It unifies transaction intelligence, machine learning anomaly detection, an audited 0–100 Financial Risk Engine, Indian equity technical/fundamental analytics (NSE/BSE), predictive cash flow forecasting, multi-agent AI advisory, and automated executive PDF reporting.

---

## ⚡ Quickstart (Demo-Ready)

### 1. Launch Application
With the virtual environment activated:
```bash
.venv\Scripts\streamlit.exe run app/app.py
```
Or with standard Python:
```bash
python -m streamlit run app/app.py
```

The application will immediately open in your browser at `http://localhost:8501`.
- **Zero Configuration Needed:** SQLite is pre-configured and pre-seeded with 12 months of realistic transactions, budgets, goals, debts, and investments.
- **Zero Crash Resilience:** Even if `GEMINI_API_KEY` or live stock internet access is unavailable, FinGuard automatically switches to high-fidelity deterministic analytical engines.

---

## 🚀 Step-by-Step 5-Minute Demo Flow

1. **🏠 Financial Health Dashboard:** Inspect real-time KPI cards (Income ₹1,25,000, Expenses, Net Savings, Financial Risk Score 38/100, Net Worth, Runway).
2. **💳 Transactions & CSV Ingestion:** View categorized Indian transactions. Download the sample CSV or upload any bank statement with automated column detection.
3. **📊 Expense Intelligence:** Review weekday vs weekend spending surge (+34% on weekends), category aggregations, and daily burn rates.
4. **🔬 Financial X-Ray:** View the structural breakdown:
   - *Risk:* Dining & Discretionary Food Concentration
   - *Evidence:* 22% of total spend
   - *Compounding Impact:* ₹58,000/year diversion
   - *Actionable Prescription:* Recommended automated limits.
5. **⚠️ Risk Center & Early Warning:** Examine the 0–100 Risk Gauge and explore the exact mathematical factor breakdown (Savings Rate, DTI Ratio, Emergency Buffer, Volatility, Recurring Commitments).
6. **📈 Stock AI & Trend Analyzer:** Enter `TCS.NS`, `RELIANCE.NS`, or `INFY.NS`. View live/cached prices, candlestick chart with 20/50 SMA and Bollinger Bands, 14-day RSI, fundamental multiples (P/E, Market Cap, ROE), and the AI Investment Outlook.
7. **🔮 Forecasting:** Inspect the 60-day predictive time-series projection for expenses and cash surplus.
8. **💡 Can I Afford This?:** Test simulating a **₹75,000 laptop**. FinGuard recalculates post-purchase liquid reserves and projected emergency runway.
9. **🤖 Ask FinGuard (Multi-Agent AI):** Query the system in natural language. Queries are automatically routed to the specialized agent (Financial Analyst, Risk Analyst, Stock Analyst, Forecasting Agent, Detective).
10. **🕵️ Financial Detective:** Review detected anomalies flagged by IQR, Z-Score, and Scikit-learn Isolation Forest.
11. **🧬 Risk DNA:** Explore the 6-axis radar behavioral persona.
12. **📄 Executive Reports:** Click **"Generate PDF Executive Report"** to export an audit-ready financial summary PDF powered by ReportLab.

---

## 🔬 Academic Data Science Project (`notebooks/`)
Located at `notebooks/Financial_Data_Analysis.ipynb`:
- Exploratory Data Analysis (EDA) on personal finance datasets
- Statistical hypothesis testing (Two-sample Welch's T-Test on weekend vs weekday spending)
- Unsupervised anomaly detection (Isolation Forest & IQR)
- Time-series decomposition and moving averages (7-day / 30-day)
- Mathematical derivation of the 0–100 Financial Risk Score.

---

## 🛠️ Technology Stack
- **Frontend:** Streamlit, Custom Glassmorphism CSS, Plotly Interactive Charts
- **Analytics & ML:** Pandas, NumPy, SciPy, Statsmodels, Scikit-learn
- **Database:** SQLite & SQLAlchemy
- **Market Data:** yfinance (NSE/BSE equities) with offline fallback caching
- **AI Intelligence:** Google Gemini API (`google-genai`) with grounded rule-based deterministic fallback
- **Reports:** ReportLab PDF Engine
