import sys
import os
from pathlib import Path

# Ensure application and project root are in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="FinGuard AI | Financial Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom glassmorphism styles
try:
    from app.styles import CUSTOM_CSS
except ImportError:
    from styles import CUSTOM_CSS

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Import Core Engines & Database
from core.database import init_db, SessionLocal, User, Transaction, Budget, Goal, Debt, Investment, Subscription, Reminder, hash_password, verify_password
from core.demo_data import seed_demo_data, clear_user_data
from core.analytics import load_transactions_df, calculate_financial_kpis, detect_anomalies, analyze_expense_intelligence, forecast_expenses_and_balance
from core.risk_engine import compute_financial_risk_score, generate_financial_xray, generate_risk_dna_profile
from core.stock_engine import fetch_stock_data, normalize_ticker
from core.ai_engine import route_agent, generate_agent_response
from core.pdf_generator import generate_executive_pdf

# Ensure database tables exist
init_db()

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏠 Dashboard"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "Hello! I am **FinGuard AI**, your autonomous financial intelligence partner. Ask me about your spending patterns, risk score, stock outlooks, or upcoming purchase affordability!"}
    ]


# ==========================================
# 2. UNIQUE ACCOUNT SYSTEM (AUTH SCREEN)
# ==========================================
if not st.session_state["authenticated"]:
    col_l1, col_l2, col_l3 = st.columns([1, 2.2, 1])
    with col_l2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="font-size: 2.6rem; margin-bottom: 4px;">🛡️</div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #00D2FF 0%, #7000FF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">FIN GUARD AI</h1>
            <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 4px;">Autonomous Financial Risk & Decision Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Log In to Account", "✨ Create New Account"])

        # LOGIN TAB
        with tab_login:
            with st.form("login_form"):
                log_email = st.text_input("Email Address", placeholder="name@example.com").strip().lower()
                log_pass = st.text_input("Password", type="password", placeholder="Enter your password")
                
                c_btn1, c_btn2 = st.columns([1, 1])
                with c_btn1:
                    login_submit = st.form_submit_button("Log In", type="primary", use_container_width=True)
                with c_btn2:
                    demo_submit = st.form_submit_button("⚡ Quick Demo Access", use_container_width=True)

            if login_submit:
                if not log_email or not log_pass:
                    st.error("Please enter both email and password.")
                else:
                    db = SessionLocal()
                    user = db.query(User).filter(User.email == log_email).first()
                    db.close()
                    if user and verify_password(log_pass, user.password_hash):
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = user.id
                        st.session_state["user_name"] = user.name
                        st.session_state["user_email"] = user.email
                        st.success(f"Welcome back, {user.name}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again or create an account.")

            # QUICK DEMO LOGIN
            if demo_submit:
                db = SessionLocal()
                demo_user = db.query(User).filter(User.email == "alex.morgan@fintech.ai").first()
                if not demo_user:
                    demo_user = User(
                        name="Alex Morgan",
                        email="alex.morgan@fintech.ai",
                        password_hash=hash_password("DemoPass123")
                    )
                    db.add(demo_user)
                    db.commit()
                    db.refresh(demo_user)
                    # Seed demo data for this demo user
                    seed_demo_data(user_id=demo_user.id, force=True)
                db.close()

                st.session_state["authenticated"] = True
                st.session_state["user_id"] = demo_user.id
                st.session_state["user_name"] = demo_user.name
                st.session_state["user_email"] = demo_user.email
                st.success("Loaded demo account! Redirecting to command center...")
                st.rerun()

        # SIGNUP TAB (FRESH USER WITH ZERO DATA)
        with tab_signup:
            with st.form("signup_form"):
                sig_name = st.text_input("Full Name", placeholder="Your Name").strip()
                sig_email = st.text_input("Email Address", placeholder="name@example.com").strip().lower()
                sig_pass = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters")
                sig_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

                signup_submit = st.form_submit_button("Create Free Account", type="primary", use_container_width=True)

            if signup_submit:
                if not sig_name or not sig_email or not sig_pass or not sig_confirm:
                    st.error("Please fill in all required fields.")
                elif sig_pass != sig_confirm:
                    st.error("Password and Confirm Password do not match.")
                elif len(sig_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    db = SessionLocal()
                    existing_user = db.query(User).filter(User.email == sig_email).first()
                    if existing_user:
                        st.error("An account with this email already exists.")
                        db.close()
                    else:
                        new_user = User(
                            name=sig_name,
                            email=sig_email,
                            password_hash=hash_password(sig_pass)
                        )
                        db.add(new_user)
                        db.commit()
                        db.refresh(new_user)
                        user_id = new_user.id
                        db.close()

                        # Brand new user starts with ZERO transactions, ZERO fake data!
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = user_id
                        st.session_state["user_name"] = sig_name
                        st.session_state["user_email"] = sig_email
                        st.success(f"Account created successfully for {sig_name}! Starting with fresh telemetry.")
                        st.rerun()

    st.stop()


# ==========================================
# MULTI-TENANT USER DATA SCOPING
# ==========================================
current_user_id = st.session_state["user_id"]
current_user_name = st.session_state["user_name"]
current_user_email = st.session_state["user_email"]

# Load transactions strictly scoped to current user
df = load_transactions_df(user_id=current_user_id)
kpis = calculate_financial_kpis(df)
risk_data = compute_financial_risk_score(kpis, df, user_id=current_user_id)


# ==========================================
# 3 & 4. INTERACTIVE GROUPED NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 12px 0;">
        <h2 style="margin:0; font-size: 1.55rem; font-weight: 800; background: linear-gradient(135deg, #00D2FF, #7000FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🛡️ FinGuard AI</h2>
        <p style="margin:0; font-size: 0.76rem; color: #94A3B8;">Autonomous Financial Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # Active User Pill
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 10px 12px; margin-bottom: 12px;">
        <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Active Account</div>
        <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; margin: 2px 0;">👤 {current_user_name}</div>
        <div style="font-size: 0.75rem; color: #38BDF8; overflow: hidden; text-overflow: ellipsis;">{current_user_email}</div>
    </div>
    """, unsafe_allow_html=True)

    # Clean Grouped Navigation Map
    nav_categories = {
        "COMMAND CENTER": [
            "🏠 Dashboard"
        ],
        "MONEY": [
            "💳 Transactions",
            "🏦 Accounts",
            "📊 Expense Intelligence",
            "💰 Budgets",
            "🔄 Subscriptions"
        ],
        "FINANCIAL HEALTH": [
            "🔬 Financial X-Ray",
            "⚠️ Risk Center",
            "🧬 Risk DNA",
            "🕵 Financial Detective",
            "🎯 Goals",
            "💸 Debt",
            "🔮 Forecasting"
        ],
        "DECISION TOOLS": [
            "💡 Can I Afford This?",
            "🧪 What-If Simulator",
            "⚡ Financial Stress Test",
            "📅 Financial Calendar"
        ],
        "INVESTMENTS": [
            "📈 Portfolio",
            "📊 Stock AI Analyzer"
        ],
        "AI CENTER": [
            "🤖 Ask FinGuard",
            "💡 AI Insights"
        ],
        "REPORTS & SETTINGS": [
            "📄 Financial Report",
            "👤 Profile",
            "⚙️ Security & Data"
        ]
    }

    # Flatten list of pages for selection
    all_pages = []
    page_to_group = {}
    for group_name, pages in nav_categories.items():
        for p in pages:
            all_pages.append(p)
            page_to_group[p] = group_name

    selected_group = st.selectbox(
        "Navigation Hub",
        list(nav_categories.keys()),
        index=0,
        key="nav_group_selector"
    )

    selected_page = st.radio(
        f"Select Feature ({selected_group})",
        nav_categories[selected_group],
        key="nav_page_selector"
    )

    st.markdown("---")

    # Demo / Data Controls Scoped to Current User
    if len(df) > 0:
        st.markdown('<div class="demo-pill">📊 Active Data Loaded</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #94A3B8; font-size: 0.8rem; margin-bottom: 8px;">✨ Fresh Zero-Data Account</div>', unsafe_allow_html=True)

    c_d1, c_d2 = st.columns(2)
    with c_d1:
        if st.button("⚡ Load Demo", help="Populates your account with realistic demo data for testing", use_container_width=True):
            seed_demo_data(user_id=current_user_id, force=True)
            st.success("Demo dataset loaded into your account!")
            st.rerun()
    with c_d2:
        if st.button("🗑️ Clear Data", help="Removes all transactions from your account", use_container_width=True):
            clear_user_data(current_user_id)
            st.info("Your financial records have been reset to fresh state.")
            st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["user_name"] = ""
        st.session_state["user_email"] = ""
        st.rerun()


# ==========================================
# 6. DASHBOARD (FRESH ZERO-STATE OR RICH TELEMETRY)
# ==========================================
if selected_page == "🏠 Dashboard":
    st.markdown('<div class="hero-header">Financial Command Center</div>', unsafe_allow_html=True)

    # 1. FRESH ACCOUNT ONBOARDING STATE (WHEN 0 TRANSACTIONS)
    if df.empty:
        st.markdown(f"""
        <div class="onboarding-hero">
            <div class="onboarding-title">Welcome to FinGuard AI, {current_user_name}! 👋</div>
            <div class="onboarding-subtitle">
                Your personal financial intelligence command center is ready and completely fresh. No fabricated numbers, no generic placeholders. Add your first transaction or set a goal to unlock automated behavioral analysis, machine learning risk detection, and predictive forecasting.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🚀 Quick Onboarding Launchpad")
        oa1, oa2, oa3, oa4 = st.columns(4)
        with oa1:
            st.markdown("""
            <div class="action-card">
                <div class="action-card-title">💳 1. Add First Transaction</div>
                <div class="action-card-desc">Log your salary, freelance payment, or an expense to calibrate your baseline cash flow.</div>
            </div>
            """, unsafe_allow_html=True)
        with oa2:
            st.markdown("""
            <div class="action-card">
                <div class="action-card-title">💰 2. Set Category Budgets</div>
                <div class="action-card-desc">Establish monthly limits for dining, transport, and bills to prevent lifestyle creep.</div>
            </div>
            """, unsafe_allow_html=True)
        with oa3:
            st.markdown("""
            <div class="action-card">
                <div class="action-card-title">🎯 3. Define Savings Goal</div>
                <div class="action-card-desc">Target an emergency reserve or vacation milestone with automated progress tracking.</div>
            </div>
            """, unsafe_allow_html=True)
        with oa4:
            st.markdown("""
            <div class="action-card">
                <div class="action-card-title">📈 4. Explore Stock AI</div>
                <div class="action-card-desc">Analyse Indian equities (TCS, RELIANCE, INFY) with live indicators and AI outlooks.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # 6 CORE KPI CARDS (Shows actual numbers or clean zero state)
    net_worth = kpis.get("net_savings", 0) + risk_data.get("portfolio_value", 0) - risk_data.get("total_debt", 0)
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💎 Net Worth</div>
            <div class="metric-value" style="font-size: 1.45rem;">₹{net_worth:,.0f}</div>
            <div class="metric-delta delta-pos">Assets − Debt</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💵 Monthly Income</div>
            <div class="metric-value" style="font-size: 1.45rem;">₹{kpis.get('current_month_income', 0):,.0f}</div>
            <div class="metric-delta delta-pos">Avg: ₹{kpis.get('monthly_avg_income', 0):,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💳 Monthly Outflow</div>
            <div class="metric-value" style="font-size: 1.45rem;">₹{kpis.get('current_month_expense', 0):,.0f}</div>
            <div class="metric-delta delta-neutral">Burn: ₹{kpis.get('burn_rate_daily', 0):,.0f}/d</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        sav_pct = kpis.get('current_month_savings_rate', 0)
        s_cls = "delta-pos" if sav_pct >= 20 else ("delta-neg" if sav_pct > 0 else "delta-neutral")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💰 Savings Rate</div>
            <div class="metric-value" style="font-size: 1.45rem;">{sav_pct:.1f}%</div>
            <div class="metric-delta {s_cls}">Target: >25%</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        score_val = f"{risk_data.get('score')} <span style='font-size: 0.8rem; color:#94A3B8;'>/100</span>" if len(df) > 0 else "--"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🛡️ Risk Score</div>
            <div class="metric-value" style="font-size: 1.45rem; color: {risk_data.get('color')};">{score_val}</div>
            <div class="metric-delta {risk_data.get('badge_class')}">{risk_data.get('status')}</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        runway_val = f"{risk_data.get('runway_months', 0):.1f} <span style='font-size: 0.8rem; color:#94A3B8;'>Mo</span>" if len(df) > 0 else "0.0 Mo"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⏳ Emergency Buffer</div>
            <div class="metric-value" style="font-size: 1.45rem;">{runway_val}</div>
            <div class="metric-delta delta-neutral">Target: 6.0 Mo</div>
        </div>
        """, unsafe_allow_html=True)

    # 7. PROMINENT ADD TRANSACTION FLOW
    with st.expander("➕ **+ Add Transaction** (Instantly Updates Dashboard & Analysis)", expanded=df.empty):
        with st.form("dashboard_add_tx_form"):
            qa1, qa2, qa3, qa4, qa5 = st.columns(5)
            with qa1:
                q_date = st.date_input("Date", datetime.now())
            with qa2:
                q_type = st.selectbox("Type", ["Income", "Expense"])
            with qa3:
                q_cat = st.selectbox("Category", ["Salary", "Freelance", "Food", "Rent", "Transport", "Shopping", "Bills", "Investments", "Entertainment", "Healthcare", "Education", "Other"])
            with qa4:
                q_amt = st.number_input("Amount (₹)", min_value=1.0, value=50000.0 if q_type == "Income" else 1500.0, step=100.0)
            with qa5:
                q_desc = st.text_input("Description", "Monthly Tech Salary" if q_type == "Income" else "Grocery Shopping")

            if st.form_submit_button("Save & Record Transaction", type="primary", use_container_width=True):
                db = SessionLocal()
                new_tx = Transaction(
                    user_id=current_user_id,
                    date=datetime.combine(q_date, datetime.min.time()),
                    type=q_type,
                    category=q_cat,
                    amount=q_amt,
                    description=q_desc,
                    account="Primary Checking"
                )
                db.add(new_tx)
                db.commit()
                db.close()
                st.success(f"Recorded ₹{q_amt:,.2f} {q_type} ({q_cat})! Telemetry updated immediately.")
                st.rerun()

    # DASHBOARD CHARTS (IF DATA AVAILABLE)
    if not df.empty:
        col_ch1, col_ch2 = st.columns([6, 4])
        with col_ch1:
            st.subheader("📊 Cash Flow Trajectory (Income vs Expenses)")
            monthly_summary = df.groupby(["month_year", "type"])["amount"].sum().reset_index()
            fig = px.bar(
                monthly_summary,
                x="month_year",
                y="amount",
                color="type",
                barmode="group",
                color_discrete_map={"Income": "#10B981", "Expense": "#EF4444"},
                labels={"amount": "Amount (₹)", "month_year": "Month"}
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_ch2:
            st.subheader("🥧 Expense Category Breakdown")
            exp_df = df[df["type"] == "Expense"]
            if not exp_df.empty:
                cat_totals = exp_df.groupby("category")["amount"].sum().reset_index()
                fig_pie = px.pie(
                    cat_totals,
                    values="amount",
                    names="category",
                    hole=0.55,
                    color_discrete_sequence=px.colors.sequential.Tealgrn_r
                )
                fig_pie.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No expense transactions recorded yet.")


# ==========================================
# 8. INTERACTIVE TRANSACTIONS PAGE & CSV INGESTION
# ==========================================
elif selected_page == "💳 Transactions":
    st.markdown('<div class="hero-header">Transaction Management Hub & Statement Ingestion</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Interactive transaction search, multi-filter aggregation, manual logging, and automated CSV bank statement ingestion.</div>', unsafe_allow_html=True)

    # 1. CSV Statement Ingestion & Sample Download
    with st.expander("📂 **CSV Statement Ingestion & Sample Download**", expanded=False):
        c_csv1, c_csv2 = st.columns([1, 2])
        with c_csv1:
            st.markdown("#### 📥 Sample Statement")
            st.markdown("Download our standardized demo CSV template to test instant bulk transaction ingestion.")
            sample_csv_path = os.path.join(PROJECT_ROOT, "data", "sample_transactions.csv")
            if os.path.exists(sample_csv_path):
                with open(sample_csv_path, "rb") as f:
                    csv_bytes = f.read()
                st.download_button(
                    label="⬇️ Download Sample CSV",
                    data=csv_bytes,
                    file_name="sample_transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.caption("Sample CSV template located in data/")

        with c_csv2:
            st.markdown("#### 📤 Upload Bank Statement (CSV)")
            uploaded_csv = st.file_uploader("Select CSV statement from your bank", type=["csv"], key="tx_csv_uploader")
            if uploaded_csv is not None:
                try:
                    up_df = pd.read_csv(uploaded_csv)
                    st.write(f"Detected **{len(up_df)}** rows. Inspecting schema...")

                    # Intelligent column detection
                    col_map = {}
                    for c in up_df.columns:
                        c_low = c.strip().lower()
                        if any(k in c_low for k in ["date", "time", "timestamp"]):
                            col_map["date"] = c
                        elif any(k in c_low for k in ["category", "tag"]):
                            col_map["category"] = c
                        elif any(k in c_low for k in ["desc", "narration", "particular", "remark", "payee"]):
                            col_map["description"] = c
                        elif any(k in c_low for k in ["account", "bank", "mode"]):
                            col_map["account"] = c
                        elif any(k in c_low for k in ["type", "cr/dr", "d/c"]):
                            col_map["type"] = c
                        elif any(k in c_low for k in ["amount", "amt", "val"]):
                            col_map["amount"] = c

                    if "date" in col_map and "amount" in col_map:
                        preview_list = []
                        for _, r in up_df.head(5).iterrows():
                            preview_list.append({
                                "Date": str(r[col_map["date"]]),
                                "Amount": r[col_map["amount"]],
                                "Type": r.get(col_map.get("type", ""), "Expense"),
                                "Category": r.get(col_map.get("category", ""), "Other"),
                                "Description": r.get(col_map.get("description", ""), "Bank Statement Record")
                            })
                        st.dataframe(pd.DataFrame(preview_list), use_container_width=True)

                        if st.button("🚀 Ingest All Transactions Into Account", type="primary"):
                            db = SessionLocal()
                            added_count = 0
                            for _, r in up_df.iterrows():
                                try:
                                    p_date = pd.to_datetime(r[col_map["date"]])
                                    p_amt = abs(float(r[col_map["amount"]]))
                                    p_type = str(r.get(col_map.get("type", ""), "Expense")).capitalize()
                                    if p_type not in ["Income", "Expense"]:
                                        p_type = "Income" if "cr" in p_type.lower() or "deposit" in p_type.lower() else "Expense"
                                    p_cat = str(r.get(col_map.get("category", ""), "Other"))
                                    p_desc = str(r.get(col_map.get("description", ""), "CSV Ingested"))
                                    p_acc = str(r.get(col_map.get("account", ""), "Primary Checking"))

                                    db.add(Transaction(
                                        user_id=current_user_id,
                                        date=p_date.to_pydatetime() if hasattr(p_date, 'to_pydatetime') else datetime.now(),
                                        type=p_type,
                                        category=p_cat,
                                        amount=p_amt,
                                        description=p_desc,
                                        account=p_acc
                                    ))
                                    added_count += 1
                                except Exception:
                                    continue
                            db.commit()
                            db.close()
                            st.success(f"✅ Successfully ingested {added_count} transactions into your account!")
                            st.rerun()
                    else:
                        st.warning("Could not automatically locate 'Date' and 'Amount' columns. Please verify column headers.")
                except Exception as e:
                    st.error(f"Error reading CSV: {e}")

    # 2. Inline Add Transaction
    with st.expander("➕ **Add New Transaction Manually**", expanded=False):
        with st.form("tx_page_form"):
            fa, fb, fc = st.columns(3)
            with fa:
                t_date = st.date_input("Date", datetime.now())
                t_type = st.selectbox("Type", ["Expense", "Income"])
            with fb:
                t_cat = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Rent", "Salary", "Freelance", "Investments", "Healthcare", "Education", "Entertainment", "Other"])
                t_amt = st.number_input("Amount (₹)", min_value=1.0, value=1500.0, step=50.0)
            with fc:
                t_desc = st.text_input("Description", "Dining at Cafe")
                t_acc = st.selectbox("Account", ["Primary Checking", "Credit Card", "Savings Bank", "Cash"])

            if st.form_submit_button("Record Transaction", type="primary"):
                db = SessionLocal()
                new_t = Transaction(
                    user_id=current_user_id,
                    date=datetime.combine(t_date, datetime.min.time()),
                    type=t_type,
                    category=t_cat,
                    amount=t_amt,
                    description=t_desc,
                    account=t_acc
                )
                db.add(new_t)
                db.commit()
                db.close()
                st.success("Transaction added successfully!")
                st.rerun()

    # 3. Search & Filters
    sf1, sf2, sf3, sf4 = st.columns([3, 2, 2, 2])
    with sf1:
        s_query = st.text_input("🔍 Search description / vendor...", value="")
    with sf2:
        cats = ["All Categories"] + sorted(df["category"].unique().tolist()) if not df.empty else ["All Categories"]
        s_cat = st.selectbox("Category Filter", cats)
    with sf3:
        s_type = st.selectbox("Type Filter", ["All Types", "Expense", "Income"])
    with sf4:
        s_sort = st.selectbox("Sort Order", ["Latest First", "Oldest First", "Amount High-to-Low", "Amount Low-to-High"])

    filtered_df = df.copy()
    if s_query:
        filtered_df = filtered_df[filtered_df["description"].str.contains(s_query, case=False, na=False)]
    if s_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == s_cat]
    if s_type != "All Types":
        filtered_df = filtered_df[filtered_df["type"] == s_type]

    # Sorting
    if not filtered_df.empty:
        if s_sort == "Latest First":
            filtered_df = filtered_df.sort_values(by="date", ascending=False)
        elif s_sort == "Oldest First":
            filtered_df = filtered_df.sort_values(by="date", ascending=True)
        elif s_sort == "Amount High-to-Low":
            filtered_df = filtered_df.sort_values(by="amount", ascending=False)
        elif s_sort == "Amount Low-to-High":
            filtered_df = filtered_df.sort_values(by="amount", ascending=True)

    # Metrics
    tot_inc = filtered_df[filtered_df["type"] == "Income"]["amount"].sum()
    tot_exp = filtered_df[filtered_df["type"] == "Expense"]["amount"].sum()
    net_cf = tot_inc - tot_exp

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Income (Filtered)", f"₹{tot_inc:,.0f}")
    with m2: st.metric("Total Expenses (Filtered)", f"₹{tot_exp:,.0f}")
    with m3: st.metric("Net Cash Flow", f"₹{net_cf:,.0f}", f"{(net_cf/tot_inc*100) if tot_inc > 0 else 0:.1f}%")
    with m4: st.metric("Transactions Found", f"{len(filtered_df)}")

    if not filtered_df.empty:
        disp_cols = ["date", "type", "category", "amount", "description", "account"]
        st.dataframe(
            filtered_df[disp_cols].style.format({"amount": "₹{:,.2f}"}),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No matching transactions. Record a transaction above, load demo data, or upload a bank CSV statement.")


# ==========================================
# 8b. ACCOUNTS BREAKDOWN & BALANCES
# ==========================================
elif selected_page == "🏦 Accounts":
    st.markdown('<div class="hero-header">Financial Accounts & Liquidity Balances</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Consolidated view of balances across checking, credit, savings, and cash accounts.</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("ℹ️ **No Account Data:** Record transactions or load demo data to view real-time account balances.")
    else:
        accounts = df["account"].unique().tolist()
        acc_stats = []
        for acc in accounts:
            a_df = df[df["account"] == acc]
            inc = a_df[a_df["type"] == "Income"]["amount"].sum()
            exp = a_df[a_df["type"] == "Expense"]["amount"].sum()
            net = inc - exp
            acc_stats.append({
                "Account": acc,
                "Inflows": inc,
                "Outflows": exp,
                "Net Balance": net,
                "Transactions": len(a_df)
            })

        acc_summary_df = pd.DataFrame(acc_stats)

        # Overview cards
        tot_liq = acc_summary_df["Net Balance"].sum()
        a1, a2, a3 = st.columns(3)
        with a1: st.metric("Total Liquid Net Position", f"₹{tot_liq:,.0f}")
        with a2: st.metric("Total Accounts Monitored", f"{len(accounts)}")
        with a3: st.metric("Active Monthly Cashflow", f"₹{kpis.get('monthly_avg_income', 0):,.0f}")

        # Account Cards Grid
        st.markdown("### 💳 Monitored Accounts")
        cols = st.columns(min(len(accounts), 4) if len(accounts) > 0 else 1)
        for idx, row in acc_summary_df.iterrows():
            with cols[idx % len(cols)]:
                b_color = "#10B981" if row["Net Balance"] >= 0 else "#EF4444"
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 12px;">
                    <div class="metric-title">🏦 {row['Account']}</div>
                    <div class="metric-value" style="color: {b_color}; font-size: 1.35rem;">₹{row['Net Balance']:,.0f}</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 6px;">
                        In: <span style="color:#10B981;">₹{row['Inflows']:,.0f}</span> | Out: <span style="color:#EF4444;">₹{row['Outflows']:,.0f}</span>
                    </div>
                    <div style="font-size: 0.75rem; color: #38BDF8; margin-top: 4px;">{row['Transactions']} Transactions logged</div>
                </div>
                """, unsafe_allow_html=True)

        # Bar chart
        fig_acc = px.bar(
            acc_summary_df,
            x="Account",
            y="Net Balance",
            color="Net Balance",
            color_continuous_scale="Tealgrn",
            labels={"Net Balance": "Net Balance (₹)"}
        )
        fig_acc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_acc, use_container_width=True)


# ==========================================
# 9. EXPENSE INTELLIGENCE
# ==========================================
elif selected_page == "📊 Expense Intelligence":
    st.markdown('<div class="hero-header">Expense Intelligence & Behavioral Analytics</div>', unsafe_allow_html=True)

    if df.empty or len(df[df["type"] == "Expense"]) < 2:
        st.info("ℹ️ **Insufficient Data:** Add at least 2 expense transactions to generate automated spending intelligence.")
    else:
        exp_intel = analyze_expense_intelligence(df)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">👑 Top Spending Category</div>
                <div class="metric-value" style="font-size: 1.45rem;">{exp_intel.get('top_category', 'None')}</div>
                <div class="metric-delta delta-neg">₹{exp_intel.get('top_category_amount', 0):,.0f} Total</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🗓️ Weekday Avg Burn</div>
                <div class="metric-value">₹{exp_intel.get('weekday_mean', 0):,.0f}</div>
                <div class="metric-delta delta-neutral">Monday - Friday</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🎉 Weekend Avg Burn</div>
                <div class="metric-value">₹{exp_intel.get('weekend_mean', 0):,.0f}</div>
                <div class="metric-delta delta-neg">+{exp_intel.get('weekend_surge_pct', 0)}% Weekend Surge</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            g = exp_intel.get('recent_monthly_growth_pct', 0)
            g_cls = "delta-neg" if g > 0 else "delta-pos"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📈 MoM Spending Growth</div>
                <div class="metric-value">{g:+.1f}%</div>
                <div class="metric-delta {g_cls}">vs Previous Month</div>
            </div>
            """, unsafe_allow_html=True)

        # Category Chart
        cat_df = pd.DataFrame(exp_intel.get("category_summary", []))
        if not cat_df.empty:
            col_c1, col_c2 = st.columns([6, 4])
            with col_c1:
                fig_bar = px.bar(cat_df, x="category", y="sum", color="category", text_auto=".2s", labels={"sum": "Total Spending (₹)", "category": "Category"})
                fig_bar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            with col_c2:
                st.write("Category Aggregation:")
                st.dataframe(cat_df.rename(columns={"sum": "Total (₹)", "count": "Count", "mean": "Avg/Tx (₹)", "pct": "% Share"}).style.format({"Total (₹)": "₹{:,.0f}", "Avg/Tx (₹)": "₹{:,.0f}", "% Share": "{:.1f}%"}), use_container_width=True)


# ==========================================
# 10. FINANCIAL X-RAY & 11. RISK CENTER
# ==========================================
elif selected_page in ["🔬 Financial X-Ray", "⚠️ Risk Center"]:
    st.markdown('<div class="hero-header">Financial Risk Intelligence & Structural X-Ray</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("ℹ️ **No Telemetry Available:** Add income and expense transactions to calculate your transparent 0–100 risk score.")
    else:
        c1, c2 = st.columns([4, 6])
        with c1:
            st.subheader("Financial Risk Score Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_data.get("score", 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Risk: {risk_data.get('status')}", 'font': {'size': 18, 'color': '#FFFFFF'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': risk_data.get("color", "#10B981")},
                    'bgcolor': "rgba(255,255,255,0.05)",
                    'borderwidth': 2,
                    'bordercolor': "rgba(255,255,255,0.2)",
                    'steps': [
                        {'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.25)'},
                        {'range': [30, 60], 'color': 'rgba(245, 158, 11, 0.25)'},
                        {'range': [60, 80], 'color': 'rgba(239, 68, 68, 0.25)'},
                        {'range': [80, 100], 'color': 'rgba(185, 28, 28, 0.45)'}
                    ],
                }
            ))
            fig_gauge.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=280)
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.info(f"💡 **Evaluation Summary:** {risk_data.get('summary')}")

        with c2:
            st.subheader("Mathematical Factor Breakdown")
            for f in risk_data.get("breakdown", []):
                pct = (f["points"] / f["max"]) if f["max"] > 0 else 0
                col_fa, col_fb = st.columns([7, 3])
                with col_fa:
                    st.write(f"**{f['factor']}** (Status: *{f['status']}*)")
                    st.progress(pct)
                with col_fb:
                    st.markdown(f"**{f['points']} / {f['max']} pts**")

        st.markdown("### 🔬 Financial X-Ray Diagnostics")
        xray_findings = generate_financial_xray(df, risk_data, user_id=current_user_id)
        if xray_findings:
            for item in xray_findings:
                cls = "xray-danger" if item["severity"] == "Danger" else ("xray-warning" if item["severity"] == "Warning" else "xray-success")
                badge_style = "risk-high" if item["severity"] == "Danger" else ("risk-moderate" if item["severity"] == "Warning" else "risk-low")
                st.markdown(f"""
                <div class="xray-card {cls}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <h4 style="margin: 0; color: #FFFFFF;">{item['risk']}</h4>
                        <span class="risk-badge {badge_style}">{item['severity']}</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #CBD5E1; margin-bottom: 4px;">
                        <strong style="color: #00D2FF;">Telemetry Evidence:</strong> {item['evidence']}
                    </div>
                    <div style="font-size: 0.9rem; color: #CBD5E1; margin-bottom: 6px;">
                        <strong style="color: #F87171;">Compounding Impact:</strong> {item['impact']}
                    </div>
                    <div style="background: rgba(0, 210, 255, 0.08); border-radius: 8px; padding: 6px 10px; font-size: 0.85rem; color: #38BDF8;">
                        <strong>💡 Actionable Prescription:</strong> {item['action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No structural vulnerabilities or anomalies detected in your current transaction records.")


# ==========================================
# 12. RISK DNA & 13. FINANCIAL DETECTIVE
# ==========================================
elif selected_page in ["🧬 Risk DNA", "🕵 Financial Detective"]:
    st.markdown('<div class="hero-header">Behavioral Risk DNA & Anomaly Radar</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("ℹ️ **No Behavioral Data:** Log transactions to profile your risk persona and detect anomalous spending spikes.")
    else:
        dna = generate_risk_dna_profile(kpis, risk_data)
        c1, c2 = st.columns([5, 5])
        with c1:
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=dna["values"] + [dna["values"][0]],
                theta=dna["categories"] + [dna["categories"][0]],
                fill='toself',
                name='Persona',
                line=dict(color='#00D2FF', width=2),
                fillcolor='rgba(0, 210, 255, 0.25)'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8", gridcolor="rgba(255,255,255,0.1)"),
                    angularaxis=dict(color="#FFFFFF", gridcolor="rgba(255,255,255,0.1)")
                ),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                height=380
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with c2:
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-title">Persona Archetype</div>
                <div class="metric-value" style="color: #00D2FF; font-size: 1.5rem;">{dna['archetype']}</div>
                <p style="color: #CBD5E1; font-size: 0.92rem; line-height: 1.5; margin-top: 10px;">{dna['archetype_desc']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Anomaly Detection
        st.subheader("🕵️ Discovered Anomalies (IQR & Isolation Forest)")
        anomalies = detect_anomalies(df)
        if anomalies:
            for a in anomalies:
                st.markdown(f"""
                <div class="xray-card xray-warning">
                    <div style="display: flex; justify-content: space-between;">
                        <h4 style="margin:0; color: #FFFFFF;">🚨 {a['category']}: ₹{a['amount']:,.0f}</h4>
                        <span class="risk-badge risk-high">{a['severity']}</span>
                    </div>
                    <p style="margin: 4px 0; color: #CBD5E1;"><strong>Vendor:</strong> {a['description']} ({a['date']})</p>
                    <p style="margin: 2px 0; color: #94A3B8;"><strong>Reason:</strong> {a['method']} | Expected: ₹{a['expected_mean']:,.0f}</p>
                    <div style="background: rgba(239, 68, 68, 0.1); padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; color: #FCA5A5;">
                        {a['explanation']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No unusual spending anomalies detected in your records.")


# ==========================================
# 14. FORECASTING
# ==========================================
elif selected_page == "🔮 Forecasting":
    st.markdown('<div class="hero-header">Predictive Financial Outlook & Cash Runway</div>', unsafe_allow_html=True)

    if len(df) < 5:
        st.info("ℹ️ **Data Threshold Notice:** Add at least 5 transactions to generate linear regression time-series forecasting.")
    else:
        fc_res = forecast_expenses_and_balance(df)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Projected Next 30-Day Outflow", f"₹{fc_res.get('next_30_projected_expense', 0):,.0f}", f"{fc_res.get('projected_change_pct', 0):+.1f}%")
        with c2:
            st.metric("Historical Monthly Outflow", f"₹{fc_res.get('historical_avg_monthly', 0):,.0f}")
        with c3:
            surplus = kpis.get("monthly_avg_income", 0) - fc_res.get('next_30_projected_expense', 0)
            st.metric("Projected 30-Day Surplus", f"₹{surplus:,.0f}")

        if fc_res.get("forecast_available"):
            daily_df = fc_res["daily_df"]
            fc_df = fc_res["forecast_df"]
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["amount_exp"], mode="lines", name="Historical Daily Expense", line=dict(color="#38BDF8", width=1)))
            fig_fc.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["exp_ma14"], mode="lines", name="14-Day Moving Average", line=dict(color="#10B981", width=2)))
            fig_fc.add_trace(go.Scatter(x=fc_df["date"], y=fc_df["projected_daily_expense"], mode="lines", name="60-Day Projected Trend", line=dict(color="#F59E0B", dash="dash", width=2.5)))
            fig_fc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
            st.plotly_chart(fig_fc, use_container_width=True)


