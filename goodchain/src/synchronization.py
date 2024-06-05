import socket
import threading

class Synchronization:
    def __init__(self, host, port, other_port):
        self.host = host
        self.port = port
        self.other_port = other_port
        self.connection = None

    def start_listening(self):
        self.server_thread = threading.Thread(target=self._listen)
        self.server_thread.start()

    def _listen(self):
        try:
            self._connect()
            print("Connected to node 1.")
        except OSError:
            print("Failed to connect to node 1. Trying node 2...")
            self.port, self.other_port = self.other_port, self.port
            self._connect()
            print("Connected to node 2.")

    def _connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print('Received', repr(data))
                    conn.sendall(data)

    def send(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.other_port))
            s.sendall(data)
            data = s.recv(1024)
        print('Received', repr(data))

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print('Received', repr(data))
                    conn.sendall(data)
