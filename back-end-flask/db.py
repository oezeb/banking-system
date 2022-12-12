from datetime import datetime
from time import strftime
import MySQLdb

HOST = 'localhost'
DB_NAME = 'bankingsystem'

def main():
    pass

# ======================================================================================================================
#  LOGIN
# ======================================================================================================================

def login(username, password):
    try:
        return MySQLdb.connect(host=HOST, user=username, passwd=password, db=DB_NAME)
    except:
        return None

# ======================================================================================================================
#  CUSTOMER
# ======================================================================================================================

def add_customer(cursor, customer, contact):
    res = _add(cursor, 'customer', customer, ['cus_id'])
    if res['success']:
        res = _add(cursor, 'contact', contact, ['cus_id'])
    return res

def delete_customer(cursor, cus_id):
    if _exists(cursor, 'customer_has_checking_account', { 'cus_id': cus_id }):
        return { 'success': False, 'error': 'Customer has checking accounts' }
    if _exists(cursor, 'customer_has_savings_account', { 'cus_id': cus_id }):
        return { 'success': False, 'error': 'Customer has savings accounts' }
    if _exists(cursor, 'customer_loan_relation', { 'cus_id': cus_id }):
        return { 'success': False, 'error': 'Customer has loans' }
    try:
        _delete(cursor, 'customer_employee_relation', f"cus_id = '{cus_id}'")
        _delete(cursor, 'contact', f"cus_id = '{cus_id}'")
        _delete(cursor, 'customer', f"cus_id = '{cus_id}'")
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def edit_customer(cursor, customer, contact):
    res = _edit(cursor, 'customer', customer, f"cus_id = '{customer['cus_id']}'")
    if res['success']:
        res = _edit(cursor, 'contact', contact, f"cus_id = '{customer['cus_id']}'")
    return res

def get_customers(cursor, condition: str = None):
    return _getter(cursor, ['customer', 'contact'], condition)

def get_customer_info(cursor, cus_id=None, cus_name=None):
    sql = '''SELECT * FROM customer NATURAL JOIN contact'''
    conditions = [(key, value) for key, value in zip(['cus_id', 'cus_name'], [cus_id, cus_name]) if value != None]
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join([f"{key} = '{value}'" for key, value in conditions])
    return _run(cursor, sql)

# ======================================================================================================================
#  ACCOUNT
# ======================================================================================================================

def add_account(cursor, account, cus_id):
    # check if the customer already have the same type of account in the same branch
    sql = f'''
        SELECT * FROM account NATURAL JOIN (
            SELECT * FROM customer_has_checking_account
            UNION
            SELECT * FROM customer_has_savings_account
        ) AS customer_has_account
        WHERE cus_id = '{cus_id}' AND acc_type = '{account['acc_type']}' AND bra_name = '{account['bra_name']}'
    '''
    res = _run(cursor, sql)
    if res['success']:
        if len(res['rows']) > 0:
            return {'success': False, 'error': 'Customer already have an account in the same branch'}

        account['acc_open_date'] = datetime.now().strftime("%Y-%m-%d")
        if account['acc_type'] == 1: # checking account
            checking_account = {
                'acc_id': account['acc_id'],
                'che_overdraft': account['che_overdraft']
            }
            account.pop('che_overdraft')

            res = _add(cursor, 'account', account, ['acc_id'])
            if res['success']:
                res = _add(cursor, 'checking_account', checking_account, ['acc_id'])
                if res['success']:
                    relation = { 'cus_id': cus_id, 'acc_id': account['acc_id'] }
                    res = _add(cursor, 'customer_has_checking_account', relation, ['cus_id', 'acc_id'])
        elif account['acc_type'] == 2: # savings account
            savings_account = {
                'acc_id': account['acc_id'],
                'sav_interest_rate': account['sav_interest_rate'],
                'sav_currency': account['sav_currency']
            }
            account.pop('sav_interest_rate')
            account.pop('sav_currency')

            res = _add(cursor, 'account', account, ['acc_id'])
            if res['success']:
                res = _add(cursor, 'savings_account', savings_account, ['acc_id'])
                if res['success']:
                    relation = { 'cus_id': cus_id, 'acc_id': account['acc_id'] }
                    res = _add(cursor, 'customer_has_savings_account', relation, ['cus_id', 'acc_id'])
        else:
            res = {'success': False, 'error': 'Invalid account type'}
    return res