# ==========================================
# 15. DECISION TOOLS: AFFORDABILITY, WHAT-IF, STRESS TEST & CALENDAR
# ==========================================
elif selected_page in ["💡 Can I Afford This?", "🧪 What-If Simulator", "⚡ Financial Stress Test", "📅 Financial Calendar"]:
    st.markdown('<div class="hero-header">Financial Decision Support & Stress Testing</div>', unsafe_allow_html=True)

    tab_afford, tab_whatif, tab_stress, tab_cal = st.tabs([
        "💡 Can I Afford This?",
        "🧪 What-If Simulator",
        "⚡ Financial Stress Test",
        "📅 Financial Calendar"
    ])

    with tab_afford:
        c1, c2 = st.columns([4, 6])
        with c1:
            item_name = st.text_input("Planned Purchase", value="MacBook Pro Workstation")
            item_cost = st.number_input("Purchase Price (₹)", min_value=100.0, value=75000.0, step=2500.0)
        with c2:
            monthly_exp = max(kpis.get("monthly_avg_expense", 0), 1.0)
            liquid_reserves = kpis.get("net_savings", 0)
            remaining_reserves = liquid_reserves - item_cost
            new_runway = remaining_reserves / monthly_exp if monthly_exp > 0 else 0

            st.subheader("Decision Engine Output")
            if liquid_reserves == 0:
                st.warning("⚠️ **Record income or savings first to evaluate liquidity impact.**")
            elif item_cost <= liquid_reserves * 0.35 and new_runway >= 3.5:
                st.markdown('<span class="risk-badge risk-low">LOW IMPACT</span>', unsafe_allow_html=True)
                st.success(f"✅ **Safe to proceed.** Liquid runway remains at **{new_runway:.1f} months** after purchase.")
            elif remaining_reserves > 0:
                st.markdown('<span class="risk-badge risk-moderate">MODERATE IMPACT</span>', unsafe_allow_html=True)
                st.warning(f"⚠️ **Proceed with caution.** Runway reduces to **{new_runway:.1f} months**.")
            else:
                st.markdown('<span class="risk-badge risk-high">HIGH FINANCIAL STRESS</span>', unsafe_allow_html=True)
                st.error("❌ **Severe liquidity deficit.** This purchase exceeds current liquid net savings.")

    with tab_whatif:
        c1, c2 = st.columns(2)
        with c1:
            sim_income_pct = st.slider("Salary / Income Change (%)", -30, 50, 10, step=5)
            sim_exp_pct = st.slider("Monthly Expense Change (%)", -30, 50, 0, step=5)
        with c2:
            sim_new_emi = st.number_input("Add New Monthly EMI (₹)", 0, 50000, 0, step=2500)
            sim_new_sip = st.number_input("Add Monthly Investment SIP (₹)", 0, 50000, 5000, step=2500)

        base_inc = kpis.get("monthly_avg_income", 0)
        base_exp = kpis.get("monthly_avg_expense", 0)

        sim_inc = base_inc * (1 + sim_income_pct / 100.0)
        sim_exp = base_exp * (1 + sim_exp_pct / 100.0) + sim_new_emi + sim_new_sip
        sim_savings = sim_inc - sim_exp
        sim_sav_rate = (sim_savings / sim_inc * 100) if sim_inc > 0 else 0

        st.subheader("Simulation Results")
        sc1, sc2, sc3 = st.columns(3)
        with sc1: st.metric("Simulated Monthly Income", f"₹{sim_inc:,.0f}", f"{sim_income_pct:+d}%")
        with sc2: st.metric("Simulated Monthly Outflow", f"₹{sim_exp:,.0f}", f"₹{sim_exp - base_exp:+,.0f}")
        with sc3: st.metric("Simulated Savings Rate", f"{sim_sav_rate:.1f}%", f"{sim_sav_rate - kpis.get('savings_rate', 0):+.1f}%")

    with tab_stress:
        st.subheader("⚡ Macro & Black Swan Financial Stress Test")
        st.markdown("Simulate severe economic disruptions, loss of employment, and catastrophic medical outlays.")
        st1, st2, st3 = st.columns(3)
        with st1:
            income_drop_pct = st.slider("Income Shock (%)", 0, 100, 50, step=10, help="Simulate job loss or wage cut")
        with st2:
            emergency_cost = st.number_input("One-Time Emergency Shock (₹)", 0, 1000000, 50000, step=25000)
        with st3:
            inflation_surge_pct = st.slider("Cost Inflation Surge (%)", 0, 50, 15, step=5)

        cur_inc = kpis.get("monthly_avg_income", 0)
        cur_exp = kpis.get("monthly_avg_expense", 0)
        cur_savings = max(kpis.get("net_savings", 0), 0)

        stressed_inc = cur_inc * (1 - income_drop_pct / 100.0)
        stressed_exp = cur_exp * (1 + inflation_surge_pct / 100.0)
        post_shock_reserves = max(cur_savings - emergency_cost, 0.0)
        monthly_deficit = max(stressed_exp - stressed_inc, 0.0)

        survival_months = (post_shock_reserves / monthly_deficit) if monthly_deficit > 0 else 99.0

        r1, r2, r3 = st.columns(3)
        with r1: st.metric("Stressed Net Deficit / Mo", f"₹{monthly_deficit:,.0f}")
        with r2: st.metric("Liquid Buffer Post-Emergency", f"₹{post_shock_reserves:,.0f}")
        with r3: st.metric("Estimated Survival Window", f"{survival_months:.1f} Months" if survival_months < 90 else ">5 Years")

        if survival_months >= 6.0:
            st.success(f"🛡️ **High Resilience:** Even under this severe economic scenario, your reserves sustain you for **{survival_months:.1f} months**.")
        elif survival_months >= 3.0:
            st.warning(f"⚠️ **Moderate Vulnerability:** Reserves cover **{survival_months:.1f} months**. Recommended action: increase liquid sweep-in holdings.")
        else:
            st.error(f"🚨 **Critical Stress:** Under this scenario, liquid cash depletes within **{survival_months:.1f} months**! Aggressive emergency cushion building required.")

    with tab_cal:
        st.subheader("📅 Financial Calendar & Obligation Schedule")
        db = SessionLocal()
        c_debts = db.query(Debt).filter(Debt.user_id == current_user_id).all()
        c_subs = db.query(Subscription).filter(Subscription.user_id == current_user_id).all()
        c_reminders = db.query(Reminder).filter(Reminder.user_id == current_user_id).all()
        db.close()

        cal_events = []
        for d in c_debts:
            cal_events.append({"Day of Month": "5th", "Event": f"Loan EMI: {d.title}", "Amount": f"₹{d.monthly_emi:,.0f}", "Type": "Debt EMI", "Status": "Recurring"})
        for s in c_subs:
            cal_events.append({"Day of Month": "1st", "Event": f"Subscription: {s.name}", "Amount": f"₹{s.amount:,.0f}", "Type": "Subscription", "Status": "Active"})
        for r in c_reminders:
            cal_events.append({"Day of Month": r.due_date.strftime("%d %b"), "Event": r.title, "Amount": f"₹{r.amount:,.0f}", "Type": r.category, "Status": "Pending" if not r.is_completed else "Done"})

        if cal_events:
            st.dataframe(pd.DataFrame(cal_events), use_container_width=True)
        else:
            st.info("No scheduled obligations found. Add debts, subscriptions, or load demo data.")


