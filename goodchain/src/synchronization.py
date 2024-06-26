import socket
import threading
import os
import json
import pickle
import sqlite3
from dataStructures import Tx, TxBlock

connected_users_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'connected_users.json')

database_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'goodchain.db')

ledger_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'ledger.dat')

pool_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'pool.dat')

hash_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'hash.dat')

notifications_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'notifications.dat')

user_database_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'goodchain.db')


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
                            data = conn.recv(16384)
                            # print(f"Received data: {data}")

                            if not data:
                                break

                            # print(f"Received data size: {len(data)}")

                            if data == self.SAME_USER_MESSAGE:
                                print("Cannot connect to yourself. Exiting...")
                                exit()
                                break

                            if data[:18] == b'CREATE_TRANSACTION':
                                notification_header_index = data.find(
                                    b'NOTIFICATIONS')
                                transaction = pickle.loads(
                                    data[18:notification_header_index])
                                notification = pickle.loads(
                                    data[notification_header_index + 13:])
                                print(f"Received transaction")
                                if Tx.is_valid(transaction):
                                    print("Transaction is valid")
                                    with open(pool_path, 'rb') as pool_file:
                                        pool = pickle.load(pool_file)
                                        pool.append(transaction)

                                    with open(pool_path, 'wb') as pool_file:
                                        pickle.dump(pool, pool_file)

                                    print("Transaction added to the pool")

                                    with open(notifications_path, 'rb') as notifications_file:
                                        local_notifications = pickle.load(
                                            notifications_file)
                                        local_notifications.append(
                                            notification)
                                    with open(notifications_path, 'wb') as notifications_file:
                                        pickle.dump(
                                            local_notifications, notifications_file)
                                    print("Notification added.")
                                else:
                                    print(
                                        "Transaction is invalid, discarding transaction")

                            elif data[:16] == b'EDIT_TRANSACTION':
                                notification_header_index = data.find(
                                    b'NOTIFICATIONS')
                                transaction = pickle.loads(
                                    data[16:notification_header_index])
                                notification = pickle.loads(
                                    data[notification_header_index + 13:])
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

                                    with open(notifications_path, 'rb') as notifications_file:
                                        local_notifications = pickle.load(
                                            notifications_file)
                                        local_notifications.append(
                                            notification)
                                    with open(notifications_path, 'wb') as notifications_file:
                                        pickle.dump(
                                            local_notifications, notifications_file)
                                    print("Notification added.")
                                else:
                                    print(
                                        "Transaction is invalid, discarding transaction")

                            elif data[:18] == b'CANCEL_TRANSACTION':
                                notification_header_index = data.find(
                                    b'NOTIFICATIONS')
                                transaction = pickle.loads(
                                    data[18:notification_header_index])
                                notification = pickle.loads(
                                    data[notification_header_index + 13:])
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

                                    with open(notifications_path, 'rb') as notifications_file:
                                        local_notifications = pickle.load(
                                            notifications_file)
                                        local_notifications.append(
                                            notification)
                                    with open(notifications_path, 'wb') as notifications_file:
                                        pickle.dump(
                                            local_notifications, notifications_file)
                                    print("Notification added.")
                                else:
                                    print(
                                        "Transaction is invalid, discarding transaction")

                            elif data[:7] == b'TXBLOCK':
                                pool_header_index = data.find(b'POOL')
                                notifications_header_index = data.find(
                                    b'NOTIFICATIONS')
                                block = pickle.loads(data[7:pool_header_index])
                                pool = pickle.loads(
                                    data[pool_header_index + 4:notifications_header_index])
                                notifications = pickle.loads(
                                    data[notifications_header_index + 13:])
                                print()
                                print(f"Received block")
                                if TxBlock.is_valid(block):
                                    print("Block is valid")
                                    cont = True
                                    try:
                                        with open(ledger_path, 'rb') as ledger_file:
                                            ledger = pickle.load(ledger_file)
                                            for b in ledger:
                                                if b.id == block.id:
                                                    print(
                                                        "Block already in the ledger, discarding block")
                                                    cont = False
                                    except EOFError:
                                        ledger = []

                                    if cont:
                                        print()
                                        print("Checking pool validity")
                                        for transaction in pool:
                                            if not Tx.is_valid(transaction):
                                                print("Pool is invalid")
                                        print("Pool is valid")

                                        with open(pool_path, 'wb') as pool_file:
                                            pickle.dump(pool, pool_file)

                                        with open(ledger_path, 'rb') as ledger_file:
                                            try:
                                                ledger = pickle.load(
                                                    ledger_file)
                                            except EOFError:
                                                ledger = []
                                            ledger.append(block)

                                        with open(ledger_path, 'wb') as ledger_file:
                                            pickle.dump(ledger, ledger_file)

                                        print()
                                        print("Block added to the ledger")

                                        for notifications in notifications:
                                            with open(notifications_path, 'rb') as notifications_file:
                                                local_notifications = pickle.load(
                                                    notifications_file)
                                                local_notifications.append(
                                                    notifications)
                                            with open(notifications_path, 'wb') as notifications_file:
                                                pickle.dump(
                                                    local_notifications, notifications_file)
                                        print(
                                            "Notifications added")
                                    else:
                                        print(
                                            "Block not added to the ledger, already mined.")

                            elif data[:4] == b'POOL':
                                pool = pickle.loads(data[4:])
                                print()
                                print(f"Received pool")
                                for transaction in pool:
                                    if not Tx.is_valid(transaction):
                                        print("Pool is invalid")
                                print("Pool is valid")
                                with open(pool_path, 'rb') as pool_file:
                                    local_pool = pickle.load(pool_file)
                                    local_transactions = []
                                    received_transactions = []
                                    for transaction in local_pool:
                                        local_transactions.append(
                                            transaction.id)
                                    for transaction in pool:
                                        received_transactions.append(
                                            transaction.id)
                                    new_transactions = [
                                        transaction for transaction in pool if transaction.id not in local_transactions]
                                    for transaction in new_transactions:
                                        local_pool.append(transaction)
                                    with open(pool_path, 'wb') as pool_file:
                                        pickle.dump(local_pool, pool_file)
                                    print("Pool updated")

                            elif data[:11] == b'ONLY_LEDGER':
                                ledger = pickle.loads(data[11:])
                                print()
                                print(f"Received ledger")
                                for block in ledger:
                                    if not TxBlock.is_valid(block):
                                        print("Ledger is invalid")
                                print("Ledger is valid")
                                with open(ledger_path, 'rb') as ledger_file:
                                    local_ledger = pickle.load(ledger_file)
                                    with open(ledger_path, 'wb') as ledger_file:
                                        pickle.dump(ledger, ledger_file)
                                    print("Ledger updated")

                            elif data[12:18] == b'LEDGER':
                                pool_header_index = data.find(b'POOL')
                                ledger = pickle.loads(
                                    data[18:pool_header_index])
                                pool = pickle.loads(
                                    data[pool_header_index + 4:])
                                # print(
                                #     f"Received ledger with size: {len(ledger)}")
                                # print(f"Received pool with size: {len(pool)}")
                                for block in ledger:
                                    if not TxBlock.is_valid(block):
                                        print("Ledger is invalid")
                                print("Ledger is valid")
                                with open(ledger_path, 'rb') as ledger_file:
                                    try:
                                        local_ledger = pickle.load(ledger_file)
                                    except EOFError:
                                        local_ledger = []
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
                                if data[:12] != b'NO_SEND_BACK':
                                    self.sync_pool_ledger(True)
                                print("Sync complete.")

                            elif data[:14] == b'NOTIFICATIONS':
                                notifications = pickle.loads(data[14:])
                                print(
                                    f"Received notifications")
                                with open(notifications_path, 'rb') as notifications_file:
                                    local_notifications = pickle.load(
                                        notifications_file)
                                    for notification in notifications:
                                        if notification not in local_notifications:
                                            local_notifications.append(
                                                notification)
                                with open(notifications_path, 'wb') as notifications_file:
                                    pickle.dump(local_notifications,
                                                notifications_file)
                                print("Notifications added.")

                            elif data[12:21] == b'NEW_USERS':
                                users = pickle.loads(data[21:])
                                print(f"Received new users ")
                                connection = sqlite3.connect(database_path)
                                cursor = connection.cursor()
                                for user in users:
                                    username = user[0]
                                    password = user[1]
                                    public_key = user[2]
                                    private_key = user[3]
                                    try:
                                        cursor.execute(
                                            'INSERT INTO registered_users VALUES (?, ?, ?, ?)', (username, password, public_key, private_key))
                                        connection.commit()
                                        print(f"Added user: {username}")
                                    except Exception as e:
                                        pass
                                print("New users added to the database.")
                                connection.close()
                                if data[:12] != b'NO_SEND_BACK':
                                    self.sync_new_users(True)

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

    def send_transaction(self, transaction, notification):
        try:
            notification_header = b'NOTIFICATIONS'
            header = b'CREATE_TRANSACTION'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                full_message = header + pickle.dumps(transaction) + \
                    notification_header + pickle.dumps(notification)
                s.sendall(full_message)
                print(f"Sent transaction.")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send transaction, please attempt to sync later.")

    def send_edit_transaction(self, transaction, notification):
        try:
            header = b'EDIT_TRANSACTION'
            notification_header = b'NOTIFICATIONS'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                full_message = header + pickle.dumps(transaction) + \
                    notification_header + pickle.dumps(notification)
                s.sendall(full_message)
                print(f"Sent edited transaction.")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send edit transaction, please attempt to sync later.")

    def send_cancel_transaction(self, transaction, notification):
        try:
            header = b'CANCEL_TRANSACTION'
            notification_header = b'NOTIFICATIONS'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                full_message = header + pickle.dumps(transaction) + \
                    notification_header + pickle.dumps(notification)
                s.sendall(full_message)
                print(f"Sent cancelled transaction.")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send cancel transaction, please attempt to sync later.")

    def send_block(self, block, pool, notifications):
        try:
            header = b'TXBLOCK'
            pool_header = b'POOL'
            notification_header = b'NOTIFICATIONS'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(block) +
                          pool_header +
                          pickle.dumps(pool) + notification_header +
                          pickle.dumps(notifications))
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
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send pool, please attempt to sync later.")

    def send_ledger(self, ledger):
        try:
            header = b'ONLY_LEDGER'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(ledger))
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send ledger, please attempt to sync later.")

    def send_notifications(self, notifications):
        try:
            header = b'NOTIFICATIONS'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + pickle.dumps(notifications))
                print(f"Sent notifications: {notifications}")
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to send notifications, please attempt to sync later.")

    def sync_new_users(self, sendback=False):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM registered_users')
        users = cursor.fetchall()

        try:
            header = b'NEW_USERS'
            no_sendback = b'NO_SEND_BACK'
            yes_sendback = b'YE_SEND_BACK'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                if sendback:
                    full_message = no_sendback + header + pickle.dumps(users)
                else:
                    full_message = yes_sendback + header + pickle.dumps(users)
                s.sendall(full_message)
            with open(pool_path, 'rb') as pool_file:
                pool = pickle.load(pool_file)
                ListeningThread.send_pool(self, pool)
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to sync new users, please attempt to sync later.")

    def sync_pool_ledger(self, sendback=False):
        try:
            header = b'HANDSHAKE'
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.other_port))
                s.sendall(header + self.username.encode())
                print(f"Sent handshake message")

            ledger = []
            pool = []
            try:
                with open(ledger_path, 'rb') as ledger_file:
                    ledger = pickle.load(ledger_file)

                with open(pool_path, 'rb') as pool_file:
                    pool = pickle.load(pool_file)

                ledger_header = b'LEDGER'
                pool_header = b'POOL'
                no_sendback = b'NO_SEND_BACK'
                yes_sendback = b'YE_SEND_BACK'
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.other_port))
                    print(f"Sending ledger size: {len(pickle.dumps(ledger))}")
                    print(f"Sending pool size: {len(pickle.dumps(pool))}")
                    print(
                        f"Total size: {len(pickle.dumps(ledger)) + len(pickle.dumps(pool))}")
                    if sendback:
                        full_message = no_sendback + ledger_header + pickle.dumps(ledger) + \
                            pool_header + pickle.dumps(pool)
                    else:
                        full_message = yes_sendback + ledger_header + pickle.dumps(ledger) + \
                            pool_header + pickle.dumps(pool)
                    s.sendall(full_message)
                    # print(f"Sent ledger: {ledger}")
                    # print(f"Sent pool: {pool}")
            except:
                print("Nothing to sync.")
                ListeningThread.sync_new_users(self)
        except ConnectionRefusedError:
            print(
                "Connection refused. Unable to sync pool and ledger, please attempt to sync later.")