def delete_account(cursor, acc_id):
    try:
        _delete(cursor, 'customer_has_checking_account', f"acc_id = '{acc_id}'")
        _delete(cursor, 'customer_has_savings_account', f"acc_id = '{acc_id}'")
        _delete(cursor, 'checking_account', f"acc_id = '{acc_id}'")
        _delete(cursor, 'savings_account', f"acc_id = '{acc_id}'")
        _delete(cursor, 'account', f"acc_id = '{acc_id}'")
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def edit_account(cursor, account):
    if account['acc_type'] == 1: # checking account
        checking_account = {
            'acc_id': account['acc_id'],
            'che_overdraft': account['che_overdraft']
        }
        account.pop('che_overdraft')

        res = _edit(cursor, 'account', account, f"acc_id = '{account['acc_id']}'")
        if res['success']:
            res = _edit(cursor, 'checking_account', checking_account, f"acc_id = '{account['acc_id']}'")
    elif account['acc_type'] == 2: # savings account
        savings_account = {
            'acc_id': account['acc_id'],
            'sav_interest_rate': account['sav_interest_rate'],
            'sav_currency': account['sav_currency']
        }
        account.pop('sav_interest_rate')
        account.pop('sav_currency')

        res = _edit(cursor, 'account', account, f"acc_id = '{account['acc_id']}'")
        if res['success']:
            res = _edit(cursor, 'savings_account', savings_account, f"acc_id = '{account['acc_id']}'")
    else:
        res = {'success': False, 'error': 'Invalid account type'}
    return res
def get_accounts(cursor, condition: str = None):
    return _getter(cursor, ['account'], condition)

def get_checking_accounts(cursor, condition: str = None):
    return _getter(cursor, ['account', 'checking_account'], condition)

def get_savings_accounts(cursor, condition: str = None):
    return _getter(cursor, ['account', 'savings_account'], condition)

def get_checking_account_info(cursor, acc_id = None, cus_id=None, bra_name=None):
    sql = '''
        SELECT account.acc_id, bra_name, acc_balance, acc_type, acc_last_activity_date, che_overdraft, cus_id
        FROM account NATURAL JOIN checking_account LEFT JOIN customer_has_checking_account ON account.acc_id = customer_has_checking_account.acc_id
    '''
    conditions = [(key, value) for key, value in zip(['account.acc_id', 'cus_id', 'bra_name'], [acc_id, cus_id, bra_name]) if value != None]
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join([f"{key} = '{value}'" for key, value in conditions])
    return _run(cursor, sql)

def get_savings_account_info(cursor, acc_id = None, cus_id=None, bra_name=None):
    sql = '''
        SELECT account.acc_id, bra_name, acc_balance, acc_type, acc_last_activity_date, sav_interest_rate, sav_currency, cus_id
        FROM account NATURAL JOIN savings_account LEFT JOIN customer_has_savings_account ON account.acc_id = customer_has_savings_account.acc_id
    '''
    conditions = [(key, value) for key, value in zip(['account.acc_id', 'cus_id', 'bra_name'], [acc_id, cus_id, bra_name]) if value != None]
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join([f"{key} = '{value}'" for key, value in conditions])
    return _run(cursor, sql)

# ======================================================================================================================
#  LOAN
# ======================================================================================================================

def add_loan(cursor, loan, cus_id):
    sql = f"SELECT MAX(loa_id) FROM loan"
    res = _run(cursor, sql)
    if res['success']:
        if len(res['rows']) > 0:
            loan['loa_id'] = res['rows'][0][0] + 1
        else:
            loan['loa_id'] = 1

        loan['loa_date'] = datetime.now().strftime("%Y-%m-%d")

        res = _add(cursor, 'loan', loan, ['loa_id'])
        if res['success']:
            relation = { 'cus_id': cus_id, 'loa_id': loan['loa_id'] }
            res = _add(cursor, 'customer_loan_relation', relation, ['cus_id', 'loa_id'])
    return res

