import socket
import threading
import os
import json
from helperFunctions import *

connected_users_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'connected_users.json')


class Synchronization:
    STOP_MESSAGE = b'STOP_LISTENING'  # Special message to signal the listener to stop

    def __init__(self, host, port, other_port):
        self.host = host
        self.port = port
        self.other_port = other_port
        self.connection = None
        self.user_file = connected_users_path
        self.lock = threading.Lock()  # Lock for thread-safe file access
        self.server_thread = None  # Store reference to the server thread

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
        self.server_thread.join()  # Wait for the thread to stop
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
            self._allocate_user(username)  # Allocate user to the new port
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
                    pass  # Handle OSError, e.g., when socket is closed

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
