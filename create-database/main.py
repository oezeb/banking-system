
import MySQLdb

from data import *

# connect to database
msq = '''
Connect to an account that has the following permissions:
    CREATE, DROP, ALTER, GRANT, INSERT
'''
print(msq)

host = 'localhost'
user = input('Username: ')
password = input('Password: ')

db = MySQLdb.connect(host, user, password)
cursor = db.cursor()

# create database
db_name = 'bankingsystem'
print(f'\nCreating {db_name} database...')
sql = f'''
    DROP DATABASE IF EXISTS {db_name};
    CREATE DATABASE {db_name};
    USE {db_name};
'''
cursor.execute(sql)

# create tables
print('\nCreating tables...')
with open('create-tables.sql', 'r') as f:
    sql = f.read()
    cursor.execute(sql)

# create testing data
print('\nCreating testing data...')
print('\nCreating user...')
user = { 'username': 'test', 'password': 'test' }
sql = f'''
    DROP USER IF EXISTS '{user['username']}'@'localhost';
    CREATE USER '{user['username']}'@'localhost' IDENTIFIED BY '{user['password']}';
    GRANT SELECT, INSERT, UPDATE, DELETE ON {db_name}.* TO '{user['username']}'@'localhost';
'''
cursor.execute(sql)

# insert testing data
print('\nGenerating random data...')
branch_list = generate_branch_list(1, 3)
department_list = generate_department_list(branch_list, 1, 2)
employee_list = generate_employee_list(department_list, 4, 6)
customer_list = generate_customer_list(5, 7)
contact_list = generate_contact_list(customer_list)
account_list = generate_account_list(branch_list, 5, 10, 5, 10)
checking_account_list = generate_checking_account_list(account_list)
saving_account_list = generate_saving_account_list(account_list)
loan_list = generate_loan_list(branch_list, 5, 10)
loan_pay_list = generate_loan_pay_list(loan_list, 1, 3)
customer_has_check_account_list = generate_customer_has_check_account_list(customer_list, checking_account_list, 1, len(branch_list))
customer_has_saving_account_list = generate_customer_has_saving_account_list(customer_list, saving_account_list, 0, len(branch_list))
loan_relation_list = generate_loan_relation_list(customer_list, loan_list, 0, 10)
customer_responsible_list = generate_customer_responsible_list(employee_list, customer_has_check_account_list, customer_has_saving_account_list, loan_relation_list, 0, 3)

print('\nInserting data...')
print('\nInserting branch...')
for branch in branch_list:
    sql = f'''
        INSERT INTO branch (bra_name, bra_city)
        VALUES (
            '{branch['bra_name']}', 
            '{branch['bra_city']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting department...')
for department in department_list:
    sql = f'''
        INSERT INTO department (bra_name, dep_id, dep_name, dep_type)
        VALUES (
            '{department['bra_name']}', 
             {department['dep_id'  ]}, 
            '{department['dep_name']}', 
            '{department['dep_type']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting employee...')
for employee in employee_list:
    sql = f'''
        INSERT INTO employee (emp_id, bra_name, dep_id, emp_name, emp_phone, emp_address, start_date)
        VALUES (
            '{employee['emp_id'     ]}',
            '{employee['bra_name'   ]}',
             {employee['dep_id'     ]},
            '{employee['emp_name'   ]}',
            '{employee['emp_phone'  ]}',
            '{employee['emp_address']}',
            '{employee['start_date' ]}'
        );
    '''
    cursor.execute(sql)

print('\nInserting customer...')
for customer in customer_list:
    sql = f'''
        INSERT INTO customer (cus_id, cus_name, cus_phone, cus_address)
        VALUES (
            '{customer['cus_id'     ]}',
            '{customer['cus_name'   ]}',
            '{customer['cus_phone'  ]}',
            '{customer['cus_address']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting contact...')
for contact in contact_list:
    sql = f'''
        INSERT INTO contact (cus_id, con_name, con_phone, con_email, con_relation)
        VALUES (
            '{contact['cus_id'      ]}',
            '{contact['con_name'    ]}',
            '{contact['con_phone'   ]}',
            '{contact['con_email'   ]}',
            '{contact['con_relation']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting account...')
for account in account_list:
    sql = f'''
        INSERT INTO account (bra_name, acc_id, acc_balance, acc_type, acc_open_date)
        VALUES (
            '{account['bra_name']}',
            '{account['acc_id'  ]}',
             {account['acc_balance']},
             {account['acc_type']},
            '{account['acc_open_date']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting checking account...')
for checking_account in checking_account_list:
    sql = f'''
        INSERT INTO checking_account (acc_id, che_overdraft)
        VALUES (
            '{checking_account['acc_id']}',
             {checking_account['che_overdraft']}
        );
    '''
    cursor.execute(sql)

print('\nInserting savings account...')
for saving_account in saving_account_list:
    sql = f'''
        INSERT INTO savings_account (acc_id, sav_interest_rate, sav_currency)
        VALUES (
            '{saving_account['acc_id']}',
             {saving_account['sav_interest_rate']},
            '{saving_account['sav_currency']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting loan...')
for loan in loan_list:
    sql = f'''
        INSERT INTO loan (bra_name, loa_id, loa_amount, loa_date)
        VALUES (
            '{loan['bra_name']}',
             {loan['loa_id'  ]},
             {loan['loa_amount']},
            '{loan['loa_date']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting loan payment...')
for pay_loan in loan_pay_list:
    sql = f'''
        INSERT INTO loan_payment (loa_id, loa_pay_id, loa_pay_amount, loa_pay_date)
        VALUES (
             {pay_loan['loa_id' ]},
             {pay_loan['loa_pay_id']},
             {pay_loan['loa_pay_amount']},
            '{pay_loan['loa_pay_date']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting customer has check account relation...')
for customer_has_check_account in customer_has_check_account_list:
    sql = f'''
        INSERT INTO customer_has_checking_account (cus_id, acc_id)
        VALUES (
            '{customer_has_check_account['cus_id']}',
            '{customer_has_check_account['acc_id']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting customer has saving account relation...')
for customer_has_saving_account in customer_has_saving_account_list:
    sql = f'''
        INSERT INTO customer_has_savings_account (cus_id, acc_id)
        VALUES (
            '{customer_has_saving_account['cus_id']}',
            '{customer_has_saving_account['acc_id']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting loan relation...')
for loan_relation in loan_relation_list:
    sql = f'''
        INSERT INTO customer_loan_relation (cus_id, loa_id)
        VALUES (
            '{loan_relation['cus_id']}',
            '{loan_relation['loa_id']}'
        );
    '''
    cursor.execute(sql)

print('\nInserting customer responsible...')
for customer_responsible in customer_responsible_list:
    sql = f'''
        INSERT INTO customer_employee_relation (emp_id, cus_id, type)
        VALUES (
            '{customer_responsible['emp_id']}',
            '{customer_responsible['cus_id']}',
             {customer_responsible['type']}
        );
    '''
    cursor.execute(sql)

# commit and close
print('\nCommitting...')
db.commit()

cursor.execute('SHOW TABLES;')
tables = "\t"
for table in cursor.fetchall():
    tables += f'{table[0]}\n\t'

msg = f'''
Done!

Database: {db_name}
Tables: 
    {tables}

Login from browser:
User: {user['username']}
Password: {user['password']}

closing connection...
'''
print(msg)

db.close()