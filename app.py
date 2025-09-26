from flask import Flask, render_template, request, redirect, make_response
from bank_system import setup_tables, add_customer, get_customers, add_account, get_accounts, update_balance, generate_report
from auth import initialize_firebase_app, login_required, create_session_cookie, verify_session_cookie
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
initialize_firebase_app()
setup_tables()

# ----- Home Page -----
@app.route("/")
def home():
    customers = get_customers()
    report = generate_report()
    cookie_name = os.getenv("SESSION_COOKIE_NAME", "session")
    cookie = request.cookies.get(cookie_name)
    is_authenticated = False
    if cookie:
        try:
            verify_session_cookie(cookie)
            is_authenticated = True
        except Exception:
            is_authenticated = False
    return render_template("index.html", customers=customers, report=report, is_authenticated=is_authenticated)

# ----- Login (Firebase Session) -----
@app.route("/login")
def login_page():
    return render_template("login.html")


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
    name = request.form["name"]
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
