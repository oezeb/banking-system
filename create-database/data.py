from collections import defaultdict
from dataclasses import dataclass
import json
from random import randint, random, shuffle
from select import select
import requests
from datetime import date, datetime
from time import strptime

def get_random_users(num):
    with open('data/random_users.json', 'r') as f:
        users = json.load(f)
        
    # url = f'https://randomuser.me/api/?results={num}&nat=us'

    # try:
    #     response = requests.get(url)
    #     data = response.json()
    #     if 'results' in data:
    #         for user in data['results']:
    #             id = user['login']['uuid']
    #             if id not in users:
    #                 users[id] = user
    # except:
    #     pass

    # with open('data/random_users.json', 'w') as f:
    #     json.dump(users, f)
    
    # select num random users
    users = list(users.values())
    shuffle(users)
    return { 'results': users[:num] }

def generate_branch_list(min, max):
    branch_list = []
    data = get_random_users(randint(min, max))
    for user in data['results']:
        branch_list.append(
            {
                'bra_name': f'{user["location"]["street"]["name"]} Branch',
                'bra_city': user['location']['city']
            }
        )
    return branch_list        

def generate_department_list(branch_list, min, max):
    print("\nGenerating department list...")
    department_list = []
    department_type_list = [ 'Accounting', 'Banking', 'Insurance', 'Investment', 'Loan', 'Security' ]
    for bra_name in branch_list:
        for i in range(1, randint(min, max)+1):
            branch = {
                'bra_name': bra_name['bra_name'],
                'dep_id': i, 
                'dep_name': f'{department_type_list[i % len(department_type_list)]} Department',
                'dep_type': department_type_list[i % len(department_type_list)]
            }
            department_list.append(branch)
    return department_list

def generate_employee_list(department_list, min, max):
    print("\nGenerating employee list...")
    employee_list = []
    data = get_random_users(5000)
    map = {}
    i = 0
    for department in department_list:
        emp_per_dep = randint(min, max)
        for j in range(emp_per_dep):
            while True:
                emp = data['results'][i*emp_per_dep+j]
                emp_id = f'{emp["id"]["name"]}{emp["id"]["value"]}'
                if emp_id not in map:
                    map[emp_id] = True
                    break
                i += 1
                if i >= len(data['results']):
                    data = get_random_users(5000)
                    i = 0


            bra_name = department['bra_name']
            dep_id = department['dep_id']
            emp_name = f'{emp["name"]["first"]} {emp["name"]["last"]}'
            emp_phone = emp['phone']
            emp_address = f'{emp["location"]["city"]}, {emp["location"]["state"]}'
            start_date = strptime(emp['registered']['date'], '%Y-%m-%dT%H:%M:%S.%fZ')

            emp = {
                'emp_id': emp_id,
                'bra_name': bra_name,
                'dep_id': dep_id,
                'emp_name': emp_name,
                'emp_phone': emp_phone,
                'emp_address': emp_address,
                'start_date': date(start_date.tm_year, start_date.tm_mon, start_date.tm_mday)
            }
            employee_list.append(emp)
        i += 1
    return employee_list

def generate_customer_list(min, max):
    print("\nGenerating customer list...")
    customer_list = []
    cus_num = randint(min, max)
    data = get_random_users(cus_num)
    map = {}
    while cus_num > 0:
        for customer in data['results']:
            if cus_num <= 0:
                break
            cus_id = f'{customer["id"]["name"]}{customer["id"]["value"]}'
            
            if cus_id not in map:
                map[cus_id] = True
                cus_num -= 1
            else:
                continue
            cus_name = f'{customer["name"]["first"]} {customer["name"]["last"]}'
            cus_phone = customer['phone']
            cus_address = f'{customer["location"]["city"]}, {customer["location"]["state"]}'
            cus = {
                'cus_id': cus_id,
                'cus_name': cus_name,
                'cus_phone': cus_phone,
                'cus_address': cus_address
            }
            customer_list.append(cus)
        data = get_random_users(cus_num)
    return customer_list

def generate_contact_list(customer_list):
    print("\nGenerating contact list...")
    relationship_list = [ 'Friend', 'Family', 'Colleague', 'Business', 'Other' ]
    contact_list = []
    data = get_random_users(len(customer_list))
    for i in range(len(customer_list)):
        contact = data['results'][randint(0, len(customer_list)-1)]

        cus_id = customer_list[i]['cus_id']
        con_name = f'{contact["name"]["first"]} {contact["name"]["last"]}'
        con_phone = contact['phone']
        con_email = contact['email']
        con_relation = relationship_list[randint(0, len(relationship_list)-1)]

        con = {
            'cus_id': cus_id,
            'con_name': con_name,
            'con_phone': con_phone,
            'con_email': con_email,
            'con_relation': con_relation
        }
        contact_list.append(con)
    return contact_list