def delete_loan(cursor, loa_id):
    try:
        cursor.execute(f"SELECT SUM(loa_pay_amount) FROM loan_payment WHERE loa_id = '{loa_id}'")
        total_paid = cursor.fetchone()[0]
        cursor.execute(f"SELECT loa_amount FROM loan WHERE loa_id = '{loa_id}'")
        loan_amount = cursor.fetchone()[0]
    except Exception as e:
        return {'success': False, 'error': str(e)}

    if total_paid == None:
        total_paid = 0
    if total_paid < loan_amount:
        return {'success': False, 'error': 'Loan is not fully paid'}
    
    try:
        _delete(cursor, 'customer_loan_relation', f"loa_id = '{loa_id}'")
        _delete(cursor, 'loan_payment', f"loa_id = '{loa_id}'")
        _delete(cursor, 'loan', f"loa_id = '{loa_id}'")
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def pay_loan(cursor, loan_payment):
    sql = f"SELECT MAX(loa_pay_id) FROM loan_payment WHERE loa_id = '{loan_payment['loa_id']}'"
    try:
        cursor.execute(sql)
        max_id = cursor.fetchone()[0]
    except Exception as e:
        return {'success': False, 'error': str(e)}
    if max_id == None:
        max_id = 0
    loan_payment['loa_pay_id'] = max_id + 1
    loan_payment['loa_pay_date'] = datetime.now()
    return _add(cursor, 'loan_payment', loan_payment, ['loa_id', 'loa_pay_id'])

def get_loans(cursor, condition: str = None):
    return _getter(cursor, ['loan'], condition)

def get_loan_info(cursor, loa_id = None, cus_id=None, bra_name=None):
    sql = '''
       SELECT loan.loa_id, bra_name, loa_amount, loa_date, cus_id, total_paid, (total_paid >= loa_amount) AS fully_paid
            FROM loan 
            LEFT JOIN customer_loan_relation ON loan.loa_id = customer_loan_relation.loa_id
            LEFT JOIN (
                SELECT loa_id, SUM(loa_pay_amount) AS total_paid
                FROM loan_payment
                GROUP BY loa_id
            ) AS payments ON loan.loa_id = payments.loa_id
    '''
    conditions = [(key, value) for key, value in zip(['loan.loa_id', 'cus_id', 'bra_name'], [loa_id, cus_id, bra_name]) if value != None]
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join([f"{key} = '{value}'" for key, value in conditions])
    return _run(cursor, sql)

def get_loan_payments(cursor, loa_id):
    return _getter(cursor, ['loan_payment'], f"loa_id = '{loa_id}'")

# ======================================================================================================================
#  DASHBOARD
# ======================================================================================================================

def get_savings_overview(cursor):
    return _run(cursor, '''
        SELECT * FROM 
            (SELECT bra_name, SUM(acc_balance) AS total_balance 
            FROM account WHERE acc_type=2 
            GROUP BY bra_name) AS savings
            NATURAL JOIN
            (SELECT bra_name, COUNT(*) AS total_customers 
            FROM customer NATURAL JOIN customer_has_savings_account NATURAL JOIN account
            GROUP BY bra_name) AS customers;
    ''')

def get_loans_overview(cursor):
    return _run(cursor, '''
        SELECT * FROM
            (SELECT bra_name, SUM(loa_amount) AS total_loan
            FROM loan
            GROUP BY bra_name) AS loans
            NATURAL JOIN
            (SELECT bra_name, COUNT(*) AS total_customers
            FROM customer NATURAL JOIN customer_loan_relation NATURAL JOIN loan
            GROUP BY bra_name) AS customers;
    ''')