# ==========================================
# 16. INVESTMENTS: PORTFOLIO & STOCK AI
# ==========================================
elif selected_page in ["📈 Portfolio", "📊 Stock AI Analyzer"]:
    st.markdown('<div class="hero-header">Investments & Stock AI Intelligence</div>', unsafe_allow_html=True)

    tab_port, tab_stock = st.tabs(["📈 Portfolio Holdings", "📊 Stock AI Analyzer"])

    with tab_port:
        db = SessionLocal()
        investments = db.query(Investment).filter(Investment.user_id == current_user_id).all()
        db.close()

        # Add investment expander
        with st.expander("➕ **Add Investment Asset to Portfolio**", expanded=False):
            with st.form("add_inv_form"):
                ia, ib, ic = st.columns(3)
                with ia:
                    i_sym = st.text_input("Symbol / Ticker", "TCS.NS").upper().strip()
                    i_name = st.text_input("Asset Name", "Tata Consultancy Services")
                with ib:
                    i_type = st.selectbox("Asset Class", ["Equity", "Mutual Fund", "Gold", "Fixed Deposit", "Crypto"])
                    i_qty = st.number_input("Quantity / Units", min_value=0.01, value=10.0, step=1.0)
                with ic:
                    i_buy = st.number_input("Buy Price (₹)", min_value=1.0, value=3500.0, step=100.0)
                    i_curr = st.number_input("Current Price (₹)", min_value=1.0, value=3912.0, step=100.0)

                if st.form_submit_button("Save Asset", type="primary"):
                    db = SessionLocal()
                    db.add(Investment(
                        user_id=current_user_id,
                        symbol=i_sym,
                        name=i_name,
                        asset_type=i_type,
                        quantity=i_qty,
                        buy_price=i_buy,
                        current_price=i_curr
                    ))
                    db.commit()
                    db.close()
                    st.success(f"Added {i_name} to portfolio!")
                    st.rerun()

        if investments:
            inv_records = []
            total_invested = 0.0
            total_current = 0.0
            for inv in investments:
                c_p = inv.current_price if inv.current_price > 0 else inv.buy_price
                invested_val = inv.quantity * inv.buy_price
                current_val = inv.quantity * c_p
                gain = current_val - invested_val
                gain_pct = (gain / invested_val * 100) if invested_val > 0 else 0
                total_invested += invested_val
                total_current += current_val

                inv_records.append({
                    "Symbol": inv.symbol,
                    "Name": inv.name,
                    "Class": inv.asset_type,
                    "Units": f"{inv.quantity:.2f}",
                    "Buy Price": f"₹{inv.buy_price:,.2f}",
                    "Current Price": f"₹{c_p:,.2f}",
                    "Invested": invested_val,
                    "Current Value": current_val,
                    "P&L": gain,
                    "Return": f"{gain_pct:+.1f}%"
                })

            tot_gain = total_current - total_invested
            tot_ret = (tot_gain / total_invested * 100) if total_invested > 0 else 0

            ip1, ip2, ip3, ip4 = st.columns(4)
            with ip1: st.metric("Total Invested", f"₹{total_invested:,.0f}")
            with ip2: st.metric("Portfolio Value", f"₹{total_current:,.0f}")
            with ip3: st.metric("Net Unrealized P&L", f"₹{tot_gain:+,.0f}", f"{tot_ret:+.1f}%")
            with ip4: st.metric("Holdings Count", f"{len(investments)}")

            inv_df = pd.DataFrame(inv_records)

            col_p1, col_p2 = st.columns([5, 5])
            with col_p1:
                fig_alloc = px.pie(
                    inv_df,
                    names="Class",
                    values="Current Value",
                    hole=0.5,
                    title="Asset Class Allocation",
                    color_discrete_sequence=px.colors.sequential.Tealgrn_r
                )
                fig_alloc.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_alloc, use_container_width=True)

            with col_p2:
                fig_hold = px.bar(
                    inv_df,
                    x="Symbol",
                    y="Current Value",
                    color="Class",
                    title="Holdings by Value",
                    text_auto=".2s"
                )
                fig_hold.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_hold, use_container_width=True)

            disp_inv = inv_df.copy()
            disp_inv["Invested"] = disp_inv["Invested"].apply(lambda x: f"₹{x:,.0f}")
            disp_inv["Current Value"] = disp_inv["Current Value"].apply(lambda x: f"₹{x:,.0f}")
            disp_inv["P&L"] = disp_inv["P&L"].apply(lambda x: f"₹{x:+,.0f}")
            st.dataframe(disp_inv, use_container_width=True)
        else:
            st.info("No investments recorded yet. Add an asset above or load demo data to view portfolio analytics.")

    with tab_stock:
        col_s1, col_s2 = st.columns([4, 6])
        with col_s1:
            ticker_input = st.selectbox("Select Benchmark Equities (NSE/BSE)", ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"])
        with col_s2:
            custom_t = st.text_input("Or Enter Any NSE/BSE Symbol", value="")
            if custom_t:
                ticker_input = custom_t.upper()

        stock_data = fetch_stock_data(ticker_input)
        info = stock_data["info"]
        hist = stock_data["history"]

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Current Price", f"₹{info.get('currentPrice', 0):,.2f}", f"{info.get('changePercent', 0):+.2f}%")
        with c2: st.metric("Market Cap", f"₹{info.get('marketCap', 0) / 1e11:.1f} Lakh Cr")
        with c3: st.metric("Trailing P/E", f"{info.get('trailingPE', 0):.1f}")
        with c4: st.metric("14-Day RSI", f"{info.get('rsi', 50):.1f}")

        if not hist.empty:
            fig_stock = go.Figure()
            fig_stock.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'))
            if "SMA_20" in hist.columns:
                fig_stock.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], line=dict(color='#00D2FF', width=1.5), name='SMA 20'))
            if "SMA_50" in hist.columns:
                fig_stock.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], line=dict(color='#F59E0B', width=1.5), name='SMA 50'))
            fig_stock.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, height=380)
            st.plotly_chart(fig_stock, use_container_width=True)

        st.subheader(f"🧠 Investment Outlook: {info.get('outlook')}")
        st.info(f"**Rationale:** {info.get('outlook_rationale')}")


