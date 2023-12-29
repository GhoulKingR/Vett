from re import search
from time import time
from datetime import datetime
from sqlite3 import connect
from .user import get_creatorid, get_user

get_database = lambda: connect('db/db.sqlite')
valid = lambda name: True if search(r'^[a-z-_]+$', name) != None else False

def init_tables():
    database = get_database()
    database.execute('''
    CREATE TABLE IF NOT EXISTS Boards (
        Name            TEXT                    NOT NULL,
        InviteOnly      INT                     NOT NULL,
        CreatorID       INT                     NOT NULL,
        Description     TEXT                    NOT NULL,
        ID              INT PRIMARY KEY         NOT NULL,
        Timestamp       TEXT                    NOT NULL
    );
    ''')
    database.execute('''
    CREATE TABLE IF NOT EXISTS Posts (
        Id          INT     PRIMARY KEY     NOT NULL,
        User        TEXT                    NOT NULL,
        Content     TEXT                    NOT NULL,
        Board       TEXT                    NOT NULL,
        BoardCreatorID  TEXT                NOT NULL,
        Timestamp   TEXT                    NOT NULL,
        PostReplyID INT
    );
    ''')
    database.close()

def board_exists(user, name):
    id = get_creatorid(user)
    database = get_database()
    cursor = database.execute("SELECT * FROM Boards WHERE Name = ? AND CreatorID = ?", (name, id))
    exists = len(cursor.fetchall()) > 0
    database.close()
    return exists
    
def setup_board(invite_only, name, username, description):
    if not valid(name):
        return False, f"\"{name}\"+is+not+valid.+Names+should+only+include+-,+_,+and+lowercase+letters."
    
    if board_exists(username, name):
        return False, f"Board+with+name+\"{name}\"+already+exist"
    
    if username == None:
        return False, "How+did+you+create+a+board+while+not+logged+in?+💀"
    
    database = get_database()
    cursor = database.execute("SELECT * FROM Boards;")
    id = len(cursor.fetchall())
    creatorid = get_creatorid(username)
    query = "INSERT INTO Boards (Name, InviteOnly, CreatorID, Description, ID, Timestamp) VALUES (?, ?, ?, ?, ?, ?);"
    database.execute(query, (name, invite_only, creatorid, description, id, str(time())))
    database.commit()
    database.close()
    return True, ""
    
def add_post(content, user, board_name, admin):
    if not board_exists(admin, board_name):
        return False
    
    adminid = get_creatorid(admin)
    database = get_database()
    cursor = database.execute("SELECT * FROM Posts;")
    id = len(cursor.fetchall()) + 1
    query = "INSERT INTO Posts (Id, User, Content, Board, Timestamp, BoardCreatorID) VALUES (?, ?, ?, ?, ?, ?);"
    database.execute(query, (id, user, content, board_name, str(time()), adminid))
    database.commit()
    database.close()
    return True

def add_reply(content, user, board_name, admin, post_id):
    if not board_exists(admin, board_name):
        return False
    
    adminid = get_creatorid(admin)
    database = get_database()
    cursor = database.execute("SELECT * FROM Posts;")
    id = len(cursor.fetchall()) + 1
    query = "INSERT INTO Posts (Id, User, Content, Board, Timestamp, BoardCreatorID, PostReplyID) VALUES (?, ?, ?, ?, ?, ?, ?);"
    database.execute(query, (id, user, content, board_name, str(time()), adminid, post_id))
    database.commit()
    database.close()
    return True

def get_posts(user, board_name):
    id = get_creatorid(user)
    database = get_database()
    cursor = database.execute("SELECT User, Content, Timestamp, ID, PostReplyID FROM Posts WHERE Board = ? AND BoardCreatorID = ?", (board_name, id))
    records = cursor.fetchall()
    result = []
    
    for record in records:
        if record[4] == None:
            result.append({
                'id': record[3],
                'from': record[0],
                'content': record[1],
                'time':  datetime.fromtimestamp(float(record[2])).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    database.close()
    return result

def get_post_replies(user, board_name, post_id):
    id = get_creatorid(user)
    database = get_database()
    cursor = database.execute("SELECT User, Content, Timestamp FROM Posts WHERE Board = ? AND BoardCreatorID = ? AND PostReplyID = ?", (board_name, id, post_id))
    records = cursor.fetchall()
    result = []
    
    for record in records:
        result.append({
            'from': record[0],
            'content': record[1],
            'time':  datetime.fromtimestamp(float(record[2])).strftime("%Y-%m-%d %H:%M:%S")
        })

    database.close()
    return result

def get_boards():
    database = get_database()
    cursor = database.execute("SELECT Name, CreatorID FROM Boards WHERE InviteOnly = 0")
    records = cursor.fetchall()
    database.close()
    boards = [
        { 'name': f'{get_user(record[1])}/{record[0]}' }
        for record in records
    ]
    boards.reverse()
    return boards

def get_description(admin, board_name):
    id = get_creatorid(admin)
    database = get_database()
    cursor = database.execute("SELECT Description FROM Boards WHERE Name = ? AND CreatorID = ?", (board_name, id))
    description = cursor.fetchone()[0]
    database.close()
    return description

def get_creation_time(admin, board_name):
    id = get_creatorid(admin)
    database = get_database()
    cursor = database.execute("SELECT Timestamp FROM Boards WHERE Name = ? AND CreatorID = ?", (board_name, id))
    creation_time = cursor.fetchone()[0]
    database.close()
    return datetime.fromtimestamp(float(creation_time)).strftime("%Y-%m-%d %H:%M:%S")

def is_board_private(admin, board_name):
    id = get_creatorid(admin)
    database = get_database()
    cursor = database.execute("SELECT InviteOnly FROM Boards WHERE Name = ? AND CreatorID = ?", (board_name, id))
    is_private = cursor.fetchone()[0]
    database.close()
    return is_private

init_tables()