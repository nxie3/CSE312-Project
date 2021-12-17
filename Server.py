import socketserver
import sys
import time
import secrets
import Database
import json
import hashlib
import base64
from socketserver import ThreadingTCPServer

socketserver.TCPServer.allow_reuse_address = True


class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    pLI = {}
    client_sockets = []
    websocket = False
    cookie = [""]

    def handle(self):
        recieved_data = self.request.recv(1024)
        client_id = self.client_address[0] + ":" + str(self.client_address[1])
        self.clients.append(client_id)
        data = recieved_data.decode().split("\r\n")
        temp = data[0].split()
        database2 = {}
        for e in data:
            splite = e.split(": ", 1)
            if len(splite) > 1:
                v = splite[1]
                i = splite[0]
                database2[i] = v
            else:
                database2[e] = "single"
        print(database2)


        length = ""
        for x in data:
            if x.find("Content-Length") != -1:
                length = x.split(":")[1]
                break
        if length != "":
            repeat = int(int(length) / 1024) + (int(length) % 1024 > 0)
            while repeat != 0:
                body = self.request.recv(1024)
                recieved_data += body
                repeat -= 1



        print("\n\n")
        #sys.stdout.flush()
        #sys.stderr.flush()

        #time.sleep(0)

        if temp[0] == "GET":
            print("New GET")
            if temp[1] == "/":
                cookie_id = secrets.token_urlsafe(16)
                cookie_data = find_cookie(data)
                if cookie_data is not None:
                    cookie_id = cookie_data
                self.cookie[0] = cookie_id
                username = Database.find_logged(self.cookie[0])
                if username is not None:
                    gen_homescreen(True, username)
                else:
                    gen_homescreen(False, "")
                content = open("Homescreen.html", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\nSet-Cookie: id=" + cookie_id + "; Max-Age=3600;\r\n\r\n" + content).encode())
            elif temp[1] == "/functions.js":
                content = open("functions.js", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/javascript; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
            elif temp[1] == "/websocket":
                # check that the user is logged in either by directly querying login db
                # or check the auth token cookie.
                # then and only then will you handle the websocket connection.
                print("Handling /websocket")
                self.handle_websocket(database2)
            elif temp[1] == "/registration":
                content = open("Account_Registration.html", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
            elif temp[1] == "/login":
                content = open("Login_Page.html", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
            elif temp[1] == "/reg_status":
                content = open("Registration_Status.html", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
            elif temp[1] == "/log_status":
                content = open("Login_Status.html", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
        elif temp[0] == "POST":
            if temp[1] == "/logged":
                parsed_bytes = recieved_data.split(b"\r\n\r\n")
                username = parsed_bytes[2].split(b"\r\n------")[0].decode()
                password = parsed_bytes[3].split(b"\r\n------")[0].decode()
                result = Database.auth_users(username, password)
                if result:
                    Database.login_token(username, self.cookie[0])
                    html = open("Login_Status.html", mode="w")
                    content = "<html lang=\"en\">\n<head>\n\t<title>CSE312 Project Login Status</title>\n</head>\n<h1>Login Successful! Return to Homepage to Start Typing!</h1>\n<p>\n\t<input type=\"submit\" value=\"Homepage\" onclick=\"window.location=\'/\';\"/>\n</p>\n</html>"
                    html.write(content)
                    html.close()
                else:
                    html = open("Login_Status.html", mode="w")
                    content = "<html lang=\"en\">\n<head>\n\t<title>CSE312 Project Registration Status</title>\n</head>\n<h1>Login Failed! Incorrect Password Return to Login!</h1>\n<p>\n\t<input type=\"submit\" value=\"Login\" onclick=\"window.location=\'/login\';\"/>\n</p>\n</html>"
                    html.write(content)
                    html.close()
                self.request.sendall("HTTP/1.1 302 Moved Permanently\r\nContent-Length: 0\r\nLocation: log_status \r\n\r\n".encode())
            elif temp[1] == "/registered":
                parsed_bytes = recieved_data.split(b"\r\n\r\n")
                username = parsed_bytes[2].split(b"\r\n------")[0].decode()
                password = parsed_bytes[3].split(b"\r\n------")[0].decode()
                image = parsed_bytes[4].split(b"\r\n------")[0]
                if ((len(password) >= 8) and (check_digit(password)) and (check_special(password)) and (password.lower() != password) and (password.upper() != password)) and len(username) != 0 and len(image) != 0:
                    if Database.existing_user(username):
                        html = open("Registration_Status.html", mode="w")
                        content = "<html lang=\"en\">\n<head>\n\t<title>CSE312 Project Registration Status</title>\n</head>\n<h1>Registration Failed, Username Already Taken! Return to Registration.</h1>\n<p>\n\t<input type=\"submit\" value=\"Register\" onclick=\"window.location=\'/registration\';\"/>\n</p>\n</html>"
                        html.write(content)
                        html.close()
                    else:
                        html = open("Registration_Status.html", mode="w")
                        content = "<html lang=\"en\">\n<head>\n\t<title>CSE312 Project Registration Status</title>\n</head>\n<h1>Registration Successful! Return to Homepage or Proceed to Login.</h1>\n<p>\n\t<input type=\"submit\" value=\"Login\" onclick=\"window.location=\'/login\';\"/>\n\t<input type=\"submit\" value=\"Homepage\" onclick=\"window.location=\'/\';\"/>\n</p>\n</html>"
                        html.write(content)
                        html.close()
                        Database.add_users(username, password, image)
                else:
                    html = open("Registration_Status.html", mode="w")
                    content = "<html lang=\"en\">\n<head>\n\t<title>CSE312 Project Registration Status</title>\n</head>\n<h1>Registration Failed, Missing or Invalid Elements! Return to Registration.</h1>\n<p>\n\t<input type=\"submit\" value=\"Register\" onclick=\"window.location=\'/registration\';\"/>\n</p>\n</html>"
                    html.write(content)
                    html.close()
                self.request.sendall("HTTP/1.1 302 Moved Permanently\r\nContent-Length: 0\r\nLocation: reg_status \r\n\r\n".encode())
            elif temp[1] == "/chat":
                print("passed")
                chat_info = json.loads(data[len(data) - 1])
                chat = chat_info["chat"]
                print("chat has been retrieved!")
                print(chat)
                mydb.messages.insert_one(chat)
                print("inserted into db")



    def handle_websocket(self, database2):
        if "Sec-WebSocket-Key" in database2:
            print("passed2")
            if database2.get("Sec-WebSocket-Key") != "None":
                wKey = database2.get("Sec-WebSocket-Key")
                print("passed3")
                print(wKey)
                wKey += "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                print("passed4")
                print(wKey)
                wKeys = wKey.encode("utf-8")
                hashKey = hashlib.sha1(wKeys)
                hexKey = hashKey.digest()
                #hexKeys = hexKey.encode("utf-8")
                b64Key = base64.standard_b64encode(hexKey)
                print(f"b64Key={b64Key}")
                headers3 = "HTTP/1.1 101 Switching Protocols\r\n" + \
                           '''Connection: Upgrade\r\n'''+ \
                           '''Upgrade: websocket\r\n''' + \
                           '''Sec-WebSocket-Accept: %s'''
                headers4 = headers3.encode("utf-8")
                ending = ('''\r\n\r\n''').encode("utf-8")
                headers4 = headers4%(b64Key)+ending
                # print("didnt Forget")
                # print(headers4.decode())
                # print(b64Key)
                # End of websocket handshake
                print("before sending handshake")
                print(f"sending headers4={headers4}")
                self.request.sendall(headers4)

                """
                print('Creating mongo client')
                myclient = pymongo.MongoClient("mongodb://mongo:27017/")
                mydb = myclient["chatDB"]
                print('Created mongo client')
                for msg in mydb.messages.find():
                    print(f'Message: {msg}')
                    # Send msg to the client over websocket
                    del msg['_id']
                    jsonMsg = json.dumps(msg) # msg is a python dict
                    frame = bytearray([129, len(jsonMsg)]) + jsonMsg.encode()
                    print(f'Frame: {frame}')
                    self.request.sendall(frame)
                """

                MyTCPHandler.client_sockets.append(self.request)

                # Start processing incoming messages
                while True:
                    data = self.request.recv(1024).strip()
                    for byte in data:
                        print(bin(byte))
                    mask = data[2:6]
                    payloadData = data[6:]
                    print("passed5")
                    wow = []

                    for x in range(len(payloadData)):
                        data2 = payloadData[x] ^ mask[x%4]
                        wow.append(data2)
                    maskedPayLoad = bytearray(wow)

                    dictPayLoad = json.loads(maskedPayLoad.decode())
                    print(f"dictPayLoad={dictPayLoad}")
                    # mydb.messages.insert_one(dictPayLoad)

                    for client in MyTCPHandler.client_sockets:
                        jsonMsg = json.dumps(dictPayLoad)
                        frame = bytearray([129, len(jsonMsg)]) + jsonMsg.encode()
                        client.sendall(frame)


def check_digit(password):
    for x in password:
        if x.isdigit():
            return True
    return False


def check_special(password):
    for y in password:
        if 32 <= ord(y) <= 47:
            return True
        elif 58 <= ord(y) <= 64:
            return True
        elif 91 <= ord(y) <= 96:
            return True
        elif 123 <= ord(y) <= 126:
            return True
    return False


def find_cookie(data):
    cookie_data = None
    for x in data:
        if x.find('Cookie:') != -1:
            cookie_data = x
            break
    if cookie_data is not None:
        cookie_data = cookie_data.split(':')[1]
        if cookie_data.find(';') != -1:
            cookie_data = cookie_data.split(';')
            for y in cookie_data:
                if y.find('id=') != -1:
                    cookie_data = y
                    cookie_data = cookie_data.split('=')[1]
                    return cookie_data
    return None


def gen_homescreen(user_exists, username):
    if user_exists:
        content1 = open("Homescreen_Template1.txt", mode="r", encoding="utf-8").read()
        content2 = open("Homescreen_Template2.txt", mode="r", encoding="utf-8").read()
        content = content1 + "Logged in as: " + username + content2
        html = open("Homescreen.html", mode="w")
        html.write(content)
        html.close()
    else:
        content1 = open("Homescreen_Template1.txt", mode="r", encoding="utf-8").read()
        content2 = open("Homescreen_Template2.txt", mode="r", encoding="utf-8").read()
        buttons = open("Buttons.txt", mode="r", encoding="utf-8").read()
        content = content1 + buttons + content2
        html = open("Homescreen.html", mode="w")
        html.write(content)
        html.close()


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    #server = socketserver.TCPServer((host, port), MyTCPHandler)
    server = ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()