def get_balance_overview(cursor, data):
    try:
        if data['type'] == 'savings':
            if data['order_by'] == 'year':
                return _get_savings_order_by_year(cursor, data['bra_name'])
            elif data['order_by'] == 'month':
                return _get_savings_order_by_month(cursor, data['bra_name'])
            elif data['order_by'] == 'season':
                return _get_savings_order_by_season(cursor, data['bra_name'])
        elif data['type'] == 'loans':
            if data['order_by'] == 'year':
                return _get_loans_order_by_year(cursor, data['bra_name'])
            elif data['order_by'] == 'month':
                return _get_loans_order_by_month(cursor, data['bra_name'])
            elif data['order_by'] == 'season':
                return _get_loans_order_by_season(cursor, data['bra_name'])
    except Exception as e:
        return {'success': False, 'error': str(e)}
    return {'success': False, 'error': 'Invalid type or order_by'}

def get_customer_overview(cursor, data):
    try:
        if data['type'] == 'savings':
            if data['order_by'] == 'year':
                return _get_savings_customer_count_by_year(cursor, data['bra_name'])
            elif data['order_by'] == 'month':
                return _get_savings_customer_count_by_month(cursor, data['bra_name'])
            elif data['order_by'] == 'season':
                return _get_savings_customer_count_by_season(cursor, data['bra_name'])
        elif data['type'] == 'loans':
            if data['order_by'] == 'year':
                return _get_loans_customer_count_by_year(cursor, data['bra_name'])
            elif data['order_by'] == 'month':
                return _get_loans_customer_count_by_month(cursor, data['bra_name'])
            elif data['order_by'] == 'season':
                return _get_loans_customer_count_by_season(cursor, data['bra_name'])
    except Exception as e:
        return {'success': False, 'error': str(e)}
    return {'success': False, 'error': 'Invalid type or order_by'}

def _get_savings_order_by_year(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(acc_open_date) AS year, SUM(acc_balance) AS total_balance 
        FROM account WHERE acc_type = 2 AND bra_name = '{bra_name}'
        GROUP BY bra_name, year(acc_open_date) ORDER BY bra_name, year;
    ''')

def _get_savings_order_by_month(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(acc_open_date) AS year, MONTH(acc_open_date) AS month, SUM(acc_balance) AS total_balance 
        FROM account WHERE acc_type = 2 AND bra_name = '{bra_name}'
        GROUP BY bra_name, year(acc_open_date), month(acc_open_date) ORDER BY bra_name, year, month;
    ''')

def _get_savings_order_by_season(cursor, bra_name):
    return _run(cursor, f'''
    SELECT bra_name, YEAR(acc_open_date) AS year, CASE FLOOR((MONTH(acc_open_date) % 12)/3) 
        WHEN 0 THEN '冬季'
        WHEN 1 THEN '春季'
        WHEN 2 THEN '夏季'
        WHEN 3 THEN '秋季'
    END AS season, SUM(acc_balance)  AS total_balance 
    FROM account WHERE acc_type=2 AND bra_name = '{bra_name}'
    GROUP BY bra_name, year(acc_open_date), season ORDER BY bra_name, year, season;
    ''')

def _get_savings_customer_count_by_year(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(acc_open_date) AS year, COUNT(*) AS total_customers 
        FROM customer NATURAL JOIN customer_has_savings_account NATURAL JOIN account
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(acc_open_date) ORDER BY bra_name, year;
    ''')

def _get_savings_customer_count_by_month(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(acc_open_date) AS year, MONTH(acc_open_date) AS month, COUNT(*) AS total_customers 
        FROM customer NATURAL JOIN customer_has_savings_account NATURAL JOIN account
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(acc_open_date), month(acc_open_date) ORDER BY bra_name, year, month;
    ''')

def _get_savings_customer_count_by_season(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(acc_open_date) AS year, CASE FLOOR((MONTH(acc_open_date) % 12)/3)
            WHEN 0 THEN '冬季'
            WHEN 1 THEN '春季'
            WHEN 2 THEN '夏季'
            WHEN 3 THEN '秋季'
        END AS season, COUNT(*) AS total_customers
        FROM customer NATURAL JOIN customer_has_savings_account NATURAL JOIN account
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(acc_open_date), season ORDER BY bra_name, year, season;
    ''')

def _get_loans_order_by_year(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(loa_date) AS year, SUM(loa_amount) AS total_loan
        FROM loan
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(loa_date) ORDER BY bra_name, year;
    ''')

