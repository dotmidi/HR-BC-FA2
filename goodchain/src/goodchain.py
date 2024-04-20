from helperFunctions import HelperFunctions, database_path, ledger_path, pool_path, NotificationSystem
from dataStructures import *
import os
import time
import datetime
import pickle
import random

HelperFunctions.create_user_database()
HelperFunctions.create_dat_files()
HelperFunctions.check_data_validity(True)

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
        HelperFunctions.check_data_validity(False)
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
        NotificationSystem.read_notifications(username)
        HelperFunctions.print_user_balance(username)
        HelperFunctions.print_blockchain_info()
        HelperFunctions.check_data_validity(False)
        print("1. Transfer coins")
        print("2. Explore the blockchain")
        print("3. View Transaction History")
        print("4. Check the Pool")
        print("5. Edit a Transaction")
        print("6. Cancel a Transaction")
        print("7. Mine a block")
        print("8. View User Keys")
        print("9. Check Chain Validity")
        print("10. Log out")
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
            '8': UserInterface.view_user_keys,
            '9': UserInterface.validate_entire_ledger,
            '10': UserInterface.logout
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
        HelperFunctions.validate_entire_ledger(False)
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
        HelperFunctions.validate_entire_ledger(False)
        print()
        input("Press Enter to return to the main menu.")
        UserInterface.public_menu()

    def transfer_coins():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Transfer Coins")
        print()
        print("Please note that transactions with higher fees will be prioritized in the mining process.")
        print("Any value left over from the input amount after the output and fee will be added to the fee.")
        print()
        print("Enter 'r' at any time to redo the transaction, 'exit' to return to the main menu.")
        print()

        with open(pool_path, 'rb') as pool_file:
            pool = pickle.load(pool_file)

        try:
            recipient = input("Enter the recipient's username: ")
            if recipient == 'r':
                UserInterface.transfer_coins()
            if recipient == 'exit':
                UserInterface.logged_in_menu()
            if not HelperFunctions.check_user_exists(recipient):
                print("Recipient does not exist.")
                print()
                input("Please try again.")
                UserInterface.transfer_coins()
            tx_input = float(input("Enter the input amount: "))
            if tx_input == 'r':
                UserInterface.transfer_coins()
            tx_output = float(
                input("Enter the output amount for the recipient: "))
            if tx_output == 'r':
                UserInterface.transfer_coins()
            fee = float(input("Enter the transaction fee: "))
            if fee == 'r':
                UserInterface.transfer_coins()
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

        if tx_input - tx_output - fee > 0:
            fee += round(tx_input - tx_output - fee, 1)

        print()
        print("You have input " + str(tx_input) + ", " + str(tx_output) +
              " of which will be sent to " + recipient + " and set a transaction fee of " + str(fee) + " coins.")
        confirm = input("Confirm transaction? (y/n): ")

        if confirm != 'y':
            print()
            print("Transaction cancelled.")
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        private_key = HelperFunctions.get_user_private_key(username)

        new_tx = Tx()
        new_tx.id = random.randint(0, 1000)
        new_tx.add_input(username, tx_input)
        new_tx.add_output(recipient, tx_output)
        new_tx.add_fee(fee)
        new_tx.sign(private_key)

        pool.append(new_tx)

        with open(pool_path, 'wb') as pool_file:
            pickle.dump(pool, pool_file)

        NotificationSystem.create_notification(
            recipient, "You have received a transaction worth " + str(tx_output) + " coins from " + username + " in the pool.")
        HelperFunctions.validate_entire_ledger(False)
        print("Transaction added to the pool!")
        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def user_explore():
        os.system('cls' if os.name == 'nt' else 'clear')
        HelperFunctions.user_explore_ledger(username)
        HelperFunctions.validate_entire_ledger(False)
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

        for tx in pool:
            print("Transaction type: " + ("NORMAL" if tx.type == 0 else "REWARD"))
            print("Transaction " + str(tx.id))
            print("From: " + str(tx.inputs[0][0]) +
                  " | To: " + str(tx.outputs[0][0]))
            print("Inputs: " + str(tx.inputs) +
                  " | Outputs: " + str(tx.outputs))
            print("Fee: " + str(tx.fee))
            if not tx.is_valid():
                print("Transaction + " + tx.id +
                      " is not valid. Removing from the pool.")
                pool.remove(tx)
            else:
                print("Transaction " + str(tx.id) + " is valid.")
            print()

        HelperFunctions.validate_entire_ledger(False)
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

        for tx in user_transactions:
            print("Transaction " + str(tx.id))
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

        HelperFunctions.validate_entire_ledger(False)
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

        for tx in user_transactions:
            print("Transaction " + str(tx.id))
            print("Inputs: ")
            for addr, amount in tx.inputs:
                print("From: " + addr + " Amount: " + str(amount))
            print("Outputs: ")
            for addr, amount in tx.outputs:
                print("To: " + addr + " Amount: " + str(amount))
            # print("Signatures: ")
            # for s in tx.sigs:
            #     print(s)
            print("Fee: ".join(str(fee) for fee in tx.fee))
            print()

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

        print("Enter 'r' at any time to redo the transaction, exit to return to the main menu.")
        print()
        try:
            print("Previous recipient: " + tx.outputs[0][0])
            recipient = input("Enter the recipient's username: ")
            if recipient == 'r':
                UserInterface.edit_transaction()
            if not HelperFunctions.check_user_exists(recipient):
                print("Recipient does not exist.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()
            print("Previous input: " + str(tx.inputs[0][1]))
            tx_input = input("Enter the input amount: ")
            if tx_input == 'r':
                UserInterface.edit_transaction()
            tx_input = float(tx_input)
            print("Previous output: " + str(tx.outputs[0][1]))
            tx_output = input("Enter the output amount for the recipient: ")
            if tx_output == 'r':
                UserInterface.edit_transaction()
            tx_output = float(tx_output)
            print("Previous fee: " + str(tx.fee[0]))
            fee = input("Enter the transaction fee: ")
            if fee == 'r':
                UserInterface.edit_transaction()
            fee = float(fee)
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

        if tx_input - tx_output - fee > 0:
            fee += round(tx_input - tx_output - fee, 1)

        print()
        print("You have input " + str(tx_input) + ", " + str(tx_output) +
              " of which will be sent to " + recipient + " and set a transaction fee of " + str(fee) + " coins.")
        confirm = input("Confirm transaction? (y/n): ")

        if confirm != 'y':
            print()
            print("Transaction cancelled.")
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

        NotificationSystem.create_notification(
            recipient, "A transaction destined for you from " + username + " has been edited in the pool.")
        HelperFunctions.validate_entire_ledger(False)
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

        for tx in user_transactions:
            print("Transaction " + str(tx.id))
            print("Inputs: ")
            for addr, amount in tx.inputs:
                print("From: " + addr + " Amount: " + str(amount))
            print("Outputs: ")
            for addr, amount in tx.outputs:
                print("To: " + addr + " Amount: " + str(amount))
            # print("Signatures: ")
            # for s in tx.sigs:
            #     print(s)
            print("Fee: " + ", ".join(str(fee) for fee in tx.fee))
            print()
        choice = input(
            "Enter the ID of the transaction you would like to cancel (enter 'exit' to return to the main menu): ")

        if choice == 'exit':
            UserInterface.logged_in_menu()

        # ask for additional confirmation
        confirm = input(
            "Are you sure you want to cancel transaction " + choice + "? (y/n): ")

        if confirm != 'y':
            print()
            print("Transaction cancellation cancelled.")
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()

        try:
            choice = int(choice)
        except ValueError:
            print("Invalid choice, please try again.")
            print()
            UserInterface.cancel_transaction()

        transaction_to_cancel = None
        for tx in user_transactions:
            if str(tx.id) == str(choice):
                transaction_to_cancel = tx
            continue

        if transaction_to_cancel is None:
            print("Invalid choice, please try again.")
            print()
            input("Press enter to retry.")
            UserInterface.cancel_transaction()

        pool.remove(transaction_to_cancel)

        with open(pool_path, 'wb') as pool_file:
            pickle.dump(pool, pool_file)

        NotificationSystem.create_notification(
            transaction_to_cancel.outputs[0][0], "A transaction destined for you from " + username + " has been cancelled.")
        HelperFunctions.validate_entire_ledger(False)
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

        with open(ledger_path, 'rb') as ledger_file:
            try:
                ledger = pickle.load(ledger_file)
            except EOFError:
                ledger = []

        if len(ledger) == 0:
            new_block = TxBlock(None)
            new_block.id = 0
        else:
            previous_block = ledger[-1]
            if previous_block.flags < 3:
                print(
                    "The previous block does not have enough validations to mine the next block.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()

            time_difference = datetime.datetime.strptime(datetime.datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"), "%d-%m-%Y %H:%M:%S") - datetime.datetime.strptime(previous_block.timeOfCreation, "%d-%m-%Y %H:%M:%S")
            if time_difference.total_seconds() < 180:
                print(
                    "There must be at least 3 minutes between the creation of the last block and the new block.")
                print()
                input("Press enter to return to the main menu.")
                UserInterface.logged_in_menu()

            new_block = TxBlock(previous_block)
            new_block.id = previous_block.id + 1

        ledger_file.close()
        reward_tx_count = 0
        normal_tx_count = 0
        for tx in pool:
            if reward_tx_count < 5 and tx.outputs[0][0] == "MINING REWARD":
                new_block.addTx(tx)
                reward_tx_count += 1

        for tx in pool:
            if reward_tx_count < 5 and tx.type == REWARD:
                new_block.addTx(tx)
                reward_tx_count += 1

        sorted_pool = sorted(
            pool, key=lambda tx: tx.fee[0] if tx.fee else 0, reverse=True)
        for tx in sorted_pool:
            if normal_tx_count < 10 - reward_tx_count and tx.type != REWARD:
                new_block.addTx(tx)
                normal_tx_count += 1

        print("Transactions to be mined: ")
        print()
        for tx in new_block.data:
            print("Transaction type: " + ("NORMAL" if tx.type == 0 else "REWARD"))
            print("Transaction " + str(tx.id))
            print("Inputs: ")
            for addr, amount in tx.inputs:
                print("From: " + addr + " Amount: " + str(amount))
            print("Outputs: ")
            for addr, amount in tx.outputs:
                print("To: " + addr + " Amount: " + str(amount))
            print("Fee: ", end="")
            if len(tx.fee) == 0:
                print(0)
            else:
                for fee in tx.fee:
                    print(fee)
            print()

        total_fee = 0
        for tx in new_block.data:
            if len(tx.fee) == 0:
                continue
            total_fee += tx.fee[0]

        print("Total mining reward: " + str(total_fee + 50))

        mine_choice = input("Would you like to mine this block? (y/n): ")

        if mine_choice != 'y':
            UserInterface.logged_in_menu()

        elapsed_time = new_block.mine(2)
        if elapsed_time > 20:
            print("Mining took too long, please try again.")
            print()
            input("Press enter to return to the main menu.")
            UserInterface.logged_in_menu()
        print("Mining successful.")

        new_block.minedBy = username
        new_block.pendingReward.append(total_fee)
        new_block.pendingReward.append(username)

        ledger.append(new_block)

        fh = open(ledger_path, 'wb')
        pickle.dump(ledger, fh)
        fh.close()

        pool = pool[reward_tx_count + normal_tx_count:]

        fh = open(pool_path, 'wb')
        pickle.dump(pool, fh)
        fh.close()

        for tx in new_block.data:
            for addr, amount in tx.outputs:
                NotificationSystem.create_notification(
                    addr, "A transaction destined for you from " + tx.inputs[0][0] + " has been mined in the ledger. Please verify the new block to receive the coins.")
        print("Block added to the ledger.")
        print()
        input("Press enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def view_user_keys():
        os.system('cls' if os.name == 'nt' else 'clear')
        HelperFunctions.print_user_keys(username)
        print()
        input("Press Enter to return to the main menu.")
        UserInterface.logged_in_menu()

    def validate_entire_ledger():
        os.system('cls' if os.name == 'nt' else 'clear')
        HelperFunctions.validate_entire_ledger(True)
        print()
        input("Press Enter to return to the main menu.")
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
