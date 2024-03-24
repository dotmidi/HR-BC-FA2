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


def register_user(username, password):
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

    # Generate private and public key
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # print(private_key)
    # print(public_key)

    os.system('cls' if os.name == 'nt' else 'clear')
    print("User " + username + " registered successfully!")
    print("You have received 50 GoodCoins for signing up!")
    print()

    # Insert user into database
    cursor.execute('INSERT INTO registered_users VALUES (?, ?, ?, ?)',
                   (username, password, private_key, public_key))
    connection.commit()

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