def _get_loans_order_by_month(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(loa_date) AS year, MONTH(loa_date) AS month, SUM(loa_amount) AS total_loan
        FROM loan
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(loa_date), month(loa_date) ORDER BY bra_name, year, month;
    ''')

def _get_loans_order_by_season(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(loa_date) AS year, CASE FLOOR((MONTH(loa_date) % 12)/3)
            WHEN 0 THEN '冬季'
            WHEN 1 THEN '春季'
            WHEN 2 THEN '夏季'
            WHEN 3 THEN '秋季'
        END AS season, SUM(loa_amount) AS total_loan
        FROM loan
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(loa_date), season ORDER BY bra_name, year, season;
    ''')

def _get_loans_customer_count_by_year(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(loa_date) AS year, COUNT(*) AS total_customers
        FROM customer NATURAL JOIN customer_loan_relation NATURAL JOIN loan
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(loa_date) ORDER BY bra_name, year;
    ''')

def _get_loans_customer_count_by_month(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(loa_date) AS year, MONTH(loa_date) AS month, COUNT(*) AS total_customers
        FROM customer NATURAL JOIN customer_loan_relation NATURAL JOIN loan
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(loa_date), month(loa_date) ORDER BY bra_name, year, month;
    ''')

def _get_loans_customer_count_by_season(cursor, bra_name):
    return _run(cursor, f'''
        SELECT bra_name, YEAR(loa_date) AS year, CASE FLOOR((MONTH(loa_date) % 12)/3)
            WHEN 0 THEN '冬季'
            WHEN 1 THEN '春季'
            WHEN 2 THEN '夏季'
            WHEN 3 THEN '秋季'
        END AS season, COUNT(*) AS total_customers
        FROM customer NATURAL JOIN customer_loan_relation NATURAL JOIN loan
        WHERE bra_name = '{bra_name}'
        GROUP BY bra_name, year(loa_date), season ORDER BY bra_name, year, season;
    ''')

# ======================================================================================================================
#  UTILITY FUNCTIONS
# ======================================================================================================================

def get_branches(cursor):
    return _getter(cursor, ['branch'])

def _select(cursor, columns: list[str], table: str, condition: str = None):
    sql = f"SELECT {', '.join(columns)} FROM {table}"
    if condition:
        sql += f" WHERE {condition}"
    cursor.execute(sql)
    return cursor.fetchall()

def _insert(cursor, table: str, data: dict):
    sql = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['%s'] * len(data.values()))})"
    cursor.execute(sql, data.values())

def _delete(cursor, table: str, condition: str):
    sql = f"DELETE FROM {table}"
    if condition:
        sql += f" WHERE {condition}"
    cursor.execute(sql)

def _update(cursor, table: str, data: dict, condition: str):
    sql = f"UPDATE {table} SET {', '.join([f'{key} = %s' for key in data.keys()])}"
    if condition:
        sql += f" WHERE {condition}"
    cursor.execute(sql, data.values())
    
def _eq_condition(data: dict):
    return ' AND '.join([f"{key} = '{value}'" for key, value in data.items()])

def _get_columns(cursor, tables: list[str]):
    columns = []
    for table in tables:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns.extend([column[0] for column in cursor.fetchall() if column[0] not in columns])
    return columns

def _getter(cursor, tables: list[str], condition: str = None):
    columns = _get_columns(cursor, tables)
    table = ' natural join '.join(tables)
    return {
        'columns': columns,
        'rows': _select(cursor, columns, table, condition)
    }

def _exists(cursor, table: str, data: dict):
    return len(_getter(cursor, [table], _eq_condition(data))['rows']) > 0

def _add(cursor, table: str, data: dict, primary_keys: list[str]):
    if _exists(cursor, table, dict([(key, data[key]) for key in primary_keys])):
        return {'success': False, 'error': f'Already exists'}

    try:
        _insert(cursor, table, data)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _edit(cursor, table: str, data: dict, condition: str):
    try:
        _update(cursor, table, data, condition)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _run(cursor, sql: str):
    try:
        cursor.execute(sql)
        return {
            'success': True,
            'columns': [column[0] for column in cursor.description],
            'rows': cursor.fetchall()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    main()