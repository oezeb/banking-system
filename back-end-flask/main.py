from flask import Flask
from flask import request, make_response
from flask_cors import CORS

import auth
import db

auth.init()
app = Flask(__name__)
app.secret_key = 'banana'
CORS(app)

# ======================================================================================================================
#  LOGIN ROUTE
# ======================================================================================================================

@app.route("/login", methods=(["POST"]))
def login():
    # get username, password from request
    headers = request.headers
    if request.authorization and 'username' in request.authorization: # username, password based auth
        if 'password' not in request.authorization:
            return make_response('Password required', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
        username = request.authorization.username
        password = request.authorization.password
    elif 'Authorization' in headers: # token based auth
        res = auth.auth(headers)
        if 'error' in res:
            return make_response(res['error'], 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
        username = res['username']
        password = res['password']
    else:
        return make_response('Failed to authenticate', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
    
    # login user
    con = db.login(username, password)
    if con: # successful login
        token = auth.add(username, password)
        return make_response(token, 200)
    else: # unsuccessful login
        return make_response('Failed to authenticate', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

# ======================================================================================================================
#  CUSTOMER ROUTES
# ======================================================================================================================

@app.route("/customer/add", methods=["POST"])
def customer_add():
    return run(request, db.add_customer, ['customer', 'contact', 'che_acc_id'], True)

@app.route("/customer/delete", methods=["POST"])
def customer_delete():
    return run(request, db.delete_customer, ['cus_id'], True)

@app.route("/customer/edit", methods=["POST"])
def customer_edit():
    return run(request, db.edit_customer, ['customer', 'contact'], True)

@app.route("/customer/all", methods=["POST"])
def customer_all():
    return run(request, db.get_customers)

@app.route("/customer/filter", methods=["POST"])
def customer_info():
    return run(request, db.get_customer_info, ['cus_id', 'cus_name'])

# ======================================================================================================================
#  ACCOUNT ROUTES
# ======================================================================================================================

@app.route("/account/add", methods=["POST"])
def account_add():
    return run(request, db.add_account, ['account', 'cus_id'], True)

@app.route("/account/delete", methods=["POST"])
def account_delete():
    return run(request, db.delete_account, ['acc_id'], True)

@app.route("/account/edit", methods=["POST"])
def account_edit():
    return run(request, db.edit_account, ['account'], True)

@app.route("/account/all", methods=["POST"])
def account_all():
    return run(request, db.get_accounts)

@app.route("/checking-accounts", methods=["POST"])
def checking_accounts():
    return run(request, db.get_checking_accounts)

@app.route("/savings-accounts", methods=["POST"])
def savings_accounts():
    return run(request, db.get_savings_accounts)

@app.route("/account/checking/filter", methods=["POST"])
def account_checking_info():
    return run(request, db.get_checking_account_info, ['acc_id', 'cus_id', 'bra_name'])

@app.route("/account/savings/filter", methods=["POST"])
def account_savings_info():
    return run(request, db.get_savings_account_info, ['acc_id', 'cus_id', 'bra_name'])

# ======================================================================================================================
#  LOAN ROUTES
# ======================================================================================================================

@app.route("/loan/add", methods=["POST"])
def loan_add():
    return run(request, db.add_loan, ['loan', 'cus_id'], True)

@app.route("/loan/delete", methods=["POST"])
def loan_delete():
    return run(request, db.delete_loan, ['loa_id'], True)

@app.route("/loan/pay", methods=["POST"])
def loan_pay():
    return run(request, db.pay_loan, ['loan_payment'], True)

@app.route("/loan/all", methods=(["POST"]))
def loans():
    return run(request, db.get_loans)

@app.route("/loan/payments", methods=(["POST"]))
def loan_payments():
    return run(request, db.get_loan_payments, ['loa_id'])

@app.route("/loan/filter", methods=["POST"])
def loan_info():
    return run(request, db.get_loan_info, ['loa_id', 'cus_id', 'bra_name'])

# ======================================================================================================================
# DASHBOARD ROUTES
# ======================================================================================================================

@app.route("/savings-overview", methods=["POST"])
def savings_overview():
    return run(request, db.get_savings_overview)

@app.route("/loans-overview", methods=["POST"])
def loans_overview():
    return run(request, db.get_loans_overview)

@app.route("/balance-overview", methods=["POST"])
def balance_overview():
    return run(request, db.get_balance_overview, ['data'])

@app.route("/customer-overview", methods=["POST"])
def customer_overview():
    return run(request, db.get_customer_overview, ['data'])

# ======================================================================================================================
#  UTILITY FUNCTIONS
# ======================================================================================================================

@app.route("/branch/all", methods=(["POST"]))
def branches():
    return run(request, db.get_branches)

def run(request, func, arg_name_list=[], commit=False):
    res = auth.auth(request.headers)
    if 'error' in res:
        return make_response(res['error'], 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
    
    con = db.login(res['username'], res['password'])
    if con:
        data = request.get_json()
        args = []
        if data:
            for arg_name in arg_name_list:
                if arg_name in data:
                    args.append(data[arg_name])
        res = func(con.cursor(), *args)
        if 'error' in res:
            con.rollback()
            return make_response(res['error'], 400)
        if commit:
            con.commit()
        return make_response(res, 200)
    else:
        return make_response('Failed to authenticate', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

if __name__ == "__main__":

    app.run(host = "0.0.0.0", debug=True)