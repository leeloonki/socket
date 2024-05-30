import socket
import multiprocessing
import json
import time


class Server(multiprocessing.Process):
    def __init__(self, server_id, host, port):
        super().__init__()
        self.server_id = server_id
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.connections = {}
        self.received_data = []
        self.running = True

    def run(self):
        print(f"Server {self.server_id} is listening on port {self.port}")
        self.accept_connections()

    def accept_connections(self):
        while self.running:
            try:
                self.server_socket.settimeout(1)
                conn, addr = self.server_socket.accept()
                self.connections[addr] = conn
                print(f"Server {self.server_id} accepted connection from {addr}")
                multiprocessing.Process(target=self.handle_connection, args=(conn,)).start()
            except socket.timeout:
                continue

    def handle_connection(self, conn):
        while self.running:
            try:
                conn.settimeout(1)
                data = conn.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode('utf-8'))
                print(f"Server {self.server_id} received: {message}")
                self.received_data.append(message['data'])
                self.process_data()
            except socket.timeout:
                continue
        conn.close()

    def process_data(self):
        if self.received_data:
            result = sum(self.received_data)  # Example computation: summing the received data
            print(f"Server {self.server_id} computed result: {result}")

    def connect_to_server(self, host, port, target_server_id):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        self.connections[target_server_id] = client_socket
        print(f"Server {self.server_id} connected to server {target_server_id} at {host}:{port}")

    def send_message(self, to, data):
        msg = json.dumps({'from': f'server{self.server_id}', 'to': to, 'data': data}).encode('utf-8')
        if to in self.connections:
            self.connections[to].send(msg)
        else:
            print(f"Connection to server {to} not found")

    def close(self):
        self.running = False
        self.server_socket.close()
        for conn in self.connections.values():
            conn.close()


def main():
    server0 = Server(0, 'localhost', 800)
    server1 = Server(1, 'localhost', 801)
    server2 = Server(2, 'localhost', 802)

    server0.start()
    server1.start()
    server2.start()

    time.sleep(1)

    server2.connect_to_server('localhost', 800, 0)
    server2.connect_to_server('localhost', 801, 1)

    time.sleep(1)

    # server2 sends data to server0 and server1
    server2.send_message(0, 10)
    server2.send_message(1, 20)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        server0.close()
        server1.close()
        server2.close()


if __name__ == '__main__':
    main()
