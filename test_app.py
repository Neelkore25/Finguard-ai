"""Verification script to test all core engines without UI."""
import sys
import os

print("Testing imports...")
from core.database import init_db, SessionLocal, Transaction
from core.demo_data import seed_demo_data
from core.analytics import load_transactions_df, calculate_financial_kpis, detect_anomalies
from core.risk_engine import compute_financial_risk_score, generate_financial_xray, generate_risk_dna_profile
from core.stock_engine import fetch_stock_data
from core.ai_engine import route_agent, generate_agent_response
from core.pdf_generator import generate_executive_pdf

print("1. Initializing DB and Demo Data...")
init_db()
seed_demo_data(force=True)
db = SessionLocal()
tx_count = db.query(Transaction).count()
db.close()
print(f"   -> DB Seeded successfully! Transactions: {tx_count}")

print("2. Testing Analytics KPIs...")
df = load_transactions_df()
kpis = calculate_financial_kpis(df)
print(f"   -> Monthly Avg Income: INR {kpis['monthly_avg_income']:,.2f}")
print(f"   -> Monthly Avg Expense: INR {kpis['monthly_avg_expense']:,.2f}")
print(f"   -> Savings Rate: {kpis['savings_rate']:.1f}%")

print("3. Testing Risk Engine...")
risk_data = compute_financial_risk_score(kpis, df)
print(f"   -> Risk Score: {risk_data['score']}/100 ({risk_data['status']})")
print(f"   -> DTI Ratio: {risk_data['dti_ratio']}% | Runway: {risk_data['runway_months']} Months")

print("4. Testing Financial X-Ray...")
xray = generate_financial_xray(df, risk_data)
print(f"   -> Identified {len(xray)} X-Ray structural risks")

print("5. Testing Stock Engine...")
stock = fetch_stock_data("TCS.NS")
print(f"   -> Stock: {stock['info']['symbol']} | Price: INR {stock['info']['currentPrice']} | Outlook: {stock['info']['outlook']}")

print("6. Testing AI Agent Routing & Grounded Response...")
agent = route_agent("Why did food expenses spike?")
resp = generate_agent_response(agent, "Why did food expenses spike?", {
    "monthly_income": kpis["monthly_avg_income"],
    "monthly_expense": kpis["monthly_avg_expense"],
    "savings_rate": kpis["savings_rate"],
    "risk_score": risk_data["score"],
    "risk_status": risk_data["status"],
    "top_category": "Food",
    "dti_ratio": risk_data["dti_ratio"],
    "monthly_sub": risk_data["monthly_recurring_sub"],
    "runway_months": risk_data["runway_months"]
})
print(f"   -> Agent '{agent}' responded ({len(resp)} chars)")

print("7. Testing PDF Report Generation...")
pdf_bytes = generate_executive_pdf(kpis, risk_data, xray)
print(f"   -> PDF generated successfully ({len(pdf_bytes)} bytes)")

print("\nALL 7 TESTS PASSED! FinGuard AI IS READY FOR DEMO!")