def generate_account_list(branch_list, che_min, che_max, sav_min, sav_max):
    print("\nGenerating account list...")
    acc_id_map = {}

    acc_per_bra = che_max + sav_max + 1
    while True:
        acc_id = str(randint(1, 9999999999999999)).zfill(16)
        acc_id_map[acc_id] = True
        
        if len(acc_id_map) == acc_per_bra * len(branch_list):
            break
    acc_id_list = list(acc_id_map.keys())
    account_list = []
    i = 0
    for branch in branch_list:
        che_acc = randint(che_min, che_max)
        acc_per_bra = che_acc + randint(sav_min, sav_max)
        for j in range(acc_per_bra):
            acc_open_date = date(randint(2000, 2020), randint(1, 12), randint(1, 28))
            acc = {
                'bra_name': branch['bra_name'],
                'acc_id': acc_id_list[i],
                'acc_balance': randint(0, 1000000),
                'acc_type': 1 if j < che_acc else 2, # 1: Checking, 2: Savings
                'acc_open_date': acc_open_date
            }

            if (randint(0, 1) == 1):
                acc['acc_last_activity_date'] = acc_open_date

            account_list.append(acc)
            i += 1
    return account_list

def generate_checking_account_list(account_list):
    print("\nGenerating checking account list...")
    checking_account_list = []
    for account in account_list:
        if account['acc_type'] == 1:
            checking_account_list.append({
                'acc_id': account['acc_id'],
                'che_overdraft': randint(0, 1000000),
                'bra_name': account['bra_name']
            })
    return checking_account_list

def generate_saving_account_list(account_list):
    print("\nGenerating saving account list...")
    saving_account_list = []
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'SEK', 'NZD', 'RUB', 'MXN', 'BRL', 'INR', 'HKD', 'KRW', 'PLN']
    for account in account_list:
        if account['acc_type'] == 2:
            saving_account_list.append({
                'acc_id': account['acc_id'],
                'sav_interest_rate': randint(0, 100),
                'sav_currency': currencies[randint(0, len(currencies)-1)],
                'bra_name': account['bra_name']
            })
    return saving_account_list

def generate_loan_list(branch_list, min, max):
    print("\nGenerating loan list...")
    loan_list = []
    loa_id = 0
    for branch in branch_list:
        lao_num = randint(min, max)
        for i in range(loa_id, loa_id + lao_num):
            loan_list.append({
                'bra_name': branch['bra_name'],
                'loa_id': i,
                'loa_amount': randint(1, 1000000),
                'loa_date': datetime(randint(2000, 2020), randint(1, 12), randint(1, 28), randint(0, 23), randint(0, 59), randint(0, 59))
            })
        loa_id += lao_num
    return loan_list

def generate_loan_pay_list(loan_list, min, max):
    print("\nGenerating loan payment list...")
    loan_pay_list = []
    loan_copy = [loan.copy() for loan in loan_list]
    for loan in loan_copy:
        loan_pay_num = randint(min, max)
        for i in range(loan_pay_num):
            lao_pay_amount = random() * loan['loa_amount']
            loan['loa_amount'] -= lao_pay_amount

            year = randint(loan['loa_date'].year, loan['loa_date'].year + 20)
            if year > loan['loa_date'].year:
                month = randint(loan['loa_date'].month, 12)
            else:
                month = randint(1, 12)
            
            if year == loan['loa_date'].year and month == loan['loa_date'].month:
                day = randint(loan['loa_date'].day, 28)
            else:
                day = randint(1, 28)
            
            if year == loan['loa_date'].year and month == loan['loa_date'].month and day == loan['loa_date'].day:
                hour = randint(loan['loa_date'].hour, 23)
            else:
                hour = randint(0, 23)
            
            if year == loan['loa_date'].year and month == loan['loa_date'].month and day == loan['loa_date'].day and hour == loan['loa_date'].hour:
                minute = randint(loan['loa_date'].minute, 59)
            else:
                minute = randint(0, 59)

            if year == loan['loa_date'].year and month == loan['loa_date'].month and day == loan['loa_date'].day and hour == loan['loa_date'].hour and minute == loan['loa_date'].minute:
                second = randint(loan['loa_date'].second, 59)
            else:
                second = randint(0, 59)

            lao_pay_date = datetime(year, month, day, hour, minute, second)


            loan_pay_list.append({
                'loa_id': loan['loa_id'],
                'loa_pay_id': i,
                'loa_pay_amount': lao_pay_amount,
                'loa_pay_date': lao_pay_date
            })

            if loan['loa_amount'] == 0:
                break
        
    return loan_pay_list

