import socketserver
import sys
import time

class MyTCPHandler(socketserver.BaseRequestHandler):
    clients = []

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

        temp = recieved_data.decode().split("\r\n")
        temp = temp[0].split()

        if temp[1] == "/":
            content = open("Homescreen.html", mode="r", encoding="utf-8")
            content = content.read()
            length = str(len(content.encode("utf-8")))
            self.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: " + length + "\r\nContent-Type: text/html; charset=utf-8; X-Content-Type-Options=nosniff\r\n\r\n" + content).encode())




if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000

    server = socketserver.TCPServer((host, port), MyTCPHandler)
    server.serve_forever()
