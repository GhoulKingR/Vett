from sqlite3 import connect
from re import search

get_database = lambda: connect('db/db.sqlite')
valid = lambda name: True if search(r'^[a-zA-Z_]+$', name) != None else False

def init_tables():
    database = get_database()
    database.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        Name            TEXT UNIQUE         NOT NULL,
        ID              INT                 NOT NULL,
        Password        TEXT                NOT NULL
    );
    ''')
    database.close()

def get_creatorid(username):
    db = get_database()
    user_entry = db.execute("SELECT ID FROM Users WHERE Name = ?;", (username, )).fetchone()
    return user_entry[0]

def get_user(id):
    db = get_database()
    user_entry = db.execute("SELECT NAME FROM Users WHERE ID = ?;", (id, )).fetchone()
    return user_entry[0]

def user_exists(username):
    database = get_database()
    cursor = database.execute("SELECT * FROM Users WHERE Name = ?", (username, ))
    exists = len(cursor.fetchall()) > 0
    database.close()
    return exists

def key_exists(key):
    database = get_database()
    cursor = database.execute("SELECT * FROM Users WHERE Key = ?;", (key, ))
    exists = len(cursor.fetchall()) > 0
    database.close()
    return exists

def add_user(username, password):
    if not valid(username):
        return False, 'Username+is+not+valid'
    
    if user_exists(username):
        return False, 'Username+already+exists'
    
    database = get_database()
    cursor = database.execute("SELECT * FROM Users;")
    id = len(cursor.fetchall()) + 1
    query = "INSERT INTO Users (Name, Password, ID) VALUES (?, ?, ?);"
    database.execute(query, (username, password, id))
    database.commit()
    database.close()
    return True, ''

def login_user(username, password):
    if not valid(username):
        return False, 'Username+is+not+valid'
    
    database = get_database()
    query = "SELECT * FROM Users WHERE Name = ? AND Password = ?;"
    correct_password = len(database.execute(query, (username, password)).fetchall()) > 0
    database.close()

    return (
        correct_password,
        '' if correct_password else 'Incorrect+username+or+password'
    )

init_tables()