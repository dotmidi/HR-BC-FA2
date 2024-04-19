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
        # make the tx id a random number between 0 and 1000
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

        return "User " + username + " registered successfully! You have received 50 GoodCoins for signing up!"

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

        # get the balance from the ledger
        balance = 0
        ledger_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'ledger.dat')
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    for txBlock in block:
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

        cursor.close()
        connection.close()
        if pending_balance > 0 and pending_balance != balance:
            print("Pending balance for " + username +
                  ": " + str(pending_balance) + " GoodCoins")

        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
            except EOFError:
                pass

        if block[-1].pendingReward != []:
            if block[-1].pendingReward[1] == username:
                print("Pending reward for " + username +
                      ": " + str(block[-1].pendingReward[0] + 50) + " GoodCoins")

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

    def user_explore_ledger(username):
        try:
            with open(ledger_path, 'rb') as ledger_file:
                while True:
                    try:
                        block = pickle.load(ledger_file)
                    except EOFError:
                        print("No blocks left in the ledger, end of ledger reached")
                        break

                    for txBlock in block:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print("Block " + str(txBlock.id))
                        print("Date and time: " + str(txBlock.timeOfCreation))
                        print("Mined by: " + str(txBlock.minedBy))
                        print("Block hash: " + str(txBlock.blockHash))
                        print("Block has " + str(txBlock.flags) + "/3 flags")
                        print("Previous block hash: " +
                              str(txBlock.previousHash))
                        print()
                        if txBlock.flags < 3 and txBlock.minedBy != username and username not in txBlock.validatedBy:
                            print("Block not validated, needs " +
                                  str(3 - txBlock.flags) + " more flags")
                            print("Validating block...")
                            if txBlock.is_valid():
                                txBlock.validatedBy.append(username)
                                txBlock.flags += 1
                                print("Block validated!")
                                print("Block now has " +
                                      str(txBlock.flags) + "/3 flags")
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
                            else:
                                print("Block not valid. Removing block...")
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
                        elif txBlock.minedBy == username:
                            print("Block mined by you, cannot validate own block")
                        elif username in txBlock.validatedBy:
                            print("Block already validated by you")
                        else:
                            continue

                        if txBlock.pendingReward != [] and txBlock.flags == 3:
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

                        if txBlock.flags == 3:
                            print(
                                "Block has 3/3 flags, block has been fully validated")

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
        except FileNotFoundError:
            pass
        except pickle.UnpicklingError as e:
            print("No blocks left in the ledger, end of ledger reached")
        except Exception as e:
            pass

    def check_data_validity(startup):
        data_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data')
        data_hash = hashlib.sha256()
        for file in ['goodchain.db', 'ledger.dat', 'pool.dat']:
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
                            if tx.type == REWARD:
                                for addr, amount in tx.outputs:
                                    total_balance += amount
            except EOFError:
                pass

        print("Total GoodCoins in circulation: " + str(total_balance))
        print()

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
                            print("Block " + str(txBlock.id) + " is valid")
                        else:
                            print("Block " + str(txBlock.id) +
                                  " is invalid, exiting")
                            exit()
            except EOFError:
                pass

        HelperFunctions.check_data_validity(False)