# ==========================================
# 17. AI CENTER: ASK FINGUARD & PROACTIVE INSIGHTS
# ==========================================
elif selected_page in ["🤖 Ask FinGuard", "💡 AI Insights"]:
    st.markdown('<div class="hero-header">🤖 FinGuard AI Intelligence Center</div>', unsafe_allow_html=True)

    tab_chat, tab_insights = st.tabs(["🤖 Ask FinGuard Assistant", "💡 Proactive AI Insights"])

    with tab_chat:
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state["chat_history"]:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-msg-user"><strong>You:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg-bot"><strong>🛡️ FinGuard AI:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        qp1, qp2, qp3, qp4 = st.columns(4)
        q_selected = ""
        if qp1.button("Where am I spending most?"): q_selected = "Where am I spending the most money?"
        if qp2.button("Why is my risk score at this level?"): q_selected = "Why is my financial risk score at this level?"
        if qp3.button("Can I afford ₹80,000 laptop?"): q_selected = "Can I afford an ₹80,000 laptop?"
        if qp4.button("Analyse TCS.NS stock"): q_selected = "Analyse TCS.NS stock outlook"

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Type your question...", value=q_selected)
            send_btn = st.form_submit_button("Send Question", type="primary")

        if send_btn and user_input:
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            agent_role = route_agent(user_input)
            context = {
                "monthly_income": kpis.get("monthly_avg_income", 0),
                "monthly_expense": kpis.get("monthly_avg_expense", 0),
                "savings_rate": kpis.get("savings_rate", 0),
                "risk_score": risk_data.get("score", 0),
                "risk_status": risk_data.get("status", "No Data"),
                "top_category": "Discretionary Spending",
                "dti_ratio": risk_data.get("dti_ratio", 0),
                "monthly_sub": risk_data.get("monthly_recurring_sub", 0),
                "runway_months": risk_data.get("runway_months", 0)
            }
            bot_response = generate_agent_response(agent_role, user_input, context)
            st.session_state["chat_history"].append({"role": "assistant", "content": bot_response})
            st.rerun()

    with tab_insights:
        st.subheader("💡 Autonomous Proactive Intelligence Diagnostics")
        in_c1, in_c2 = st.columns(2)
        with in_c1:
            st.markdown(f"""
            <div class="xray-card xray-warning" style="margin-bottom: 12px;">
                <h4 style="margin:0; color:#FFFFFF;">🚀 Weekend Consumption Multiplier</h4>
                <p style="color:#CBD5E1; font-size:0.9rem; margin:6px 0;">
                    Discretionary transactions spike by an estimated <strong>34%</strong> on Saturdays & Sundays.
                </p>
                <div style="background: rgba(245, 158, 11, 0.1); padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; color: #FCD34D;">
                    <strong>Prescription:</strong> Restricting restaurant delivery to 1 order per weekend can salvage ~₹6,500 monthly.
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="xray-card xray-danger" style="margin-bottom: 12px;">
                <h4 style="margin:0; color:#FFFFFF;">⚡ Debt Avalanche Optimization</h4>
                <p style="color:#CBD5E1; font-size:0.9rem; margin:6px 0;">
                    Total outstanding liabilities stand at <strong>₹{risk_data.get('total_debt', 0):,.0f}</strong> with monthly EMI obligations of <strong>₹{risk_data.get('monthly_emi', 0):,.0f}</strong>.
                </p>
                <div style="background: rgba(239, 68, 68, 0.1); padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; color: #FCA5A5;">
                    <strong>Prescription:</strong> Pay down high APR revolving credit first to prevent compounded interest erosion.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with in_c2:
            st.markdown(f"""
            <div class="xray-card xray-success" style="margin-bottom: 12px;">
                <h4 style="margin:0; color:#FFFFFF;">🛡️ Emergency Buffer Trajectory</h4>
                <p style="color:#CBD5E1; font-size:0.9rem; margin:6px 0;">
                    Current living expense runway: <strong>{risk_data.get('runway_months', 0):.1f} Months</strong> (Target: 6.0 Months).
                </p>
                <div style="background: rgba(16, 185, 129, 0.1); padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; color: #6EE7B7;">
                    <strong>Prescription:</strong> Allocate 30% of monthly net surplus directly into high-liquidity sweep accounts.
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="xray-card xray-warning" style="margin-bottom: 12px;">
                <h4 style="margin:0; color:#FFFFFF;">🔄 Subscription Leakage Containment</h4>
                <p style="color:#CBD5E1; font-size:0.9rem; margin:6px 0;">
                    Active subscriptions generate <strong>₹{risk_data.get('monthly_recurring_sub', 0):,.0f}/mo</strong> in automatic deductions.
                </p>
                <div style="background: rgba(0, 210, 255, 0.1); padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; color: #38BDF8;">
                    <strong>Prescription:</strong> Convert monthly entertainment subscriptions to annual family plans for a ~20% discount.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# 18. GOALS, DEBT, BUDGETS & SUBSCRIPTIONS (CONTINUOUS CRUD)
# ==========================================
elif selected_page in ["💰 Budgets", "🔄 Subscriptions", "🎯 Goals", "💸 Debt"]:
    db = SessionLocal()
    goals = db.query(Goal).filter(Goal.user_id == current_user_id).all()
    debts = db.query(Debt).filter(Debt.user_id == current_user_id).all()
    subs = db.query(Subscription).filter(Subscription.user_id == current_user_id).all()
    budgets = db.query(Budget).filter(Budget.user_id == current_user_id).all()
    db.close()

    if selected_page == "💰 Budgets":
        st.markdown('<div class="hero-header">Monthly Category Budgets & Limit Guardrails</div>', unsafe_allow_html=True)

        with st.expander("➕ **Add or Update Category Budget**", expanded=not bool(budgets)):
            with st.form("add_budget_form"):
                ba, bb, bc = st.columns(3)
                with ba:
                    b_cat = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Rent", "Entertainment", "Healthcare", "Other"])
                with bb:
                    b_lim = st.number_input("Monthly Limit (₹)", min_value=500.0, value=15000.0, step=500.0)
                with bc:
                    b_thresh = st.number_input("Alert Threshold (%)", min_value=50.0, max_value=100.0, value=85.0, step=5.0)

                if st.form_submit_button("Set Budget Guardrail", type="primary"):
                    db = SessionLocal()
                    existing_b = db.query(Budget).filter(Budget.user_id == current_user_id, Budget.category == b_cat).first()
                    if existing_b:
                        existing_b.monthly_limit = b_lim
                        existing_b.alert_threshold_pct = b_thresh
                    else:
                        db.add(Budget(user_id=current_user_id, category=b_cat, monthly_limit=b_lim, alert_threshold_pct=b_thresh))
                    db.commit()
                    db.close()
                    st.success(f"Budget configured for {b_cat}!")
                    st.rerun()

        if budgets:
            # Calculate current month spend per category
            curr_period = df["month_year"].max() if not df.empty else None
            exp_curr = df[(df["type"] == "Expense") & (df["month_year"] == curr_period)] if curr_period is not None else pd.DataFrame()

            for b in budgets:
                spent = exp_curr[exp_curr["category"] == b.category]["amount"].sum() if not exp_curr.empty else 0.0
                pct = min(spent / b.monthly_limit, 1.0) if b.monthly_limit > 0 else 0
                st.markdown(f"#### {b.category}: Spent ₹{spent:,.0f} of ₹{b.monthly_limit:,.0f} ({spent/b.monthly_limit*100 if b.monthly_limit>0 else 0:.1f}%)")
                st.progress(pct)
                st.caption(f"Monthly ceiling: ₹{b.monthly_limit:,.0f} | Alert at {b.alert_threshold_pct:.0f}%")
        else:
            st.info("No budgets established yet. Use the form above to configure monthly guardrails.")

    elif selected_page == "🎯 Goals":
        st.markdown('<div class="hero-header">Financial Goal Milestones & Targets</div>', unsafe_allow_html=True)

        with st.expander("➕ **Create New Financial Goal**", expanded=not bool(goals)):
            with st.form("add_goal_form"):
                ga, gb, gc = st.columns(3)
                with ga:
                    g_title = st.text_input("Goal Title", "Emergency Reserve Fund")
                    g_cat = st.selectbox("Category", ["Savings", "Investment", "Retirement", "Major Purchase", "Travel"])
                with gb:
                    g_target = st.number_input("Target Amount (₹)", min_value=1000.0, value=250000.0, step=5000.0)
                    g_curr = st.number_input("Current Amount Saved (₹)", min_value=0.0, value=50000.0, step=2500.0)
                with gc:
                    g_days = st.number_input("Target Timeline (Days)", min_value=30, value=180, step=30)

                if st.form_submit_button("Save Goal", type="primary"):
                    db = SessionLocal()
                    db.add(Goal(
                        user_id=current_user_id,
                        title=g_title,
                        category=g_cat,
                        target_amount=g_target,
                        current_amount=g_curr,
                        target_date=datetime.now() + timedelta(days=int(g_days))
                    ))
                    db.commit()
                    db.close()
                    st.success("Goal created!")
                    st.rerun()

        if goals:
            for g in goals:
                pct = min((g.current_amount / g.target_amount), 1.0) if g.target_amount > 0 else 0
                st.markdown(f"#### 🎯 {g.title} ({g.category})")
                st.progress(pct)
                st.write(f"Current Saved: **₹{g.current_amount:,.0f}** | Target: **₹{g.target_amount:,.0f}** ({pct*100:.1f}%) | Target Date: {g.target_date.strftime('%d %b %Y')}")
        else:
            st.info("No active savings goals found. Use the form above to add your first milestone.")

    elif selected_page == "💸 Debt":
        st.markdown('<div class="hero-header">Debt & Liabilities Analysis</div>', unsafe_allow_html=True)

        with st.expander("➕ **Add Liability / Loan Account**", expanded=not bool(debts)):
            with st.form("add_debt_form"):
                da, db_col, dc = st.columns(3)
                with da:
                    d_title = st.text_input("Liability Name", "Auto Loan")
                    d_prin = st.number_input("Principal Amount (₹)", min_value=1000.0, value=650000.0, step=25000.0)
                with db_col:
                    d_bal = st.number_input("Outstanding Balance (₹)", min_value=0.0, value=420000.0, step=10000.0)
                    d_rate = st.number_input("Interest Rate APR (%)", min_value=0.0, value=8.9, step=0.5)
                with dc:
                    d_emi = st.number_input("Monthly EMI (₹)", min_value=100.0, value=14200.0, step=500.0)
                    d_rem = st.number_input("Remaining Months", min_value=1, value=36, step=1)

                if st.form_submit_button("Record Liability", type="primary"):
                    db = SessionLocal()
                    db.add(Debt(
                        user_id=current_user_id,
                        title=d_title,
                        principal=d_prin,
                        outstanding_balance=d_bal,
                        interest_rate_pct=d_rate,
                        monthly_emi=d_emi,
                        remaining_months=int(d_rem)
                    ))
                    db.commit()
                    db.close()
                    st.success("Liability recorded!")
                    st.rerun()

        if debts:
            total_debt = sum(d.outstanding_balance for d in debts)
            total_emi = sum(d.monthly_emi for d in debts)
            d1, d2 = st.columns(2)
            with d1: st.metric("Total Outstanding Balance", f"₹{total_debt:,.0f}")
            with d2: st.metric("Total Monthly EMI", f"₹{total_emi:,.0f}")
            debt_records = [{"Liability": d.title, "Principal": f"₹{d.principal:,.0f}", "Outstanding": f"₹{d.outstanding_balance:,.0f}", "Interest Rate": f"{d.interest_rate_pct:.1f}%", "Monthly EMI": f"₹{d.monthly_emi:,.0f}", "Months Left": d.remaining_months} for d in debts]
            st.dataframe(pd.DataFrame(debt_records), use_container_width=True)
        else:
            st.info("No debt or loan records registered in your account.")

    elif selected_page == "🔄 Subscriptions":
        st.markdown('<div class="hero-header">Recurring Subscriptions & Leakage Monitor</div>', unsafe_allow_html=True)

        with st.expander("➕ **Add Recurring Subscription**", expanded=not bool(subs)):
            with st.form("add_sub_form"):
                sa, sb_col, sc = st.columns(3)
                with sa:
                    s_name = st.text_input("Subscription Name", "Netflix Premium")
                    s_cat = st.selectbox("Category", ["Entertainment", "Productivity", "Utilities", "Health", "Other"])
                with sb_col:
                    s_amt = st.number_input("Cost (₹)", min_value=10.0, value=649.0, step=50.0)
                    s_cycle = st.selectbox("Billing Cycle", ["Monthly", "Annual"])
                with sc:
                    s_active = st.checkbox("Active Service", value=True)

                if st.form_submit_button("Record Subscription", type="primary"):
                    db = SessionLocal()
                    db.add(Subscription(
                        user_id=current_user_id,
                        name=s_name,
                        amount=s_amt,
                        billing_cycle=s_cycle,
                        category=s_cat,
                        is_active=s_active
                    ))
                    db.commit()
                    db.close()
                    st.success("Subscription added!")
                    st.rerun()

        if subs:
            mo_sub = sum(s.amount if s.billing_cycle == "Monthly" else s.amount / 12.0 for s in subs)
            yr_sub = mo_sub * 12.0
            s1, s2 = st.columns(2)
            with s1: st.metric("Monthly Subscriptions Outflow", f"₹{mo_sub:,.0f}/mo")
            with s2: st.metric("Annualized Cost", f"₹{yr_sub:,.0f}/yr")
            sub_data = [{"Name": s.name, "Cost": f"₹{s.amount:,.0f}", "Cycle": s.billing_cycle, "Category": s.category, "Status": "Active" if s.is_active else "Paused"} for s in subs]
            st.dataframe(pd.DataFrame(sub_data), use_container_width=True)
        else:
            st.info("No active subscriptions registered.")


# ==========================================
# 19. REPORTS & 20. PROFILE / SECURITY
# ==========================================
elif selected_page == "📄 Financial Report":
    st.markdown('<div class="hero-header">📄 Automated Executive PDF Report Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Generate a publication-grade personal financial audit report via ReportLab.</div>', unsafe_allow_html=True)

    xray_findings = generate_financial_xray(df, risk_data, user_id=current_user_id)
    if st.button("🚀 Generate PDF Executive Report", type="primary"):
        pdf_bytes = generate_executive_pdf(kpis, risk_data, xray_findings)
        st.success("Report generated successfully!")
        st.download_button(
            label="📥 Download PDF Financial Report",
            data=pdf_bytes,
            file_name=f"FinGuard_{current_user_name.replace(' ', '_')}_Report.pdf",
            mime="application/pdf"
        )

elif selected_page in ["👤 Profile", "⚙️ Security & Data"]:
    st.markdown('<div class="hero-header">User Profile & Account Security</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">User Account Details</div>
            <p style="margin: 6px 0; font-size: 1.1rem; color: #FFFFFF;"><strong>Name:</strong> {current_user_name}</p>
            <p style="margin: 6px 0; font-size: 1.1rem; color: #FFFFFF;"><strong>Email:</strong> {current_user_email}</p>
            <p style="margin: 6px 0; font-size: 0.95rem; color: #94A3B8;"><strong>Account ID:</strong> #{current_user_id}</p>
            <p style="margin: 6px 0; font-size: 0.95rem; color: #10B981;"><strong>Security Status:</strong> Password Hash Verified (SHA-256)</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Telemetry Storage & Isolation</div>
            <p style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.5;">
                FinGuard AI guarantees complete tenant isolation. Your transactions, budgets, goals, and risk profiles are strictly filtered by your unique account ID.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Data Management Controls")
    cd1, cd2 = st.columns(2)
    with cd1:
        if st.button("⚡ Populate Account with Demo Data", help="Fills your personal account with 12 months of testing data"):
            seed_demo_data(user_id=current_user_id, force=True)
            st.success("Demo data loaded into your account!")
            st.rerun()
    with cd2:
        if st.button("⚠️ Erase All My Personal Data", help="Permanently deletes all transactions from your account"):
            clear_user_data(current_user_id)
            st.info("Your account data has been wiped.")
            st.rerun()
