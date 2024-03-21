from helperFunctions import (
    create_relational_database,
    register_user
)

import os

create_relational_database()

os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    while True:
        print("Public Menu")
        print()
        print("Welcome to Goodchain!")
        print()
        print("1. Login")
        print("2. Explore the blockchain")
        print("3. Sign up")
        print("4. Exit")
        print()
        choice = input("Enter your choice: ")

        def login():
            print("Login")
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            # login logic goes here

        def explore_blockchain():
            print("Explore the blockchain")
            # explore blockchain logic goes here

        def sign_up():
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Sign up")
            print("You will receive 50 GoodCoins for signing up!")
            print()
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            register_user(username, password)

        def default():
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Invalid choice, please try again.")
            print()

        switch = {
            '1': login,
            '2': explore_blockchain,
            '3': sign_up,
            '4': lambda: print("Goodbye!") or exit()
        }

        switch.get(choice, default)()
