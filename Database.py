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

def add_chat(chat):
    data = self.request.recv(1024).strip()
    for byte in data:
        print(bin(byte))
    mask = data[2:6]
    payloadData = data[6:]
    print("passed5")
    wow = []

    for x in range(len(payloadData)):
        data2 = payloadData[x] ^ mask[x % 4]
        wow.append(data2)
    maskedPayLoad = bytearray(wow)

    dictPayLoad = json.loads(maskedPayLoad.decode())
    mydb.messages.insert_one(dictPayLoad)


def display_chat():
    for msg in mydb.messages.find():
        print(f'Message: {msg}')
        # Send msg to the client over websocket
        del msg['_id']
        jsonMsg = json.dumps(msg)  # msg is a python dict
        frame = bytearray([129, len(jsonMsg)]) + jsonMsg.encode()
        print(f'Frame: {frame}')
        self.request.sendall(frame)


