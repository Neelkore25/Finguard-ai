"""Verification script for Multi-Tenant Auth, Zero-Data Fresh State, and Isolation."""

from core.database import init_db, SessionLocal, User, Transaction, hash_password, verify_password
from core.demo_data import seed_demo_data, clear_user_data
from core.analytics import load_transactions_df, calculate_financial_kpis
from core.risk_engine import compute_financial_risk_score, generate_financial_xray

print("Initializing DB...")
init_db()

db = SessionLocal()
# Clean any previous test users and their data completely
prev_users = db.query(User).filter(User.email.in_(["userA@test.com", "userB@test.com"])).all()
for u in prev_users:
    clear_user_data(u.id)
    db.delete(u)
db.commit()

# Test 1: User A Registration
print("\n1. Testing User A Signup (Fresh Account)...")
user_a = User(
    name="Alice Smith",
    email="userA@test.com",
    password_hash=hash_password("AliceSecurePass1")
)
db.add(user_a)
db.commit()
db.refresh(user_a)
print(f"   -> User A registered with ID #{user_a.id}")
assert verify_password("AliceSecurePass1", user_a.password_hash)
assert not verify_password("WrongPass", user_a.password_hash)
print("   -> Password hashing verified!")

# Test 2: Verify User A starts with ZERO data
df_a = load_transactions_df(user_id=user_a.id)
assert len(df_a) == 0, f"Expected 0 transactions for new user, found {len(df_a)}"
kpis_a = calculate_financial_kpis(df_a)
assert kpis_a["total_income"] == 0.0
assert kpis_a["total_expense"] == 0.0
risk_a = compute_financial_risk_score(kpis_a, df_a, user_id=user_a.id)
assert risk_a["status"] == "No Telemetry"
assert risk_a["score"] == 0
print("   -> User A confirmed with ZERO transactions, ZERO income, ZERO expenses, and No Telemetry risk state!")

# Test 3: User A adds a transaction
print("\n2. Testing User A adds a transaction...")
tx_a = Transaction(
    user_id=user_a.id,
    type="Income",
    category="Salary",
    amount=50000.0,
    description="Initial Tech Salary",
    account="Primary Checking"
)
db.add(tx_a)
db.commit()

df_a_updated = load_transactions_df(user_id=user_a.id)
assert len(df_a_updated) == 1
kpis_a_updated = calculate_financial_kpis(df_a_updated)
assert kpis_a_updated["total_income"] == 50000.0
print(f"   -> User A income updated dynamically to INR {kpis_a_updated['total_income']:,.2f}")

# Test 4: User B Signup & Isolation Verification
print("\n3. Testing User B Signup & Isolation from User A...")
user_b = User(
    name="Bob Jones",
    email="userB@test.com",
    password_hash=hash_password("BobSecurePass2")
)
db.add(user_b)
db.commit()
db.refresh(user_b)
print(f"   -> User B registered with ID #{user_b.id}")

df_b = load_transactions_df(user_id=user_b.id)
assert len(df_b) == 0, f"Tenant leakage! User B saw {len(df_b)} transactions"
kpis_b = calculate_financial_kpis(df_b)
assert kpis_b["total_income"] == 0.0
print("   -> Complete Tenant Isolation confirmed! User B sees ZERO transactions and ZERO of User A's data.")

# Test 5: User B loads demo data
print("\n4. Testing User B loading demo data...")
seed_demo_data(user_id=user_b.id, force=True)
df_b_demo = load_transactions_df(user_id=user_b.id)
assert len(df_b_demo) > 50, f"Expected rich demo data for User B, found {len(df_b_demo)}"

# Verify User A is untouched
df_a_check = load_transactions_df(user_id=user_a.id)
assert len(df_a_check) == 1, f"User A data corrupted by User B demo seed! Count: {len(df_a_check)}"
print(f"   -> User B has {len(df_b_demo)} demo transactions while User A strictly retains only {len(df_a_check)} transaction!")

# Test 6: Clear User B data
print("\n5. Testing Clear Data for User B...")
clear_user_data(user_id=user_b.id)
df_b_cleared = load_transactions_df(user_id=user_b.id)
assert len(df_b_cleared) == 0
df_a_final = load_transactions_df(user_id=user_a.id)
assert len(df_a_final) == 1
print("   -> User B data cleared back to 0. User A remains intact!")

db.close()
print("\n=======================================================")
print("ALL MULTI-TENANT & ZERO-DATA VERIFICATIONS PASSED 100%!")
print("=======================================================")
