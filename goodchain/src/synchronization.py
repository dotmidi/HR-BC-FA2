import socket
import threading
import os
import json
import pickle
from helperFunctions import *
from dataStructures import Tx, TxBlock

connected_users_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'connected_users.json')


class ListeningThread:
    STOP_MESSAGE = b'STOP_LISTENING'
    SAME_USER_MESSAGE = b'SAME_USER'

    def __init__(self, host, port, other_port):
        self.host = host
        self.port = port
        self.other_port = other_port
        self.connection = None
        self.user_file = connected_users_path
        self.lock = threading.Lock()
        self.server_thread = None
        self.username = None

        if not os.path.exists(os.path.dirname(self.user_file)):
            os.makedirs(os.path.dirname(self.user_file))

        if not os.path.exists(self.user_file):
            with open(self.user_file, 'w') as f:
                json.dump({}, f)

    def start_listening(self, username):
        self.username = username
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
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Received connection")
                        print('Connected by', addr)
                        while True:
                            data = conn.recv(8192)

                            if not data:
                                break

                            print(f"Received data size: {len(data)}")

                            if data == self.SAME_USER_MESSAGE:
                                print("Cannot connect to yourself. Exiting...")
                                exit()
                                break

                            if data[:18] == b'CREATE_TRANSACTION':
                                transaction = pickle.loads(data[18:])
                                print(f"Received transaction")
                                if Tx.is_valid(transaction):
                                    print("Transaction is valid")
                                    with open(pool_path, 'rb') as pool_file:
                                        pool = pickle.load(pool_file)
                                        pool.append(transaction)

                                    with open(pool_path, 'wb') as pool_file:
                                        pickle.dump(pool, pool_file)

                                    print("Transaction added to the pool")
                                else:
                                    print(
                                        "Transaction is invalid, discarding transaction")

                            elif data[:16] == b'EDIT_TRANSACTION':
                                transaction = pickle.loads(data[16:])
                                print(f"Received edit transaction")
                                if Tx.is_valid(transaction):
                                    print("Transaction is valid")

                                    with open(pool_path, 'rb') as pool_file:
                                        pool = pickle.load(pool_file)
                                        for i in range(len(pool)):
                                            if pool[i].id == transaction.id:
                                                pool[i] = transaction

                                    with open(pool_path, 'wb') as pool_file:
                                        pickle.dump(pool, pool_file)

                                    print("Transaction edited in the pool")
                                else:
                                    print(
                                        "Transaction is invalid, discarding transaction")

                            elif data[:18] == b'CANCEL_TRANSACTION':
                                transaction = pickle.loads(data[18:])
                                print(f"Received cancel transaction")
                                if Tx.is_valid(transaction):
                                    with open(pool_path, 'rb') as pool_file:
                                        pool = pickle.load(pool_file)
                                        for i in range(len(pool)):
                                            if pool[i].id == transaction.id:
                                                pool.pop(i)
                                                break

                                    with open(pool_path, 'wb') as pool_file:
                                        pickle.dump(pool, pool_file)

                                    print("Transaction removed from the pool")
                                else:
                                    print(
                                        "Transaction is invalid, discarding transaction")

                            elif data[:7] == b'TXBLOCK':
                                # CODE HERE TO STOP THE ONGOING MINING THREAD MAYBE XD IM GOIG INSANE
                                pool_header_index = data.find(b'POOL')
                                block = pickle.loads(data[7:pool_header_index])
                                pool = pickle.loads(
                                    data[pool_header_index + 4:])
                                print(f"Received block: {block}")
                                if TxBlock.is_valid(block):
                                    print("Block is valid")
                                    for transaction in pool:
                                        if not Tx.is_valid(transaction):
                                            print("Pool is invalid")
                                    print("Pool is valid")

                                    with open(pool_path, 'wb') as pool_file:
                                        pickle.dump(pool, pool_file)

                                    with open(ledger_path, 'rb') as ledger_file:
                                        ledger = pickle.load(ledger_file)
                                        ledger.append(block)

                                    with open(ledger_path, 'wb') as ledger_file:
                                        pickle.dump(ledger, ledger_file)

                                    print("Block added to the ledger")
                                else:
                                    print("Block is invalid, discarding block")

                            elif data[:4] == b'POOL':
                                pool = pickle.loads(data[4:])
                                print(f"Received pool: {pool}")
                                for transaction in pool:
                                    if not Tx.is_valid(transaction):
                                        print("Pool is invalid")
                                print("Pool is valid")
                                with open(pool_path, 'rb') as pool_file:
                                    local_pool = pickle.load(pool_file)
                                    if len(pool) > len(local_pool):
                                        with open(pool_path, 'wb') as pool_file:
                                            pickle.dump(pool, pool_file)
                                        print("Pool updated")
                                    else:
                                        print("Pool not updated")

                            elif data[:6] == b'LEDGER':
                                pool_header_index = data.find(b'POOL')
                                ledger = pickle.loads(
                                    data[6:pool_header_index])
                                pool = pickle.loads(
                                    data[pool_header_index + 4:])
                                print(
                                    f"Received ledger with size: {len(ledger)}")
                                print(f"Received pool with size: {len(pool)}")
                                for block in ledger:
                                    if not TxBlock.is_valid(block):
                                        print("Ledger is invalid")
                                print("Ledger is valid")
                                with open(ledger_path, 'rb') as ledger_file:
                                    local_ledger = pickle.load(ledger_file)
                                    if len(ledger) > len(local_ledger):
                                        with open(ledger_path, 'wb') as ledger_file:
                                            pickle.dump(ledger, ledger_file)
                                        print("Ledger updated")
                                    else:
                                        print(
                                            "Ledger not updated, no new blocks received.")
                                for transaction in pool:
                                    if not Tx.is_valid(transaction):
                                        print("Pool is invalid")
                                print("Pool is valid")
                                with open(pool_path, 'rb') as pool_file:
                                    local_pool = pickle.load(pool_file)
                                    if len(pool) > len(local_pool):
                                        with open(pool_path, 'wb') as pool_file:
                                            pickle.dump(pool, pool_file)
                                        print("Pool updated")
                                    else:
                                        print(
                                            "Pool not updated, no new transactions received.")
                                print("Sync complete.")

                            elif data[:9] == b'HANDSHAKE':
                                other_username = data[9:].decode()
                                if other_username == self.username:
                                    os.system('cls' if os.name ==
                                              'nt' else 'clear')
                                    print(
                                        "Cannot connect to yourself. Exiting...")
                                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                        s.connect((self.host, self.other_port))
                                        s.sendall(self.SAME_USER_MESSAGE)
                                    exit()
                                    break
                                print(f"Connected to user: {other_username}")

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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.host, self.other_port))
                s.sendall(message.encode())
                print(f"Sent message: {message}")
            except ConnectionRefusedError:
                print(
                    "Connection refused. Unable to send message, please attempt to sync later.")

    def send_transaction(self, transaction):
        try:
            header = b'CREATE_TRANSACTION'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(transaction))
                print(f"Sent transaction: {transaction}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send transaction, please attempt to sync later.")

    def send_edit_transaction(self, transaction):
        try:
            header = b'EDIT_TRANSACTION'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(transaction))
                print(f"Sent edit transaction: {transaction}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send edit transaction, please attempt to sync later.")

    def send_cancel_transaction(self, transaction):
        try:
            header = b'CANCEL_TRANSACTION'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(transaction))
                print(f"Sent cancel transaction: {transaction}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send cancel transaction, please attempt to sync later.")

    def send_block(self, block, pool):
        try:
            header = b'TXBLOCK'
            pool_header = b'POOL'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(block) +
                          pool_header + pickle.dumps(pool))
                print(f"Sent block: {block}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send block, please attempt to sync later.")

    def send_pool(self, pool):
        try:
            header = b'POOL'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(pool))
                print(f"Sent pool: {pool}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send pool, please attempt to sync later.")

    def send_ledger(self, ledger):
        try:
            header = b'LEDGER'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(ledger))
                print(f"Sent ledger: {ledger}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send ledger, please attempt to sync later.")

    def sync_pool_ledger(self):
        try:
            header = b'HANDSHAKE'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + self.username.encode())
                print(f"Sent handshake message")

            ledger = []
            pool = []
            with open(ledger_path, 'rb') as ledger_file:
                ledger = pickle.load(ledger_file)

            with open(pool_path, 'rb') as pool_file:
                pool = pickle.load(pool_file)

            ledger_header = b'LEDGER'
            pool_header = b'POOL'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                # print the size of the data being sent
                print(f"Sending ledger size: {len(pickle.dumps(ledger))}")
                print(f"Sending pool size: {len(pickle.dumps(pool))}")
                print(
                    f"Total size: {len(pickle.dumps(ledger)) + len(pickle.dumps(pool))}")
                s.sendall(ledger_header + pickle.dumps(ledger) +
                          pool_header + pickle.dumps(pool))
                # print(f"Sent ledger: {ledger}")
                # print(f"Sent pool: {pool}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to sync pool and ledger, please attempt to sync later.")

    def request_sync(self):
        try:
            header = b'SYNC_REQUEST'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header)
                print(f"Sent sync request")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to request sync, please attempt to sync later.")