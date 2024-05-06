import os
import random
import sqlite3
import re
import datetime
import time
from cryptography.exceptions import *
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import hashlib
from dataStructures import *
import pickle
import random

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


class HelperFunctions:
    def __init__(self):
        pass

    def create_user_database():
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS registered_users
                        (username TEXT PRIMARY KEY, password TEXT, private_key TEXT, public_key TEXT)''')

        connection.commit()

        cursor.close()
        connection.close()

    def create_dat_files():
        if not os.path.exists(ledger_path):
            with open(ledger_path, 'wb') as ledger_file:
                pass

        if not os.path.exists(pool_path):
            with open(pool_path, 'wb') as pool_file:
                pass

        if not os.path.exists(hash_path):
            with open(hash_path, 'wb') as hash_file:
                pass

        if not os.path.exists(notifications_path):
            with open(notifications_path, 'wb') as notifications_file:
                pass

    def register_user(username, password):
        if len(username) < 3 or not re.match("^[a-zA-Z0-9_]*$", username):
            os.system('cls' if os.name == 'nt' else 'clear')
            # print("**Invalid username, please try again.**")
            print()
            return "Invalid username, please try again."

        if len(password) < 5 or not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]*$", password):
            os.system('cls' if os.name == 'nt' else 'clear')
            # print("**Invalid password, please try again.**")
            # print()
            return "Invalid password, please try again."

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            os.system('cls' if os.name == 'nt' else 'clear')
            # print("**Username already taken, please try again.**")
            # print()
            return "Username already taken, please try again."

        connection.close()

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        private_key, public_key = Signature.generate_keys()

        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []

        tx = Tx(type=REWARD)
        tx.add_input("SIGN UP REWARD", 50)
        tx.add_output(username, 50)
        tx.id = random.randint(0, 1000)

        if not tx.is_valid():
            raise Exception("Invalid transaction")

        pool.append(tx)

        with open(pool_path, 'wb') as pool_file:
            pickle.dump(pool, pool_file)

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute('INSERT INTO registered_users VALUES (?, ?, ?, ?)',
                       (username, password, private_key, public_key))
        connection.commit()
        connection.close()

        os.system('cls' if os.name == 'nt' else 'clear')
        # print("User " + username + " registered successfully!")
        # print("You have received 50 GoodCoins for signing up!")
        # print()

        return "User " + username + " registered successfully! A transaction of 50 GoodCoins has been added to the pool for you, this will be added to your balance once the block is mined."

    def login_user(username, password):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            os.system('cls' if os.name == 'nt' else 'clear')
            cursor.close()
            connection.close()
            return True
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("**Invalid username or password, please register or try again.**")
            print()
            return False

    def check_user_exists(username):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            return True
        else:
            return False

    def get_user_private_key(username):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ?', (username,))
        user = cursor.fetchone()
        return user[2]

    def explore_ledger():
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    for txBlock in block:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Block " + str(txBlock.id))
                        print("Date and time: " + str(txBlock.timeOfCreation))
                        print("Mined by: " + str(txBlock.minedBy))
                        print("Block hash: " + str(txBlock.blockHash))
                        print("Block has " + str(txBlock.flags) + "/3 flags")
                        print("Block has been validated by: " + str(txBlock.validatedBy)
                              if txBlock.validatedBy != [] else "Block has not been validated yet")
                        print("Previous block hash: " +
                              str(txBlock.previousHash))
                        for tx in txBlock.data:
                            print()
                            print(
                                "Transaction #" + str(txBlock.data.index(tx) + 1) + " in block " + str(txBlock.id))
                            print("Transaction id: " + str(tx.id))
                            print(
                                "From: " + str(tx.inputs[0][0]) + " | To: " + str(tx.outputs[0][0]))
                            print("Inputs: " + str(tx.inputs) +
                                  " | Outputs: " + str(tx.outputs))
                            print("Fee: " + str(tx.fee))
                        print()
                        input("Press Enter to continue to next block")
            except EOFError:
                print("No blocks left in the ledger, end of ledger reached")
                pass

    def view_ledger():
        choice = input(
            "How would you like to view the ledger?\n1. From the beginning to the end\n2. Specific block (by id)\n3. Only the last block\nEnter your choice (1/2/3): ")
        if choice == "1":
            HelperFunctions.explore_ledger()
        elif choice == "2":
            block_id = input("Enter the block id: ")
            with open(ledger_path, 'rb') as ledger_file:
                try:
                    while True:
                        block = pickle.load(ledger_file)
                        for txBlock in block:
                            try:
                                if txBlock.id == int(block_id):
                                    os.system('cls' if os.name ==
                                              'nt' else 'clear')
                                    print("Block " + str(txBlock.id))
                                    print("Date and time: " +
                                          str(txBlock.timeOfCreation))
                                    print("Mined by: " + str(txBlock.minedBy))
                                    print("Block hash: " +
                                          str(txBlock.blockHash))
                                    print("Block has " +
                                          str(txBlock.flags) + "/3 flags")
                                    print("Block has been validated by: " + str(txBlock.validatedBy)
                                          if txBlock.validatedBy != [] else "Block has not been validated yet")
                                    print("Previous block hash: " +
                                          str(txBlock.previousHash))
                                    for tx in txBlock.data:
                                        print()
                                        print(
                                            "Transaction #" + str(txBlock.data.index(tx) + 1) + " in block " + str(txBlock.id))
                                        print("Transaction id: " + str(tx.id))
                                        print(
                                            "From: " + str(tx.inputs[0][0]) + " | To: " + str(tx.outputs[0][0]))
                                        print("Inputs: " + str(tx.inputs) +
                                              " | Outputs: " + str(tx.outputs))
                                        print("Fee: " + str(tx.fee))
                                    print()
                            except ValueError:
                                print("Invalid block id")
                                return
                except EOFError:
                    pass
        elif choice == "3":
            with open(ledger_path, 'rb') as ledger_file:
                try:
                    while True:
                        block = pickle.load(ledger_file)
                        last_block = block[-1]
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Block " + str(last_block.id))
                        print("Date and time: " +
                              str(last_block.timeOfCreation))
                        print("Mined by: " + str(last_block.minedBy))
                        print("Block hash: " + str(last_block.blockHash))
                        print("Block has " + str(last_block.flags) + "/3 flags")
                        print("Block has been validated by: " + str(last_block.validatedBy)
                              if last_block.validatedBy != [] else "Block has not been validated yet")
                        print("Previous block hash: " +
                              str(last_block.previousHash))
                        for tx in last_block.data:
                            print()
                            print(
                                "Transaction #" + str(last_block.data.index(tx) + 1) + " in block " + str(last_block.id))
                            print("Transaction id: " + str(tx.id))
                            print(
                                "From: " + str(tx.inputs[0][0]) + " | To: " + str(tx.outputs[0][0]))
                            print("Inputs: " + str(tx.inputs) +
                                  " | Outputs: " + str(tx.outputs))
                            print("Fee: " + str(tx.fee))
                        print()
                except EOFError:
                    print("No blocks left in the ledger, end of ledger reached")
                    pass
        else:
            print("Invalid choice")

    def check_data_validity(startup):
        data_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data')
        data_hash = hashlib.sha256()
        for file in ['goodchain.db', 'ledger.dat', 'pool.dat', 'notifications.dat']:
            with open(os.path.join(data_path, file), 'rb') as f:
                data_hash.update(f.read())
        data_hash_digest = data_hash.digest()
        if os.path.getsize(os.path.join(data_path, 'hash.dat')) == 0:
            with open(os.path.join(data_path, 'hash.dat'), 'wb') as hash_file:
                hash_file.write(data_hash_digest)
                return
        hash_path = os.path.join(data_path, 'hash.dat')
        if startup:
            with open(hash_path, 'rb') as hash_file:
                stored_hash = hash_file.read()
            if data_hash_digest == stored_hash:
                print("Data is valid")
            else:
                print("Data has been tampered with")
                exit()
        with open(hash_path, 'wb') as hash_file:
            hash_file.write(data_hash_digest)

    def print_user_keys(username):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            print("Public key: " + user[3].decode('utf-8'))
            print("Private key: " + user[2].decode('utf-8'))
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("**Invalid username, please try again.**")
            print()

        cursor.close()
        connection.close()

    def validate_entire_ledger(func):
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    for txBlock in block:
                        if not func and txBlock.is_valid():
                            continue
                        elif txBlock.is_valid():
                            print("Block " + str(txBlock.id) + " is valid.")
                        else:
                            print("Block " + str(txBlock.id) +
                                  " is invalid.")
            except EOFError:
                pass

        HelperFunctions.check_data_validity(False)


class AutomaticLoginActions:
    def __init__(self):
        pass

    def check_tx_pool(username):
        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []

        if pool == []:
            print("No transactions to check.")
        else:
            print("Checking transaction pool for invalid transactions...")
            all_valid = True
            for tx in pool:
                if not tx.is_valid():
                    print("Transaction " + str(tx.id) +
                          " is invalid, removing...")
                    for addr, amount in tx.outputs:
                        NotificationSystem.create_notification(
                            addr, "A transaction you were involved in has been deemed invalid and removed from the pool")
                    pool.remove(tx)
                    all_valid = False

            if all_valid:
                print("All transactions are valid!")

        with open(pool_path, 'wb') as pool_file:
            pickle.dump(pool, pool_file)

    def check_ledger_blocks(username):
        print()
        print("Checking ledger blocks' validity...")
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    try:
                        block = pickle.load(ledger_file)
                        for txBlock in block:
                            print("Checking block " + str(txBlock.id) + "...")
                            if txBlock.flags >= 3:
                                print("Block " + str(txBlock.id) +
                                    " has 3/3 flags, block is fully validated")
                            elif txBlock.minedBy == username:
                                print("Block currently has " +
                                    str(txBlock.flags) + "/3 flags")
                                print("Block " + str(txBlock.id) +
                                    " was mined by you, skipping...")
                            elif txBlock.validatedBy != [] and username in txBlock.validatedBy:
                                print("Block currently has " +
                                    str(txBlock.flags) + "/3 flags")
                                print("Block " + str(txBlock.id) +
                                    " has already been validated by you, skipping...")
                            elif not txBlock.is_valid():
                                txBlock.invalidFlags += 1
                                print("Block " + str(txBlock.id) +
                                    " is invalid, adding invalid flag...")
                                NotificationSystem.create_notification(
                                    txBlock.minedBy, "Block " + str(txBlock.id) + " has been given an invalid flag by " + username)
                                if txBlock.invalidFlags == 3:
                                    print(
                                        "Block " + str(txBlock.id) + " has reached 3 invalid flags, removing block from ledger...")
                                    ledger = []
                                    ledger_file.seek(0)
                                    try:
                                        while True:
                                            ledger.append(
                                                pickle.load(ledger_file))
                                    except EOFError:
                                        pass
                                    ledger.pop()
                                    with open(ledger_path, 'wb') as ledger_filew:
                                        for block in ledger:
                                            pickle.dump(block, ledger_filew)
                                    NotificationSystem.create_notification(
                                        txBlock.minedBy, "Block " + str(txBlock.id) + " has received 3 invalid flags and has been removed from the ledger")
                                    for tx in txBlock.data:
                                        for addr, amount in tx.outputs:
                                            NotificationSystem.create_notification(
                                                addr, "A block which you have a transaction in has been removed from the ledger")
                                else:
                                    ledger = []
                                    ledger_file.seek(0)
                                    try:
                                        while True:
                                            ledger.append(pickle.load(ledger_file))
                                    except EOFError:
                                        pass
                                    ledger.pop()
                                    ledger.append(block)
                                    with open(ledger_path, 'wb') as ledger_filew:
                                        for block in ledger:
                                            pickle.dump(block, ledger_filew)
                            else:
                                print("Block " + str(txBlock.id) + " is valid.")
                                txBlock.flags += 1
                                txBlock.validatedBy.append(username)
                                print("Block now has " +
                                    str(txBlock.flags) + "/3 flags")
                                ledger = []
                                ledger_file.seek(0)
                                try:
                                    while True:
                                        ledger.append(pickle.load(ledger_file))
                                except EOFError:
                                    pass
                                ledger.pop()
                                ledger.append(block)
                                with open(ledger_path, 'wb') as ledger_filew:
                                    for block in ledger:
                                        pickle.dump(block, ledger_filew)
                                NotificationSystem.create_notification(
                                    txBlock.minedBy, "Block " + str(txBlock.id) + " has been validated by " + username)
                                if txBlock.flags == 3 and txBlock.pendingReward != []:
                                    tx = Tx(type=REWARD)
                                    tx.add_input("MINING REWARD", 50)
                                    tx.add_input("TRANSACTION FEES",
                                                txBlock.pendingReward[0])
                                    tx.add_output(
                                        txBlock.pendingReward[1], 50 + txBlock.pendingReward[0])
                                    tx.id = random.randint(0, 1000)
                                    if not tx.is_valid():
                                        raise Exception("Invalid transaction")
                                    with open(pool_path, 'rb') as pool_file:
                                        try:
                                            pool = pickle.load(pool_file)
                                        except EOFError:
                                            pool = []
                                    pool.append(tx)
                                    with open(pool_path, 'wb') as pool_filew:
                                        pickle.dump(pool, pool_filew)
                                    txBlock.pendingReward = []
                                    ledger = []
                                    ledger_file.seek(0)
                                    try:
                                        while True:
                                            ledger.append(
                                                pickle.load(ledger_file))
                                    except EOFError:
                                        pass
                                    ledger.pop()
                                    ledger.append(block)
                                    with open(ledger_path, 'wb') as ledger_filew:
                                        for block in ledger:
                                            pickle.dump(block, ledger_filew)
                                    for tx in txBlock.data:
                                        for addr, amount in tx.outputs:
                                            NotificationSystem.create_notification(
                                                addr, "A block which you have a transaction in has been fully validated.")
                                    NotificationSystem.create_notification(
                                        txBlock.minedBy, "Block " + str(txBlock.id) + " has been fully validated and your mining reward has been added to the pool")
                    except pickle.UnpicklingError:
                        # print("End of ledger reached, no more blocks to check")
                        break
            except EOFError:
                print("End of ledger reached, no more blocks to check")
                pass

    def main(username):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Running automatic login checks...")
        print()
        AutomaticLoginActions.check_tx_pool(username)
        AutomaticLoginActions.check_ledger_blocks(username)
        HelperFunctions.check_data_validity(False)
        print()
        input("Press Enter to continue")
        os.system('cls' if os.name == 'nt' else 'clear')


class NotificationSystem:
    def __init__(self):
        pass

    def create_notification(username, message):
        with open(notifications_path, 'rb') as notifications_file:
            try:
                notifications = pickle.load(notifications_file)
            except EOFError:
                notifications = []

        notifications.append((username, message))

        with open(notifications_path, 'wb') as notifications_file:
            pickle.dump(notifications, notifications_file)

    def read_notifications(username):
        with open(notifications_path, 'rb') as notifications_file:
            try:
                notifications = pickle.load(notifications_file)
            except EOFError:
                notifications = []

        for notification in notifications:
            if notification[0] == username:
                print(f"\033[1m{notification[1]}\033[0m")
                print()

        notifications = [
            notification for notification in notifications if notification[0] != username]

        with open(notifications_path, 'wb') as notifications_file:
            pickle.dump(notifications, notifications_file)

    def print_blockchain_info():
        print()
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM registered_users')
        users = cursor.fetchall()
        print("Total signed up users: " + str(len(users)))

        cursor.close()
        connection.close()

        with open(ledger_path, 'rb') as ledger_file:
            try:
                block = pickle.load(ledger_file)
            except EOFError:
                block = []
        print("Total blocks in the ledger: " + str(len(block)))

        total_tx = 0
        if block == []:
            total_tx = 0
        else:
            for txBlock in block:
                total_tx += len(txBlock.data)
        print("Total transactions in the ledger: " + str(total_tx))

        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []
        print("Total transactions in the pool: " + str(len(pool)))

        total_balance = 0
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    for txBlock in block:
                        for tx in txBlock.data:
                            if tx.inputs[0][0] == "SIGN UP REWARD":
                                for addr, amount in tx.outputs:
                                    total_balance += amount
                            elif tx.inputs[0][0] == "MINING REWARD":
                                total_balance += 50
            except EOFError:
                pass
        print("Total GoodCoins in circulation: " + str(total_balance))
        print()


class WalletFunctions:
    def __init__(self):
        pass

    def check_user_balance(username):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            public_key = user[3]
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("**Invalid username, please try again.**")
            print()
            return False

        balance = 0
        ledger_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'ledger.dat')
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    for txBlock in block:
                        if txBlock.flags == 3:
                            for tx in txBlock.data:
                                for addr, amount in tx.outputs:
                                    if addr == username:
                                        balance += amount
                                for addr, amount in tx.inputs:
                                    if addr == username:
                                        balance -= amount
            except EOFError:
                pass

        cursor.close()
        connection.close()
        return balance

    def print_user_balance(username):
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            public_key = user[3]
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("**Invalid username, please try again.**")
            print()
            return False

        balance = 0
        ledger_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'ledger.dat')
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    for txBlock in block:
                        if txBlock.flags == 3:
                            for tx in txBlock.data:
                                for addr, amount in tx.outputs:
                                    if addr == username:
                                        balance += amount
                                for addr, amount in tx.inputs:
                                    if addr == username:
                                        balance -= amount
            except EOFError:
                pass

        print(f"Current balance for {username}: {balance:.1f} GoodCoins")

        pool_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'pool.dat')

        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                pool = []

        pending_balance = balance
        for tx in pool:
            for addr, amount in tx.outputs:
                if addr == username:
                    pending_balance += amount
            for addr, amount in tx.inputs:
                if addr == username:
                    pending_balance -= amount

        ledger_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'ledger.dat')

        with open(ledger_path, 'rb') as ledger_file:
            try:
                block = pickle.load(ledger_file)
                for txBlock in block:
                    if txBlock.flags < 3:
                        for tx in txBlock.data:
                            for addr, amount in tx.outputs:
                                if addr == username:
                                    pending_balance += amount
                            for addr, amount in tx.inputs:
                                if addr == username:
                                    pending_balance -= amount
            except EOFError:
                pass

        cursor.close()
        connection.close()
        if pending_balance > 0 and pending_balance != balance:
            print("Pending balance for " + username +
                  ": " + str(pending_balance) + " GoodCoins")

        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    if block[-1].pendingReward != []:
                        if block[-1].pendingReward[1] == username:
                            print("Pending mining reward for " + username +
                                  ": " + str(block[-1].pendingReward[0] + 50) + " GoodCoins")
            except EOFError:
                pass
