import socketserver
import sys
import time
import json
import Database


class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []
    websocket = False
    def handle(self):
        recieved_data = self.request.recv(1024)

        client_id = self.client_address[0] + ":" + str(self.client_address[1])
        print(client_id + " is sending data:")
        print(recieved_data.decode())

        self.clients.append(client_id)
        print(self.clients)

        print("\n\n")
        sys.stdout.flush()
        sys.stderr.flush()

        time.sleep(0)

        data = recieved_data.decode().split("\r\n")
        temp = data[0].split()

        if temp[0] == "GET":
            if temp[1] == "/":
                content = open("Homescreen.html", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
            elif temp[1] == "/server.js":
                content = open("server.js", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/javascript; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
            elif temp[1] == "/registration":
                content = open("Account_Registration.html", mode="r", encoding="utf-8")
                content = content.read()
                length = str(len(content.encode("utf-8")))
                self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())
        elif temp[0] == "POST":
            if temp[1] == "/registered":
                user_info = json.loads(data[len(data)-1])
                username = user_info['username']
                password = user_info['password']
                print(username, password)
                Database.add_users(username, password)
                self.request.sendall("HTTP/1.1 302 Moved Permanently\r\nContent-Length: 0\r\nLocation: \\ \r\n\r\n".encode())


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.TCPServer((host, port), MyTCPHandler)
    server.serve_forever()
