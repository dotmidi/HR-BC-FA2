from helperFunctions import (
    create_relational_database,
    register_user,
    login_user,
)

import os

create_relational_database()

os.system('cls' if os.name == 'nt' else 'clear')

def public_menu():
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
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Login")
        print()
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        is_logged_in = login_user(username, password)
        if is_logged_in:
            current_user = username
            logged_in_menu()
        else:
            public_menu()

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

def logged_in_menu():
    print("User currently logged in: " + current_user)
    print()
    print("1. Transfer coins")
    print("2. Check Balance")
    print("3. Explore the blockchain")
    print("4. Check the Pool")
    print("5. Cancel a Transaction")
    print("6. Mine a block")
    print("7. Log out")
    print()
    choice = input("Enter your choice: ")

    def view_profile():
        print("View Profile")
        # view profile logic goes here

    def send_goodcoins():
        print("Send GoodCoins")
        # send GoodCoins logic goes here

    def check_balance():
        print("Check Balance")
        # check balance logic goes here

    def explore_blockchain():
        print("Explore the blockchain")
        # explore blockchain logic goes here

    def check_pool():
        print("Check the Pool")
        # check the pool logic goes here

    def cancel_transaction():
        print("Cancel a Transaction")
        # cancel a transaction logic goes here

    def mine_block():
        print("Mine a block")
        # mine a block logic goes here

    def logout():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("You have been logged out.")
        print()
        public_menu()

    def default():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Invalid choice, please try again.")
        print()

    switch = {
        '1': send_goodcoins,
        '2': check_balance,
        '3': explore_blockchain,
        '4': check_pool,
        '5': cancel_transaction,
        '6': mine_block,
        '7': logout
    }

    switch.get(choice, default)()

# Check if the user is logged in
current_user = ""
is_logged_in = False  # Replace with your login logic

while True:
    if is_logged_in:
        logged_in_menu()
    else:
        public_menu()
