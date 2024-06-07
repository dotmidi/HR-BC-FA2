import socket
import threading
import os
import json
from helperFunctions import *

connected_users_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'connected_users.json')


class ListeningThread:
    STOP_MESSAGE = b'STOP_LISTENING'

    def __init__(self, host, port, other_port):
        self.host = host
        self.port = port
        self.other_port = other_port
        self.connection = None
        self.user_file = connected_users_path
        self.lock = threading.Lock()
        self.server_thread = None

        if not os.path.exists(os.path.dirname(self.user_file)):
            os.makedirs(os.path.dirname(self.user_file))

        if not os.path.exists(self.user_file):
            with open(self.user_file, 'w') as f:
                json.dump({}, f)

    def start_listening(self, username):
        if self._allocate_user(username):
            self.server_thread = threading.Thread(
                target=self._listen, name="listen_thread", args=(username,))
            self.server_thread.start()
        else:
            print(
                f"User '{username}' is already allocated a listening server.")
            exit()

    def stop_listening(self, username):
        self._remove_user(username)
        self.send_stop_message()
        self.server_thread.join()
        print(f"User '{username}' stopped listening.")
        input("Press Enter to continue...")

    def _listen(self, username):
        try:
            self._connect()
            print(f"User '{username}' connected to node 1.")
        except OSError:
            print(
                f"User '{username}' failed to connect to node 1. Trying node 2...")
            self.port, self.other_port = self.other_port, self.port
            self._allocate_user(username)
            self._connect()
            print(f"User '{username}' connected to node 2.")

    def _connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print(f"Connected to port {self.port}")
            s.listen()
            while True:
                try:
                    conn, addr = s.accept()
                    with conn:
                        print('Connected by', addr)
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                break
                            print('Received', repr(data))
                            if data == self.STOP_MESSAGE:
                                print('Stop message received. Stopping listener.')
                                return
                            conn.sendall(data)
                except OSError:
                    pass

    def send_stop_message(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(self.STOP_MESSAGE)

    def _allocate_user(self, username):
        with self.lock:
            users = self._read_users()
            if username not in users:
                users[username] = self.port
                self._write_users(users)
                return True
            return False

    def _is_user_allowed(self, username):
        with self.lock:
            users = self._read_users()
            return users.get(username) == self.port

    def _read_users(self):
        with open(self.user_file, 'r') as f:
            return json.load(f)

    def _write_users(self, users):
        with open(self.user_file, 'w') as f:
            json.dump(users, f)

    def _remove_user(self, username):
        with self.lock:
            users = self._read_users()
            users.pop(username, None)
            self._write_users(users)

    def send_message(self, message):
        # look at the current user's port and send the message to the other port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.other_port))
            s.sendall(message.encode())
            print(f"Sent message: {message}")

# class Synchronization:
#     def sync_on_demand(self, host, port, other_port, username, ledger, pool):
#         listening_thread = ListeningThread(host, port, other_port)
#         listening_thread.start_listening(username)
#         self.sync(ledger, pool, host, other_port)  # Assume the other node is listening on other_port
#         listening_thread.stop_listening(username)

#     def sync(self, ledger, pool, host, port):
#         try:
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                 s.connect((host, port))
#                 print(f"Connected to {host}:{port} for synchronization")

#                 # Send local ledger and pool to the other node
#                 self._send_file(s, ledger)
#                 self._send_file(s, pool)

#                 # Receive ledger and pool from the other node
#                 received_ledger = self._receive_file(s, ledger)
#                 received_pool = self._receive_file(s, pool)

#                 # Validate received ledger and pool
#                 if self._validate(received_ledger, received_pool):
#                     # Update local ledger and pool
#                     self._update_file(ledger, received_ledger)
#                     self._update_file(pool, received_pool)
#                     print("Synchronization complete and data updated.")
#                 else:
#                     print("Received data is invalid. Synchronization aborted.")

#         except ConnectionRefusedError:
#             print(f"Failed to connect to {host}:{port} for synchronization")

#     def _send_file(self, socket, file_path):
#         with open(file_path, 'rb') as f:
#             data = f.read()
#             file_size = len(data)
#             socket.sendall(file_size.to_bytes(8, 'big'))  # Send file size
#             socket.sendall(data)  # Send file data
#         print(f"Sent {file_path}")

#     def _receive_file(self, socket, file_path):
#         file_size = int.from_bytes(socket.recv(8), 'big')  # Receive file size
#         received_data = b''
#         while len(received_data) < file_size:
#             packet = socket.recv(1024)
#             if not packet:
#                 break
#             received_data += packet

#         with open(file_path, 'wb') as f:
#             f.write(received_data)
#         print(f"Received {file_path}")
#         return received_data

#     def _validate(self, ledger_data, pool_data):
#         return True

#     def _update_file(self, file_path, data):
#         with open(file_path, 'wb') as f:
#             f.write(data)
#         print(f"Updated {file_path}")
