from flask import Flask, render_template, request, redirect, make_response
from bank_system import setup_tables, add_customer, get_customers, add_account, get_accounts, update_balance, generate_report
from auth import initialize_firebase_app, login_required, create_session_cookie, verify_session_cookie
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
initialize_firebase_app()
setup_tables()

# ----- Demo Data Seeding -----
def seed_demo_data() -> None:
    # Only seed if there are no customers yet
    if get_customers():
        return
    demo_customers = [
        ("Alice Johnson", "alice@example.com"),
        ("Bob Smith", "bob@example.com"),
        ("Carol Davis", "carol@example.com"),
        ("David Wilson", "david@example.com"),
        ("Eva Brown", "eva@example.com"),
        ("Frank Miller", "frank@example.com"),
        ("Grace Lee", "grace@example.com"),
        ("Henry Clark", "henry@example.com"),
        ("Ivy Lewis", "ivy@example.com"),
        ("Jack Walker", "jack@example.com"),
    ]
    for name, email in demo_customers:
        add_customer(name, email)
    # Create simple accounts for first few customers
    accounts = [
        (1, "Checking", 1200.00),
        (1, "Savings", 5400.50),
        (2, "Checking", 300.00),
        (3, "Savings", 9000.00),
        (4, "Checking", -25.00),
        (5, "Savings", 150.00),
        (6, "Checking", 750.75),
        (7, "Savings", 50.00),
        (8, "Checking", 0.00),
        (9, "Savings", 1234.56),
    ]
    for customer_id, account_type, balance in accounts:
        add_account(customer_id, account_type, balance)

# Enable demo mode by default
if True:  # os.getenv("DEMO_MODE", "false").lower() == "true":
    seed_demo_data()

# ----- Home Page -----
@app.route("/")
def home():
    customers = get_customers()
    accounts = get_accounts()
    report = generate_report()
    repo_url = os.getenv("GITHUB_REPO_URL", "")
    cookie_name = os.getenv("SESSION_COOKIE_NAME", "session")
    cookie = request.cookies.get(cookie_name)
    is_authenticated = False
    # In demo mode, treat user as authenticated for UI enabling
    if True:  # os.getenv("DEMO_MODE", "false").lower() == "true":
        is_authenticated = True
    if cookie:
        try:
            verify_session_cookie(cookie)
            is_authenticated = True
        except Exception:
            is_authenticated = False
    return render_template("index.html", customers=customers, accounts=accounts, report=report, is_authenticated=is_authenticated, repo_url=repo_url)

# ----- Login (Firebase Session) -----
@app.route("/login")
def login_page():
    repo_url = os.getenv("GITHUB_REPO_URL", "")
    return render_template("login.html", repo_url=repo_url)


@app.route("/sessionLogin", methods=["POST"])
def session_login():
    id_token = request.form.get("idToken")
    if not id_token:
        return redirect("/login")
    cookie = create_session_cookie(id_token)
    cookie_name = os.getenv("SESSION_COOKIE_NAME", "session")
    resp = make_response(redirect("/"))
    resp.set_cookie(cookie_name, cookie, max_age=60*60*24*5, httponly=True, secure=False)
    return resp


@app.route("/logout", methods=["POST"])
def logout():
    cookie_name = os.getenv("SESSION_COOKIE_NAME", "session")
    resp = make_response(redirect("/login"))
    resp.delete_cookie(cookie_name)
    return resp

# ----- Add Customer -----
@app.route("/add_customer", methods=["POST"])
@login_required
def add_customer_route():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    name = f"{first_name} {last_name}"
    email = request.form["email"]
    add_customer(name, email)
    return redirect("/")

# ----- Add Account -----
@app.route("/add_account", methods=["POST"])
@login_required
def add_account_route():
    customer_id = int(request.form["customer_id"])
    account_type = request.form["account_type"]
    balance = float(request.form["balance"])
    add_account(customer_id, account_type, balance)
    return redirect("/")

# ----- Update Balance -----
@app.route("/update_balance", methods=["POST"])
@login_required
def update_balance_route():
    account_id = int(request.form["account_id"])
    amount = float(request.form["amount"])
    update_balance(account_id, amount)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
