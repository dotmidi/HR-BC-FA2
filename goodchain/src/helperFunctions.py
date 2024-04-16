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

database_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'goodchain.db')

ledger_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'ledger.dat')

pool_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'pool.dat')


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

    def create_ledger_database():
        if not os.path.exists(ledger_path):
            with open(ledger_path, 'wb') as ledger_file:
                pass

        if not os.path.exists(pool_path):
            with open(pool_path, 'wb') as pool_file:
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
                            # if tx.type == REWARD and tx.outputs[0][0] == username:
                            #     balance += tx.outputs[0][1]
                            for addr, amount in tx.outputs:
                                if addr == username:
                                    balance += amount
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
                            # if tx.type == REWARD and tx.outputs[0][0] == username:
                            #     balance += tx.outputs[0][1]
                            for addr, amount in tx.outputs:
                                if addr == username:
                                    balance += amount
            except EOFError:
                pass

        print("Current balance for " + username +
              ": " + str(balance) + " GoodCoins")

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
        ledger_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'ledger.dat')
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    i = 1
                    for txBlock in block:
                        print("Block " + str(i))
                        print("Date and time: " + str(txBlock.timeOfCreation))
                        print("Mined by: " + str(txBlock.minedBy))
                        print("Block hash: " + str(txBlock.blockHash))
                        print("Previous block hash: " +
                              str(txBlock.previousHash))
                        # if the block has less than 3 flags, print that it's not validated and needs x/3 flags
                        if txBlock.flags < 3:
                            print("Block not validated, needs " +
                                  str(3 - txBlock.flags) + "/3 flags")
                        i += 1
                        # ask for input v to view transactions, everything else to go to next block
                        view = input(
                            "Enter v to view transactions in this block, or any other key to continue: ")
                        if view == 'v':
                            for tx in txBlock.data:
                                print(
                                    "From: " + str(tx.inputs[0][0]) + " | To: " + str(tx.outputs[0][0]))
                                print("Inputs: " + str(tx.inputs) +
                                      " | Outputs: " + str(tx.outputs))
                                print("Fee: " + str(tx.fee))
                                print()
            except EOFError:
                pass

    # make a function similar to explore_ledger but if txBlock.flags < 3, validate the block and add a flag
    def user_explore_ledger():
        with open(ledger_path, 'rb') as ledger_file:
            try:
                while True:
                    block = pickle.load(ledger_file)
                    i = 1
                    for txBlock in block:
                        print("Block " + str(i))
                        print("Date and time: " + str(txBlock.timeOfCreation))
                        print("Mined by: " + str(txBlock.minedBy))
                        print("Block hash: " + str(txBlock.blockHash))
                        print("Previous block hash: " +
                              str(txBlock.previousHash))
                        # if the block has less than 3 flags, print that it's not validated and needs x/3 flags
                        if txBlock.flags < 3:
                            print("Block not validated, needs " +
                                  str(3 - txBlock.flags) + "/3 flags")
                            validate = input(
                                "Enter v to validate this block, or any other key to continue: ")
                            if validate == 'v':
                                if txBlock.is_valid():
                                    txBlock.flags += 1
                                    print("Block validated!")
                                    print("Block now has " +
                                          str(txBlock.flags) + "/3 flags")
                                else:
                                    print("Block not validated")
                        i += 1
                        # ask for input v to view transactions, everything else to go to next block
                        view = input(
                            "Enter v to view transactions in this block, or any other key to continue: ")
                        if view == 'v':
                            for tx in txBlock.data:
                                print(
                                    "From: " + str(tx.inputs[0][0]) + " | To: " + str(tx.outputs[0][0]))
                                print("Inputs: " + str(tx.inputs) +
                                      " | Outputs: " + str(tx.outputs))
                                print("Fee: " + str(tx.fee))
                                print()
            except EOFError:
                pass
    