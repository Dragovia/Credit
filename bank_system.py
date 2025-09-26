import sqlite3

# =========================
# Database Connection
# =========================
conn = sqlite3.connect("bank_system.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# Setup Tables
# =========================
def setup_tables():
    """Create customers, accounts, and transactions tables"""
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS accounts")
    cursor.execute("DROP TABLE IF EXISTS customers")

    # Customers table
    cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)

    # Accounts table
    cursor.execute("""
    CREATE TABLE accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        account_type TEXT NOT NULL,
        balance REAL DEFAULT 0,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    """)

    # Transactions table for audit
    cursor.execute("""
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        amount REAL,
        type TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    """)
    conn.commit()


# =========================
# Customer Functions
# =========================
def add_customer(name, email):
    cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))
    conn.commit()


def get_customers():
    cursor.execute("SELECT * FROM customers")
    return cursor.fetchall()


# =========================
# Account Functions
# =========================
def add_account(customer_id, account_type, balance=0.0):
    cursor.execute(
        "INSERT INTO accounts (customer_id, account_type, balance) VALUES (?, ?, ?)",
        (customer_id, account_type, balance)
    )
    conn.commit()


def get_accounts(customer_id=None):
    if customer_id:
        cursor.execute("SELECT * FROM accounts WHERE customer_id=?", (customer_id,))
    else:
        cursor.execute("SELECT * FROM accounts")
    return cursor.fetchall()


def update_balance(account_id, amount):
    """Deposit (+) or Withdraw (-) and log the transaction"""
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", (amount, account_id))
    tran_type = "Deposit" if amount > 0 else "Withdrawal"
    cursor.execute("INSERT INTO transactions (account_id, amount, type) VALUES (?, ?, ?)",
                   (account_id, amount, tran_type))
    conn.commit()


# =========================
# Reporting & Compliance
# =========================
def generate_report():
    """Report totals, averages, and negative balances"""
    cursor.execute("SELECT SUM(balance) FROM accounts")
    total_balance = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(balance) FROM accounts")
    avg_balance = cursor.fetchone()[0]

    cursor.execute("SELECT customers.name, accounts.account_type, accounts.balance FROM accounts "
                   "JOIN customers ON accounts.customer_id = customers.id WHERE balance < 0")
    negative_balances = cursor.fetchall()

    return {
        "total_balance": total_balance,
        "avg_balance": avg_balance,
        "negative_balances": negative_balances
    }
