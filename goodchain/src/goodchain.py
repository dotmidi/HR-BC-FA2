from helperFunctions import HelperFunctions
import os
import time
import datetime

HelperFunctions.create_user_database()
HelperFunctions.create_ledger_database()

os.system('cls' if os.name == 'nt' else 'clear')

is_logged_in = False
username = None


class UserInterface:
    def __init__(self):
        pass

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

        switch = {
            '1': UserInterface.login,
            '2': UserInterface.explore,
            '3': UserInterface.signup,
            '4': lambda: print("Goodbye!") or exit()
        }

        def default():
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Invalid choice, please try again.")
            print()

        try:
            switch.get(choice, default)()
        except TypeError:
            print("Invalid choice, please try again.")

    def logged_in_menu():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("User currently logged in: " + username)
        HelperFunctions.print_user_balance(username)
        print()
        print("1. Transfer coins")
        print("2. Explore the blockchain")
        print("3. Check the Pool")
        print("4. Cancel a Transaction")
        print("5. Mine a block")
        print("6. Log out")
        print()
        choice = input("Enter your choice: ")

        switch = {
            '1': UserInterface.transfer_coins,
            '2': UserInterface.explore,
            '3': UserInterface.check_pool,
            '4': UserInterface.cancel_transaction,
            '5': UserInterface.mine_block,
            '6': UserInterface.logout
        }

        try:
            switch.get(choice, default)()
        except TypeError:
            print("Invalid choice, please try again.")

    def login():
        global is_logged_in
        global username

        os.system('cls' if os.name == 'nt' else 'clear')
        print("Login")
        print()
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if HelperFunctions.login_user(username, password):
            is_logged_in = True
            UserInterface.logged_in_menu()
        else:
            print("Invalid username or password, please try again.")
            print()
            UserInterface.public_menu()

    def explore():
        os.system('cls' if os.name == 'nt' else 'clear')
        HelperFunctions.explore_ledger()
        print()
        input("Press enter to return to the main menu.")
        UserInterface.public_menu()

    def signup():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Sign Up")
        print()
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        HelperFunctions.register_user(username, password)
        print("You have successfully signed up!")
        print()
        UserInterface.public_menu()

UserInterface.public_menu()