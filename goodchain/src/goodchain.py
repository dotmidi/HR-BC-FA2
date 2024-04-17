from helperFunctions import HelperFunctions, database_path, ledger_path, pool_path
from dataStructures import *
import os
import time
import datetime
import pickle

HelperFunctions.create_user_database()
HelperFunctions.create_ledger_database()

os.system('cls' if os.name == 'nt' else 'clear')

is_logged_in = False
username = None


class UserInterface:
    def __init__(self):
        pass

    def public_menu():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Public Menu")
        print("Welcome to Goodchain!")
        HelperFunctions.print_blockchain_info()
        print("1. Login")
        print("2. Explore the blockchain")
        print("3. Sign up")
        print("4. Exit")
        print()
        choice = input("Enter your choice: ")

        switch = {
            '1': UserInterface.login,
            '2': UserInterface.public_explore,
            '3': UserInterface.signup,
            '4': lambda: print("Goodbye!") or exit()
        }

        def default():
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Invalid choice, please try again.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.public_menu()

        try:
            switch.get(choice, default)()
        except TypeError:
            print("Invalid choice, please try again.")

    def logged_in_menu():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("User currently logged in: " + username)
        HelperFunctions.print_user_balance(username)
        HelperFunctions.print_blockchain_info()
        print("1. Transfer coins")
        print("2. Explore the blockchain")
        print("3. View Transaction History")
        print("4. Check the Pool")
        print("5. Edit a Transaction")
        print("6. Cancel a Transaction")
        print("7. Mine a block")
        print("8. Log out")
        print()
        choice = input("Enter your choice: ")

        switch = {
            '1': UserInterface.transfer_coins,
            '2': UserInterface.user_explore,
            '3': UserInterface.view_transaction_history,
            '4': UserInterface.check_pool,
            '5': UserInterface.edit_transaction,
            '6': UserInterface.cancel_transaction,
            '7': UserInterface.mine_block,
            '8': UserInterface.logout
        }

        def default():
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Invalid choice, please try again.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

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
            input("Press enter to return to the main menu.")
            UserInterface.public_menu()

    def public_explore():
        os.system('cls' if os.name == 'nt' else 'clear')
        HelperFunctions.explore_ledger()
        print()
        input("Press Enter to return to the main menu.")
        UserInterface.public_menu()

    def signup():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Sign Up")
        print()
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        print(HelperFunctions.register_user(username, password))
        print()
        input("Press Enter to return to the main menu.")
        UserInterface.public_menu()

    def transfer_coins():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Transfer Coins")

        with open(pool_path, 'rb') as pool_file:
            pool = pickle.load(pool_file)

        # ask for recipient, input, output and fee. Make these fields navigatable using arrow keys
        try:
            recipient = input("Enter the recipient's username: ")
            tx_input = float(input("Enter the input amount: "))
            tx_output = float(input("Enter the output amount for the recipient: "))
            fee = float(input("Enter the transaction fee: "))
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        if tx_input < tx_output + fee:
            print("Invalid transaction: input must be greater than output and fee.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        if not HelperFunctions.check_user_exists(recipient):
            print("Recipient does not exist.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        if recipient == username:
            print("You cannot send coins to yourself.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        if HelperFunctions.check_user_balance(username) < tx_input:
            print("Insufficient balance.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        private_key = HelperFunctions.get_user_private_key(username)

        new_tx = Tx()
        new_tx.add_input(username, tx_input)
        new_tx.add_output(recipient, tx_output)
        new_tx.add_fee(fee)
        new_tx.sign(private_key)

        pool.append(new_tx)

        with open(pool_path, 'wb') as pool_file:
            pickle.dump(pool, pool_file)

        print("Transaction added to the pool!")
        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def user_explore():
        os.system('cls' if os.name == 'nt' else 'clear')
        HelperFunctions.user_explore_ledger(username)
        print()
        input("Press Enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def check_pool():
        os.system('cls' if os.name == 'nt' else 'clear')
        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                print("The pool is empty.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()

        if len(pool) == 0:
            print("The pool is empty.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        i = 1
        for tx in pool:
            print("From: " + str(tx.inputs[0][0]) +
                  " | To: " + str(tx.outputs[0][0]))
            print("Inputs: " + str(tx.inputs) +
                  " | Outputs: " + str(tx.outputs))
            print("Fee: " + str(tx.fee))
            print()

        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def view_transaction_history():
        os.system('cls' if os.name == 'nt' else 'clear')
        with open(ledger_path, 'rb') as ledger_file:
            try:
                ledger = pickle.load(ledger_file)
            except EOFError:
                print("The ledger is empty.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()

        user_transactions = []
        for block in ledger:
            for tx in block.data:
                if tx.inputs[0][0] == username or tx.outputs[0][0] == username:
                    user_transactions.append(tx)

        if len(user_transactions) == 0:
            print("You have no transactions.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        i = 1
        for tx in user_transactions:
            print("Transaction " + str(i))
            print("Inputs: ", end="")
            for addr, amount in tx.inputs:
                print("From: " + addr + " Amount: " + str(amount), end=" ")
            print()
            print("Outputs: ", end="")
            for addr, amount in tx.outputs:
                print("To: " + addr + " Amount: " + str(amount), end=" ")
            print()
            for fee in tx.fee:
                print("Fee: " + str(fee))
            print()
            i += 1

        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()
    
    def edit_transaction():
        os.system('cls' if os.name == 'nt' else 'clear')
        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                print("The pool is empty.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()

        user_transactions = []
        for tx in pool:
            if tx.inputs[0][0] == username:
                user_transactions.append(tx)

        if len(user_transactions) == 0:
            print("You have no transactions to edit.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        i = 1
        for tx in user_transactions:
            print("Transaction " + str(i))
            print("Inputs: ")
            for addr, amount in tx.inputs:
                print("From: " + addr + " Amount: " + str(amount))
            print("Outputs: ")
            for addr, amount in tx.outputs:
                print("To: " + addr + " Amount: " + str(amount))
            # print("Signatures: ")
            # for s in tx.sigs:
            #     print(s)
            print("Fee: ")
            for fee in tx.fee:
                print(fee)
            print()
            i += 1

        choice = input(
            "Enter the number of the transaction you would like to edit (enter 'r' to return to the main menu): ")

        if choice == 'r':
            UserInterface.logged_in_menu()

        try:
            choice = int(choice)
        except ValueError:
            print("Invalid choice, please try again.")
            print()
            UserInterface.edit_transaction()

        if choice < 1 or choice > len(user_transactions):
            print("Invalid choice, please try again.")
            print()
            UserInterface.edit_transaction()

        tx = user_transactions[choice - 1]
        
        # ask for recipient, input, output and fee. the default values should be the current values of the transaction
        try:
            print("Previous recipient: " + tx.outputs[0][0])
            recipient = input("Enter the recipient's username: ")
            print("Previous input: " + str(tx.inputs[0][1]))
            tx_input = float(input("Enter the input amount: "))
            print("Previous output: " + str(tx.outputs[0][1]))
            tx_output = float(input("Enter the output amount for the recipient: "))
            print("Previous fee: " + str(tx.fee[0]))
            fee = float(input("Enter the transaction fee: "))
            
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()
            
        if tx_input < tx_output + fee:
            print("Invalid transaction: input must be greater than output and fee.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()
            
        if not HelperFunctions.check_user_exists(recipient):
            print("Recipient does not exist.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()
            
        if recipient == username:
            print("You cannot send coins to yourself.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()
            
        if HelperFunctions.check_user_balance(username) < tx_input:
            print("Insufficient balance.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()
            
        private_key = HelperFunctions.get_user_private_key(username)
        
        new_tx = Tx()
        new_tx.add_input(username, tx_input)
        new_tx.add_output(recipient, tx_output)
        new_tx.add_fee(fee)
        new_tx.sign(private_key)
        
        pool.remove(tx)
        
        pool.append(new_tx)
        
        with open(pool_path, 'wb') as pool_file:
            pickle.dump(pool, pool_file)
            
        print("Transaction edited.")
        print()

        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()
        
    def cancel_transaction():
        os.system('cls' if os.name == 'nt' else 'clear')
        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                print("The pool is empty.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()

        user_transactions = []
        for tx in pool:
            if tx.inputs[0][0] == username:
                user_transactions.append(tx)

        if len(user_transactions) == 0:
            print("You have no transactions to cancel.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        i = 1
        for tx in user_transactions:
            print("Transaction " + str(i))
            print("Inputs: ")
            for addr, amount in tx.inputs:
                print("From: " + addr + " Amount: " + str(amount))
            print("Outputs: ")
            for addr, amount in tx.outputs:
                print("To: " + addr + " Amount: " + str(amount))
            # print("Signatures: ")
            # for s in tx.sigs:
            #     print(s)
            print("Fee:")
            for fee in tx.fee:
                print(fee)
            print()
            i += 1

        choice = input(
            "Enter the number of the transaction you would like to cancel (enter 'r' to return to the main menu): ")

        if choice == 'r':
            UserInterface.logged_in_menu()

        try:
            choice = int(choice)
        except ValueError:
            print("Invalid choice, please try again.")
            print()
            UserInterface.cancel_transaction()

        if choice < 1 or choice > len(user_transactions):
            print("Invalid choice, please try again.")
            print()
            UserInterface.cancel_transaction()

        pool.remove(user_transactions[choice - 1])

        with open(pool_path, 'wb') as pool_file:
            pickle.dump(pool, pool_file)

        print("Transaction cancelled.")
        print()
        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def mine_block():
        os.system('cls' if os.name == 'nt' else 'clear')
        with open(pool_path, 'rb') as pool_file:
            try:
                pool = pickle.load(pool_file)
            except EOFError:
                print("The pool is empty.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()

        pool_file.close()

        if len(pool) == 0:
            print("The pool is empty.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        print("Transactions in the pool: ")
        print()
        i = 1
        for tx in pool:
            print("Transaction " + str(i))
            print("Inputs: ")
            for addr, amount in tx.inputs:
                print("From: " + addr + " Amount: " + str(amount))
            print("Outputs: ")
            for addr, amount in tx.outputs:
                print("To: " + addr + " Amount: " + str(amount))
            # print("Signatures: ")
            # for s in tx.sigs:
            #     print(s)
            print("Fee:")
            for fee in tx.fee:
                print(fee)
            print()
            i += 1

        if len(pool) < 5:
            print("There are not enough transactions in the pool to mine a block.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        mine_choice = input("Would you like to mine a block? (y/n): ")

        if mine_choice != 'y':
            UserInterface.logged_in_menu()

        with open(ledger_path, 'rb') as ledger_file:
            try:
                ledger = pickle.load(ledger_file)
            except EOFError:
                ledger = []

        if len(ledger) == 0:
            new_block = TxBlock(None)
        else:
            previous_block = ledger[-1]
            if previous_block.validations < 3:
                print("The previous block does not have enough validations to mine the next block.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()
            new_block = TxBlock(previous_block)

        ledger_file.close()
        j = 0
        for i, tx in enumerate(pool):
            if i < 10:
                new_block.addTx(tx)
                j += 1
            else:
                break

        new_block.mine(2)

        # if not new_block.is_valid():
        #     print("Block is not valid.")
        #     print()
        #     input("Press enter to return to the main menu.")
        #     UserInterface.logged_in_menu()
        new_block.minedBy = username
        if new_block.is_valid():
            print("Block is valid. ")
            # print(new_block.blockHash)
            # print(new_block.previousHash)
            # print(new_block.nonce)
            # print(new_block.timeOfCreation)
        else:
            print("Block is not valid.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        ledger.append(new_block)

        fh = open(ledger_path, 'wb')
        pickle.dump(ledger, fh)
        fh.close()

        pool = pool[j:]

        fh = open(pool_path, 'wb')
        pickle.dump(pool, fh)
        fh.close()

        print("Block added to the ledger.")
        print()
        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def logout():
        global is_logged_in
        global username

        os.system('cls' if os.name == 'nt' else 'clear')
        print("You have been logged out.")
        print()
        is_logged_in = False
        username = None
        UserInterface.public_menu()

UserInterface.public_menu()
