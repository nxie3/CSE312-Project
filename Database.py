import hashlib

from pymongo import MongoClient
import bcrypt

mongo_client = MongoClient('mongo')
db = mongo_client["login_database"]

users = db["user_list"]
tokens = db["token_list"]


def add_users(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed})


def login_token(username, cookie):
    token = hashlib.sha256(cookie.encode()).hexdigest()
    tokens.insert_one({"token": token, "username": username})


def find_logged(cookie):
    token = hashlib.sha256(cookie.encode()).hexdigest()
    verify = tokens.find_one({"token": token})
    if verify:
        return verify["username"]
    else:
        return None


def auth_users(username, password):
    user = users.find_one({'username': username})
    if user:
        return bcrypt.checkpw(password.encode(), user['password'])
    else:
        return False


