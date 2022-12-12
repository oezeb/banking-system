import sqlite3
from time import time
from uuid import uuid4

_db = 'auth.db'
_table = 'users'
_session_timeout = 3600

def init():
    con = sqlite3.connect(_db)
    cursor = con.cursor()
    cursor.execute(
        f'''CREATE TABLE IF NOT EXISTS {_table} (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            auth_token TEXT NOT NULL,
            expiry_date TEXT NOT NULL
        )'''
    )
    con.close()

def auth(headers):
    # connect to auth db
    con = sqlite3.connect('auth.db')
    cursor = con.cursor()
    # get token
    try:
        token = headers['Authorization'].split(' ')[1]
    except:
        return {'error': 'Token required'}
    # get username and password
    try:
        cursor.execute(f"SELECT * FROM users WHERE auth_token = '{token}'")
        user = cursor.fetchone()
        if float(user[3]) < time():
            return {'error': 'Token expired'}
        return {'username': user[0], 'password': user[1]}
    except:
        return {'error': 'Invalid token'}

def get(username):
    con = sqlite3.connect('auth.db')
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    user = cursor.fetchone()
    con.close()
    return dict(zip(['username', 'password', 'auth_token', 'expiry_date'] , user))

def add(username, password):
    try:
        user = get(username)
    except:
        pass

    con = sqlite3.connect('auth.db')
    cursor = con.cursor()
    if user:
        user['password'] = password
        if float(user['expiry_date']) < time():
            user['auth_token'] = str(uuid4())
            user['expiry_date'] = time() + _session_timeout
        _update(cursor, user)
    else:
        user = {
            'username': username,
            'password': password,
            'auth_token': str(uuid4()),
            'expiry_date': time() + _session_timeout
        }
        _insert(cursor, user)
    con.commit()
    con.close()
    return user['auth_token']

        
    

def _update(cursor, user):
    cursor.execute(
        f'''UPDATE users SET 
            {", ".join([f"{k} = '{v}'" for k, v in user.items()])}
            WHERE username = '{user['username']}'
        '''
    )

def _insert(cursor, user):
    cursor.execute(
        f'''INSERT INTO users VALUES (
            '{user['username']}',
            '{user['password']}',
            '{user['auth_token']}',
            '{user['expiry_date']}'
        )'''
    )

if __name__ == '__main__':
    init()