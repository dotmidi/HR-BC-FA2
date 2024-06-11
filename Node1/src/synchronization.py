import socket
import threading
import os
import json
import pickle
from helperFunctions import *
from dataStructures import *

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
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Received connection")
                        print('Connected by', addr)
                        while True:
                            data = conn.recv(8192)
                            # if the header is header = b'TRANSACTION', then it is a transaction
                            # print the size of the data received
                            print(f"Received data size: {len(data)}")
                            if data[:11] == b'TRANSACTION':
                                transaction = pickle.loads(data[11:])
                                print(f"Received transaction")
                                # validate the transaction
                                if Tx.is_valid(transaction):
                                    print("Transaction is valid")
                                    # open the transaction pool file and append the transaction to it
                                    with open(pool_path, 'rb') as pool_file:
                                        pool = pickle.load(pool_file)
                                        pool.append(transaction)

                                    with open(pool_path, 'wb') as pool_file:
                                        pickle.dump(pool, pool_file)

                                    print("Transaction added to the pool")
                                    # go back to the main menu but keep the connection open
                                    print()
                                    input(
                                        "Press Enter to return to the main menu...")
                                else:
                                    print(
                                        "Transaction is invalid, discarding transaction")
                                    print()
                                    input("Press Enter to continue...")
                            # if the header is head = b'TXBLOCK', then it is a block
                            elif data[:7] == b'TXBLOCK':
                                block = pickle.loads(data[7:])
                                print(f"Received block: {block}")
                                # validate the block
                                if TxBlock.is_valid(block):
                                    print("Block is valid")
                                    # open the ledger file and append the block to it
                                    # with open(ledger_path, 'rb') as ledger_file:
                                    #     ledger = pickle.load(ledger_file)
                                    #     ledger.append(block)

                                    # with open(ledger_path, 'wb') as ledger_file:
                                    #     pickle.dump(ledger, ledger_file)

                                    print("Block added to the ledger")
                                    # go back to the main menu but keep the connection open
                                    print()
                                    input(
                                        "Press Enter to return to the main menu...")
                                else:
                                    print("Block is invalid, discarding block")
                                    print()
                                    input("Press Enter to continue...")
                            # if the header is header = b'POOL', then it is a pool
                            elif data[:4] == b'POOL':
                                pool = pickle.loads(data[4:])
                                print(f"Received pool: {pool}")
                                # validate the pool
                                for transaction in pool:
                                    if not Tx.is_valid(transaction):
                                        print("Pool is invalid")
                                print("Pool is valid")
                            # if the header is header = b'LEDGER', then it is a ledger. There is also a pool header after the ledger, split them
                            elif data[:6] == b'LEDGER':
                                # find the start of the pool header
                                pool_header_index = data.find(b'POOL')
                                ledger = pickle.loads(
                                    data[6:pool_header_index])
                                pool = pickle.loads(
                                    data[pool_header_index + 4:])
                                print(f"Received ledger: {ledger}")
                                print(f"Received pool: {pool}")
                                # validate the ledger
                                for block in ledger:
                                    if not TxBlock.is_valid(block):
                                        print("Ledger is invalid")
                                print("Ledger is valid")
                                # check the difference between the ledger on the ledger_path and the received ledger
                                # if the received ledger is longer, then replace the ledger on the ledger_path with the received ledger
                                with open(ledger_path, 'rb') as ledger_file:
                                    local_ledger = pickle.load(ledger_file)
                                    if len(ledger) > len(local_ledger):
                                        with open(ledger_path, 'wb') as ledger_file:
                                            pickle.dump(ledger, ledger_file)
                                        print("Ledger updated")
                                    else:
                                        print("Ledger not updated")
                                # validate the pool
                                for transaction in pool:
                                    if not Tx.is_valid(transaction):
                                        print("Pool is invalid")
                                print("Pool is valid")
                                # check the difference between the pool on the pool_path and the received pool
                                # if the received pool is longer, then replace the pool on the pool_path with the received pool
                                with open(pool_path, 'rb') as pool_file:
                                    local_pool = pickle.load(pool_file)
                                    if len(pool) > len(local_pool):
                                        with open(pool_path, 'wb') as pool_file:
                                            pickle.dump(pool, pool_file)
                                        print("Pool updated")
                                    else:
                                        print("Pool not updated")
                                print("Sync complete.")
                            if not data:
                                break
                            # print('Received data')
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

    def send_transaction(self, transaction):
        header = b'TRANSACTION'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.other_port))
            s.sendall(header + pickle.dumps(transaction))
            print(f"Sent transaction: {transaction}")

    def send_block(self, block):
        header = b'TXBLOCK'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.other_port))
            s.sendall(header + pickle.dumps(block))
            print(f"Sent block: {block}")

    def send_pool(self, pool):
        header = b'POOL'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.other_port))
            s.sendall(header + pickle.dumps(pool))
            print(f"Sent pool: {pool}")

    def send_ledger(self, ledger):
        header = b'LEDGER'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.other_port))
            s.sendall(header + pickle.dumps(ledger))
            print(f"Sent ledger: {ledger}")

    def sync_pool_ledger(self):
        # send in a single message, first the ledger and then the pool. should be separated by a delimiter
        # get the ledger and pool
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
            print(f"Sent ledger: {ledger}")
            print(f"Sent pool: {pool}")
