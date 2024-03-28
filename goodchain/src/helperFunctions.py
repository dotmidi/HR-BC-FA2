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


def create_user_database():
    # setup connection for database
    database_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'data', 'goodchain.db')
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    # Create tables if they don't exist
    # Table: registered_users
    # Table contents: registered_users: username, password, private key, public key

    cursor.execute('''CREATE TABLE IF NOT EXISTS registered_users
                    (username TEXT PRIMARY KEY, password TEXT, private_key TEXT, public_key TEXT)''')

    connection.commit()


def create_ledger_database():
    # open ledger.dat file in write mode
    ledger_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'data', 'ledger.dat')

    # check if the ledger file already exists
    if os.path.exists(ledger_path):
        # print("Ledger file already exists.")
        return

    # create the ledger file
    with open(ledger_path, 'wb') as ledger_file:
        pass

    # create pool file
    pool_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'data', 'pool.dat')

    # check if the pool file already exists
    if os.path.exists(pool_path):
        # print("Pool file already exists.")
        return

    # create the pool file
    with open(pool_path, 'wb') as pool_file:
        pass

    # # use the CBlock class to create the ledger
    # # create the genesis block
    # genesis_block = CBlock("Genesis Block", None)
    # genesis_block.blockHash = genesis_block.computeHash()

    # # write the genesis block to the ledger file
    # with open(ledger_path, 'wb') as ledger_file:
    #     ledger_file.write(pickle.dumps(genesis_block))


def register_user(username, password):
    # check if username is atleast 3 characters long and contains only alphanumeric characters
    if len(username) < 3 or not re.match("^[a-zA-Z0-9_]*$", username):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("**Invalid username, please try again.**")
        print()
        return False

    # check if password is atleast 5 characters long and contains atleast one uppercase letter, one lowercase letter, one digit and one special character
    if len(password) < 5 or not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]*$", password):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("**Invalid password, please try again.**")
        print()
        return False

    # setup connection for database
    database_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'data', 'goodchain.db')
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    # Check if username is already taken
    cursor.execute(
        'SELECT * FROM registered_users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("**Username already taken, please try again.**")
        print()
        return False

    # hash the password
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Generate private and public keys
    private_key, public_key = Signature.generate_keys()

    # grant 50 GoodCoins to the user
    pool_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'data', 'pool.dat')
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

    # Insert user into database
    cursor.execute('INSERT INTO registered_users VALUES (?, ?, ?, ?)',
                   (username, password, private_key, public_key))
    connection.commit()
    connection.close()

    os.system('cls' if os.name == 'nt' else 'clear')
    print("User " + username + " registered successfully!")
    print("You have received 50 GoodCoins for signing up!")
    print()

    return True


def login_user(username, password):
    # setup connection for database
    database_path = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'data', 'goodchain.db')
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    # hash the password
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Check if username and password match
    cursor.execute(
        'SELECT * FROM registered_users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
        os.system('cls' if os.name == 'nt' else 'clear')
        return True
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("**Invalid username or password, please register or try again.**")
        print()
        return False
