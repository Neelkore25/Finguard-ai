"""FinGuard AI - Realistic Financial Demo Dataset Generator (Scoped to User ID)"""

import random
from datetime import datetime, timedelta
from core.database import SessionLocal, init_db, User, Transaction, Budget, Goal, Debt, Investment, Subscription, Reminder, hash_password


def clear_user_data(user_id: int):
    """Deletes all financial telemetry for a specific user ID."""
    db = SessionLocal()
    try:
        db.query(Transaction).filter(Transaction.user_id == user_id).delete()
        db.query(Budget).filter(Budget.user_id == user_id).delete()
        db.query(Goal).filter(Goal.user_id == user_id).delete()
        db.query(Debt).filter(Debt.user_id == user_id).delete()
        db.query(Investment).filter(Investment.user_id == user_id).delete()
        db.query(Subscription).filter(Subscription.user_id == user_id).delete()
        db.query(Reminder).filter(Reminder.user_id == user_id).delete()
        db.commit()
    finally:
        db.close()


def seed_demo_data(user_id: int = 1, force: bool = False):
    """Generates and inserts realistic 12-month demo financial data for a specific user."""
    init_db()
    db = SessionLocal()

    try:
        # Ensure user exists before inserting foreign key relations
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                name="Demo User",
                email=f"demo_{user_id}@finguard.ai",
                password_hash=hash_password("DemoPass123")
            )
            db.add(user)
            db.commit()

        existing_tx_count = db.query(Transaction).filter(Transaction.user_id == user_id).count()
        if existing_tx_count > 0 and not force:
            return  # Already seeded for this user

        if force:
            clear_user_data(user_id)

        today = datetime.now()
        transactions = []

        # 1. Base Incomes (Monthly salary on 1st + quarterly freelance bonuses)
        for i in range(12, -1, -1):
            month_date = today - timedelta(days=i * 30)
            salary_dt = datetime(month_date.year, month_date.month, 1, 10, 0)
            transactions.append(Transaction(
                user_id=user_id,
                date=salary_dt,
                type="Income",
                category="Salary",
                amount=125000.0,
                description="Monthly Salary - Tech Corp Ltd",
                account="HDFC Salary A/c",
                is_recurring=True,
                is_anomaly=False
            ))

            if i in [2, 5, 8, 11]:
                bonus_dt = datetime(month_date.year, month_date.month, 15, 14, 30)
                transactions.append(Transaction(
                    user_id=user_id,
                    date=bonus_dt,
                    type="Income",
                    category="Freelance",
                    amount=35000.0,
                    description="AI Consulting Project Stipend",
                    account="HDFC Salary A/c",
                    is_recurring=False,
                    is_anomaly=False
                ))

            # 2. Fixed Monthly Expenses
            rent_dt = datetime(month_date.year, month_date.month, 3, 11, 0)
            transactions.append(Transaction(
                user_id=user_id,
                date=rent_dt,
                type="Expense",
                category="Rent",
                amount=30000.0,
                description="Apartment Rent Transfer",
                account="HDFC Salary A/c",
                is_recurring=True,
                is_anomaly=False
            ))

            emi_dt = datetime(month_date.year, month_date.month, 5, 9, 30)
            transactions.append(Transaction(
                user_id=user_id,
                date=emi_dt,
                type="Expense",
                category="Debt",
                amount=14200.0,
                description="Auto-Debit Car Loan EMI - HDFC Bank",
                account="HDFC Salary A/c",
                is_recurring=True,
                is_anomaly=False
            ))

            sip_dt = datetime(month_date.year, month_date.month, 7, 10, 0)
            transactions.append(Transaction(
                user_id=user_id,
                date=sip_dt,
                type="Expense",
                category="Investments",
                amount=25000.0,
                description="Parag Parikh Flexi Cap SIP",
                account="HDFC Salary A/c",
                is_recurring=True,
                is_anomaly=False
            ))

            # Subscriptions
            sub_dt = datetime(month_date.year, month_date.month, 10, 16, 0)
            transactions.append(Transaction(
                user_id=user_id,
                date=sub_dt,
                type="Expense",
                category="Entertainment",
                amount=649.0,
                description="Netflix 4K Premium Plan",
                account="Credit Card",
                is_recurring=True,
                is_anomaly=False
            ))
            transactions.append(Transaction(
                user_id=user_id,
                date=sub_dt + timedelta(days=1),
                type="Expense",
                category="Entertainment",
                amount=119.0,
                description="Spotify Premium Individual",
                account="Credit Card",
                is_recurring=True,
                is_anomaly=False
            ))
            transactions.append(Transaction(
                user_id=user_id,
                date=sub_dt + timedelta(days=2),
                type="Expense",
                category="Education",
                amount=1999.0,
                description="ChatGPT Plus / Cloud Tools",
                account="Credit Card",
                is_recurring=True,
                is_anomaly=False
            ))
            transactions.append(Transaction(
                user_id=user_id,
                date=sub_dt + timedelta(days=3),
                type="Expense",
                category="Healthcare",
                amount=2500.0,
                description="Cult.fit Gym Monthly Membership",
                account="Credit Card",
                is_recurring=True,
                is_anomaly=False
            ))

            # Utilities
            util_dt = datetime(month_date.year, month_date.month, 18, 12, 0)
            transactions.append(Transaction(
                user_id=user_id,
                date=util_dt,
                type="Expense",
                category="Bills",
                amount=2250.0 + random.randint(-200, 450),
                description="Electricity Board Bill Payment",
                account="HDFC Salary A/c",
                is_recurring=True,
                is_anomaly=False
            ))
            transactions.append(Transaction(
                user_id=user_id,
                date=util_dt + timedelta(days=1),
                type="Expense",
                category="Bills",
                amount=999.0,
                description="Jio Fiber Broadband 150 Mbps",
                account="HDFC Salary A/c",
                is_recurring=True,
                is_anomaly=False
            ))

            # 3. Discretionary Daily Expenses
            for d in [4, 8, 12, 16, 20, 24, 27]:
                tx_date = datetime(month_date.year, month_date.month, min(d, 28), random.randint(12, 21), random.randint(10, 50))
                food_vendors = ["Swiggy Gourmet Order", "Zomato Dinner", "Blinkit Instant Groceries", "Nature Basket Organic", "Barbeque Nation Dining", "Blue Tokai Coffee"]
                transactions.append(Transaction(
                    user_id=user_id,
                    date=tx_date,
                    type="Expense",
                    category="Food",
                    amount=float(random.randint(350, 2200)),
                    description=random.choice(food_vendors),
                    account="Credit Card",
                    is_recurring=False,
                    is_anomaly=False
                ))

            for d in [6, 14, 22, 28]:
                tx_date = datetime(month_date.year, month_date.month, min(d, 28), random.randint(8, 19), 0)
                trans_vendors = ["Uber Premier Commute", "Shell Petrol Pump Fuel", "Fastag Toll Recharge", "Metro Card Topup"]
                transactions.append(Transaction(
                    user_id=user_id,
                    date=tx_date,
                    type="Expense",
                    category="Transport",
                    amount=float(random.randint(450, 2800)),
                    description=random.choice(trans_vendors),
                    account="Credit Card",
                    is_recurring=False,
                    is_anomaly=False
                ))

            if i % 2 == 0:
                tx_date = datetime(month_date.year, month_date.month, 19, 17, 30)
                transactions.append(Transaction(
                    user_id=user_id,
                    date=tx_date,
                    type="Expense",
                    category="Shopping",
                    amount=float(random.randint(1800, 6500)),
                    description="Amazon India Online Shopping",
                    account="Credit Card",
                    is_recurring=False,
                    is_anomaly=False
                ))

        # 4. Realistic Anomalies
        anom1_dt = today - timedelta(days=75)
        transactions.append(Transaction(
            user_id=user_id,
            date=anom1_dt,
            type="Expense",
            category="Shopping",
            amount=149900.0,
            description="Apple Store - MacBook Pro 16 inch M3",
            account="Credit Card",
            is_recurring=False,
            is_anomaly=True,
            anomaly_reason="Single transaction 12.4x standard deviation above category average."
        ))

        anom2_dt = today - timedelta(days=140)
        transactions.append(Transaction(
            user_id=user_id,
            date=anom2_dt,
            type="Expense",
            category="Food",
            amount=28400.0,
            description="Taj Palace - Anniversary Banquet Dinner",
            account="Credit Card",
            is_recurring=False,
            is_anomaly=True,
            anomaly_reason="Spike 15x normal restaurant transaction amount."
        ))

        anom3_dt = today - timedelta(days=25)
        transactions.append(Transaction(
            user_id=user_id,
            date=anom3_dt,
            type="Expense",
            category="Education",
            amount=18500.0,
            description="AWS Cloud Enterprise Cluster - Unusual Overuse Billing",
            account="Credit Card",
            is_recurring=False,
            is_anomaly=True,
            anomaly_reason="Unexpected 900% jump in monthly cloud infrastructure cost."
        ))

        db.bulk_save_objects(transactions)

        # Seed Budgets
        budgets = [
            Budget(user_id=user_id, category="Food", monthly_limit=22000.0, alert_threshold_pct=80.0),
            Budget(user_id=user_id, category="Rent", monthly_limit=32000.0, alert_threshold_pct=95.0),
            Budget(user_id=user_id, category="Transport", monthly_limit=8000.0, alert_threshold_pct=85.0),
            Budget(user_id=user_id, category="Entertainment", monthly_limit=6000.0, alert_threshold_pct=85.0),
            Budget(user_id=user_id, category="Shopping", monthly_limit=12000.0, alert_threshold_pct=80.0),
            Budget(user_id=user_id, category="Bills", monthly_limit=6000.0, alert_threshold_pct=90.0),
            Budget(user_id=user_id, category="Investments", monthly_limit=30000.0, alert_threshold_pct=90.0),
        ]
        db.bulk_save_objects(budgets)

        # Seed Goals
        goals = [
            Goal(user_id=user_id, title="🛡️ Emergency Reserve (6 Mo)", target_amount=350000.0, current_amount=280000.0, target_date=today + timedelta(days=90), category="Emergency"),
            Goal(user_id=user_id, title="✈️ Tokyo & Kyoto Trip", target_amount=180000.0, current_amount=95000.0, target_date=today + timedelta(days=180), category="Vacation"),
            Goal(user_id=user_id, title="⚡ Tata Harrier EV Down Payment", target_amount=500000.0, current_amount=175000.0, target_date=today + timedelta(days=365), category="Asset"),
            Goal(user_id=user_id, title="💻 M-Series Studio Workstation", target_amount=120000.0, current_amount=110000.0, target_date=today + timedelta(days=30), category="Tech"),
        ]
        db.bulk_save_objects(goals)

        # Seed Debts
        debts = [
            Debt(user_id=user_id, title="HDFC Auto Loan", principal=600000.0, outstanding_balance=245000.0, interest_rate_pct=8.6, monthly_emi=14200.0, remaining_months=19),
            Debt(user_id=user_id, title="HDFC Regalia Credit Card", principal=45000.0, outstanding_balance=38500.0, interest_rate_pct=38.4, monthly_emi=4200.0, remaining_months=10),
        ]
        db.bulk_save_objects(debts)

        # Seed Investments
        investments = [
            Investment(user_id=user_id, symbol="TCS.NS", name="Tata Consultancy Services", asset_type="Large Cap Tech", quantity=25, buy_price=3480.0, current_price=3890.0),
            Investment(user_id=user_id, symbol="RELIANCE.NS", name="Reliance Industries Ltd", asset_type="Energy & Conglomerate", quantity=35, buy_price=2680.0, current_price=2940.0),
            Investment(user_id=user_id, symbol="INFY.NS", name="Infosys Limited", asset_type="IT Services", quantity=50, buy_price=1460.0, current_price=1750.0),
            Investment(user_id=user_id, symbol="HDFCBANK.NS", name="HDFC Bank Limited", asset_type="Private Banking", quantity=45, buy_price=1520.0, current_price=1640.0),
            Investment(user_id=user_id, symbol="PPFAS.MF", name="Parag Parikh Flexi Cap Fund", asset_type="Mutual Fund", quantity=1450, buy_price=54.2, current_price=68.5),
        ]
        db.bulk_save_objects(investments)

        # Seed Subscriptions
        subscriptions = [
            Subscription(user_id=user_id, name="Netflix 4K Ultra", amount=649.0, billing_cycle="Monthly", category="Entertainment", next_billing_date=today + timedelta(days=8)),
            Subscription(user_id=user_id, name="Spotify Premium Family", amount=179.0, billing_cycle="Monthly", category="Entertainment", next_billing_date=today + timedelta(days=12)),
            Subscription(user_id=user_id, name="Amazon Prime Annual", amount=1499.0, billing_cycle="Annual", category="Shopping", next_billing_date=today + timedelta(days=110)),
            Subscription(user_id=user_id, name="Cult.fit Fitness Pass", amount=2500.0, billing_cycle="Monthly", category="Healthcare", next_billing_date=today + timedelta(days=15)),
            Subscription(user_id=user_id, name="ChatGPT Plus Subscription", amount=1999.0, billing_cycle="Monthly", category="Education", next_billing_date=today + timedelta(days=5)),
            Subscription(user_id=user_id, name="Jio Fiber Broadband", amount=999.0, billing_cycle="Monthly", category="Bills", next_billing_date=today + timedelta(days=18)),
        ]
        db.bulk_save_objects(subscriptions)

        # Seed Reminders
        reminders = [
            Reminder(user_id=user_id, title="Pay Apartment Rent to Landlord", due_date=today + timedelta(days=2), amount=30000.0, category="Rent", frequency="Monthly"),
            Reminder(user_id=user_id, title="Car Loan EMI Auto-Debit", due_date=today + timedelta(days=5), amount=14200.0, category="EMI", frequency="Monthly"),
            Reminder(user_id=user_id, title="HDFC Credit Card Bill Due", due_date=today + timedelta(days=11), amount=38500.0, category="Credit Card", frequency="Monthly"),
            Reminder(user_id=user_id, title="Electricity Board BESCOM Bill", due_date=today + timedelta(days=14), amount=2450.0, category="Utility", frequency="Monthly"),
            Reminder(user_id=user_id, title="Quarterly Portfolio Rebalance Review", due_date=today + timedelta(days=22), amount=0.0, category="Investment", frequency="Quarterly"),
        ]
        db.bulk_save_objects(reminders)

        db.commit()
    finally:
        db.close()