def generate_customer_has_check_account_list(customer_list, checking_account_list, min, max):
    print("\nGenerating customer has checking account list...")
    customer_has_check_account_list = []
    if max > len(checking_account_list):
        max = len(checking_account_list)

    for customer in customer_list:
        num = randint(min, max)
        id_map = {}
        bra_map = {}
        for i in range(num):
            while True:
                j = randint(0, len(checking_account_list)-1)
                acc_id = checking_account_list[j]['acc_id']
                bra_name = checking_account_list[j]['bra_name']
                if acc_id not in id_map and bra_name not in bra_map:
                    id_map[acc_id] = True
                    bra_map[bra_name] = True
                    customer_has_check_account_list.append({
                        'cus_id': customer['cus_id'],
                        'acc_id': acc_id,
                        'bra_name': bra_name
                    })
                    break
    return customer_has_check_account_list

def generate_customer_has_saving_account_list(customer_list, saving_account_list, min, max):
    print("\nGenerating customer has saving account list...")
    customer_has_saving_account_list = []
    if max > len(saving_account_list):
        max = len(saving_account_list)

    for customer in customer_list:
        num = randint(min, max)
        id_map = {}
        bra_map = {}
        for i in range(num):
            while True:
                j = randint(0, len(saving_account_list)-1)
                acc_id = saving_account_list[j]['acc_id']
                bra_name = saving_account_list[j]['bra_name']
                if acc_id not in id_map and bra_name not in bra_map:
                    id_map[acc_id] = True
                    bra_map[bra_name] = True
                    customer_has_saving_account_list.append({
                        'cus_id': customer['cus_id'],
                        'acc_id': acc_id,
                        'bra_name': bra_name
                    })
                    break
    return customer_has_saving_account_list

def generate_loan_relation_list(customer_list, loan_list, min, max):
    print("\nGenerating loan relation list...")
    loan_relation_list = []
    if max > len(loan_list):
        max = len(loan_list)
    
    for customer in customer_list:
        num = randint(min, max)
        id_map = {}
        for i in range(num):
            while True:
                j = randint(0, len(loan_list)-1)
                if loan_list[j]['loa_id'] not in id_map:
                    id_map[loan_list[j]['loa_id']] = True
                    loan_relation_list.append({
                        'cus_id': customer['cus_id'],
                        'loa_id': loan_list[j]['loa_id'],
                        'bra_name': loan_list[j]['bra_name']
                    })
                    break
    return loan_relation_list
                    
def generate_customer_responsible_list(
    employee_list, 
    customer_has_check_account_list,
    customer_has_saving_account_list,
    loan_relation_list,
    min, max
    ):
    print("\nGenerating customer responsible list...")
    customer_responsible_map = {}

    map = {}
    for e in [ *customer_has_check_account_list, * customer_has_saving_account_list, * loan_relation_list ]:
        if e['bra_name'] not in map:
            map[e['bra_name']] = {}
        if 'customers' not in map[e['bra_name']]:
            map[e['bra_name']]['customers'] = {}
        map[e['bra_name']]['customers'][e['cus_id']] = True
    for e in employee_list:
        if e['bra_name'] not in map:
            map[e['bra_name']] = {}
        if 'employees' not in map[e['bra_name']]:
            map[e['bra_name']]['employees'] = {}
        map[e['bra_name']]['employees'][e['emp_id']] = True
    
    for branch in map:
        cus_list = list(map[branch]['customers'].keys())
        emp_list = list(map[branch]['employees'].keys())
        num = randint(min, max)
        type = randint(1, 2)
        count = 0
        while count < num:
            while True:
                i = randint(0, len(cus_list)-1)
                j = randint(0, len(emp_list)-1)
                key = f'{cus_list[i]}_{emp_list[j]}_{type}'
                if key in customer_responsible_map:
                    if type == 1:
                        key = f'{cus_list[i]}_{emp_list[j]}_2'
                    else:
                        key = f'{cus_list[i]}_{emp_list[j]}_1'
                    
                    if key in customer_responsible_map:
                        continue
                customer_responsible_map[key] = {
                    'cus_id': cus_list[i],
                    'emp_id': emp_list[j],
                    'type': type
                }
                count += 1
                break
    return customer_responsible_map.values()