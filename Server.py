import socketserver
import sys
import time
import secrets
import Database


class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    websocket = False
    cookie = [""]

    def handle(self):
        recieved_data = self.request.recv(1024)
        data = recieved_data.decode().split("\r\n")
        temp = data[0].split()
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

        client_id = self.client_address[0] + ":" + str(self.client_address[1])
        print(client_id + " is sending data:")
        print(recieved_data)

        self.clients.append(client_id)
        print(self.clients)

        print("\n\n")
        sys.stdout.flush()
        sys.stderr.flush()

        time.sleep(0)

        if temp[0] == "GET":
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

    server = socketserver.TCPServer((host, port), MyTCPHandler)
    server.serve_forever()
