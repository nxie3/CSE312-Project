import hashlib

from pymongo import MongoClient
import bcrypt

mongo_client = MongoClient('mongo')
db = mongo_client["login_database"]

users = db["user_list"]
tokens = db["token_list"]


def add_users(username, password, profile_picture):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed, "picture": profile_picture})


def login_token(username, cookie):
    token = cookie
    #token = hashlib.sha256(cookie.encode()).hexdigest()
    tokens.find_one_and_delete({"username": username})
    tokens.insert_one({"token": token, "username": username})


def existing_user(username):
    verify = users.find_one({"username": username})
    if verify:
        return True
    else:
        return False


def find_logged(cookie):
    #token = hashlib.sha256(cookie.encode()).hexdigest()
    token = cookie
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


