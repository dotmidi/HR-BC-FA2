import os
import pickle

from helperFunctions import *
from dataStructures import *
import time
import datetime

create_user_database()
create_ledger_database()

os.system('cls' if os.name == 'nt' else 'clear')

is_logged_in = False
current_user = ""

def public_menu():
    global is_logged_in
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
        global is_logged_in
        global current_user
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Login")
        print()
        username = input("Enter your username: ")
        password = input("Enter your password (enter 'r' to redo the login): ")
        if password == 'r':
            login()
        else:
            is_logged_in = login_user(username, password)
            current_user = username

    def explore_blockchain():
        os.system('cls' if os.name == 'nt' else 'clear')
        # open the ledger.dat file in read mode
        ledger_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'ledger.dat')

        # check if the ledger file exists
        if not os.path.exists(ledger_path):
            print("No blocks found in the blockchain.")
            print()
            return

        # read the ledger file
        with open(ledger_path, 'rb') as ledger_file:
            try:
                blocks = pickle.load(ledger_file)
            except EOFError:
                print("No blocks found in the blockchain.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # iterate through the blocks in the blockchain
            i = 1
            for block in blocks:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Block " + str(i))
                print("Transaction Data:")
                print()
                # print like this: <TYPE> | <AMOUNT> From <FROM> To <TO>
                for tx in block.data:
                    if tx.type == REWARD:
                        print("REWARD | " + str(tx.outputs[0][1]) + " From " + str(
                            tx.outputs[0][0]) + " To " + str(tx.outputs[0][0]))
                    else:
                        for addr, amount in tx.inputs:
                            print("NORMAL | " + str(amount) +
                                  " From " + str(addr), end=' ')
                        for addr, amount in tx.outputs:
                            print("To " + str(addr))
                print()
                print("Date of Creation: " + str(block.dateOfCreation))
                print("Mined by: " + str(block.minedBy))
                print("Block Hash: " + str(block.blockHash))
                print("Previous Hash: " + str(block.previousHash))
                print()
                i += 1
                if i != len(blocks) + 1:
                    input("Press Enter to view the next block...")

            input("Press Enter to return to the main menu...")
            os.system('cls' if os.name == 'nt' else 'clear')
            return

    def sign_up():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Sign up")
        print("You will receive 50 GoodCoins for signing up!")
        print()
        username = input(
            "Enter your username (at least 3 characters long and unique): ")
        password = input(
            "Enter your password (at least 5 characters long, 1 uppercase letter, 1 lowercase letter, 1 digit and 1 special character): ")
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

    try:
        switch.get(choice, default)()
    except TypeError:
        print("Invalid choice, please try again.")


def logged_in_menu():
    global is_logged_in
    global current_user
    os.system('cls' if os.name == 'nt' else 'clear')
    print("User currently logged in: " + current_user)
    # print the current balance
    print_user_balance(current_user)
    print()
    print("1. Transfer coins")
    print("2. Explore the blockchain")
    print("3. Check the Pool")
    print("4. Cancel a Transaction")
    print("5. Mine a block")
    print("6. Log out")
    print()
    choice = input("Enter your choice: ")

    def send_goodcoins():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Send GoodCoins")

        # open the pool.dat file in read mode
        pool_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'pool.dat')

        # check if the pool file exists
        if not os.path.exists(pool_path):
            print("No transactions found in the pool.")
            print()
            return

        # read the pool file
        with open(pool_path, 'rb') as pool_file:
            try:
                # load the transactions from the pool file
                transactions = pickle.load(pool_file)
            except EOFError:
                print("No transactions found in the pool.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # ask for the recipient, input, output and fee
            recipient = input("Enter the recipient's username: ")
            tx_input = int(input("Enter the input amount: "))
            tx_output = int(input("Enter the output amount: "))
            fee = int(input("Enter the fee: "))

            # if the input is less than the output and fee, print an invalid tx message and return to the main menu
            if tx_input < tx_output + fee:
                print("Invalid transaction, input is less than output + fee.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # check if recipient exists
            if not check_user_exists(recipient):
                print("Recipient does not exist.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # check if recipient is the sender
            if recipient == current_user:
                print("Recipient cannot be the same as the sender.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # check if the user has enough balance
            if check_user_balance(current_user) < tx_input:
                print("Not enough balance to send the transaction.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # get the user's private key
            private_key = get_user_private_key(current_user)

            # create a new transaction
            new_tx = Tx()
            new_tx.add_input(current_user, tx_input)
            new_tx.add_output(recipient, tx_output)
            new_tx.add_fee(fee)
            new_tx.sign(private_key)

            # add the transaction to the pool
            transactions.append(new_tx)

            # write the new pool to the pool file
            with open(pool_path, 'wb') as pool_file:
                pickle.dump(transactions, pool_file)

            print("Transaction added to the pool successfully!")
            input("Press Enter to return to the main menu...")
            os.system('cls' if os.name == 'nt' else 'clear')

    def explore_blockchain():
        os.system('cls' if os.name == 'nt' else 'clear')
        # open the ledger.dat file in read mode
        ledger_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'ledger.dat')

        # check if the ledger file exists
        if not os.path.exists(ledger_path):
            print("No blocks found in the blockchain.")
            print()
            return

        # read the ledger file
        with open(ledger_path, 'rb') as ledger_file:
            try:
                blocks = pickle.load(ledger_file)
            except EOFError:
                print("No blocks found in the blockchain.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # iterate through the blocks in the blockchain
            i = len(blocks)
            while i > 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Block " + str(i))
                print("Transaction Data:")
                print()
                # print like this: <TYPE> | <AMOUNT> From <FROM> To <TO>
                for tx in blocks[i-1].data:
                    if tx.type == REWARD:
                        print("REWARD | " + str(tx.outputs[0][1]) + " From " + str(
                            tx.outputs[0][0]) + " To " + str(tx.outputs[0][0]))
                    else:
                        for addr, amount in tx.inputs:
                            print("NORMAL | " + str(amount) +
                                  " From " + str(addr), end=' ')
                        for addr, amount in tx.outputs:
                            print("To " + str(addr))
                print()
                print("Block Hash: " + str(blocks[i-1].blockHash))
                print("Previous Hash: " + str(blocks[i-1].previousHash))
                print()
                # check the amount of flags
                flag_count = blocks[i-1].flags
                if flag_count < 3:
                    print("Block has " + str(flag_count) +
                          "/3 flags, not validated yet.")
                    # run is_valid on the block to validate it
                    if blocks[i-1].is_valid():
                        # add a flag
                        blocks[i-1].flags.append(True)
                    else:
                        print("Block is not valid.")
                i -= 1
                if i != 0:
                    input("Press Enter to view the previous block...")

            input("Press Enter to return to the main menu...")
            os.system('cls' if os.name == 'nt' else 'clear')
            return

    def check_pool():
        os.system('cls' if os.name == 'nt' else 'clear')
        # open the pool.dat file in read mode
        pool_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'pool.dat')

        # check if the pool file exists
        if not os.path.exists(pool_path):
            print("No transactions found in the pool.")
            print()
            return

        # read the pool file
        with open(pool_path, 'rb') as pool_file:
            try:
                # load the transactions from the pool file
                transactions = pickle.load(pool_file)
            except EOFError:
                print("No transactions found in the pool.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # if there are no transactions in the pool, print a message and return to the main menu
            if len(transactions) == 0:
                print("No transactions found in the pool.")
                print()
                input("Press Enter to return to the main menu...")
                os.system('cls' if os.name == 'nt' else 'clear')
                return

            # iterate through the transactions in the pool
            i = 1
            for tx in transactions:
                print("Transaction " + str(i))
                print("Transaction Inputs: " + str(tx.inputs))
                print("Transaction Outputs: " + str(tx.outputs))
                print("Transaction Fee: " + str(tx.fee))
                # print("Transaction Signatures: " + str(tx.sigs))
                print()
                i += 1

        # wait for an input to return to the main menu
        input("Press Enter to return to the main menu...")

    def cancel_transaction():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Cancel a Transaction")
        # print all the transactions that the logged in user has in the pool
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'pool.dat'), 'rb') as pool_file:
            try:
                transactions = pickle.load(pool_file)
            except EOFError:
                print("No transactions found in the pool.")
                print()
                input("Press Enter to return to the main menu...")
                return

        # only print the transactions that the user has in the pool
        user_transactions = []
        for tx in transactions:
            if tx.inputs[0][0] == current_user:
                user_transactions.append(tx)

        if len(user_transactions) == 0:
            print("User does not have any transactions in the pool.")
            print()
            input("Press Enter to return to the main menu...")
            return

        i = 1
        for tx in user_transactions:
            print("Transaction " + str(i))
            print("Transaction Inputs: " + str(tx.inputs))
            print("Transaction Outputs: " + str(tx.outputs))
            print()
            i += 1

        # ask the user to choose a transaction to cancel
        choice = input("Enter the number of the transaction you want to cancel (enter 'r' to return to the main menu): ")

        # remove the transaction from the pool
        if choice == 'r':
            return
        
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid choice, please try again.")
            return

        if choice < 1 or choice > len(user_transactions):
            print("Invalid choice, please try again.")
            return

        transactions.remove(user_transactions[choice - 1])

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'pool.dat'), 'wb') as pool_file:
            pickle.dump(transactions, pool_file)

        print("Transaction cancelled successfully!")
        input("Press Enter to return to the main menu...")
        return


        # write the new pool to the pool file
        # print a message that the transaction was cancelled successfully
        # wait for an input to return to the main menu

    def mine_block():
        os.system('cls' if os.name == 'nt' else 'clear')
        # mine the first 5 transactions in the pool

        # open the pool.dat file in read mode
        pool_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'pool.dat')

        # check if the pool file exists
        if not os.path.exists(pool_path):
            print("No transactions found in the pool.")
            print()
            return

        # read the pool file
        with open(pool_path, 'rb') as pool_file:
            try:
                # load the transactions from the pool file
                transactions = pickle.load(pool_file)
                # check if there are valid transactions in the pool
                if len(transactions) == 0:
                    print("No transactions found in the pool.")
                    print()
                    input("Press Enter to return to the main menu...")
                    return
            except EOFError:
                print("No transactions found in the pool.")
                print()
                input("Press Enter to return to the main menu...")
                return

            # open the ledger.dat file in read mode
            ledger_path = os.path.join(os.path.dirname(
                os.path.dirname(__file__)), 'data', 'ledger.dat')

            # read the ledger file
            with open(ledger_path, 'rb') as ledger_file:
                try:
                    blocks = pickle.load(ledger_file)
                except EOFError:
                    blocks = []

            # print info about the transactions in the pool, and ask the user if they want to mine the block
            print("Transactions in the pool:")
            print()
            i = 1
            for tx in transactions:
                print("Transaction " + str(i))
                print("Transaction Inputs: " + str(tx.inputs))
                print("Transaction Outputs: " + str(tx.outputs))
                print()
                i += 1

            # if the pool has less than 5 transactions, tell the user that the block cannot be mined.
            if len(transactions) < 5:
                print(
                    "There are less than 5 transactions in the pool, the block cannot be mined.")
                print()
                input("Press Enter to return to the main menu...")
                return

            mine_block_choice = input(
                "Do you want to mine the block with the first 10 transactions in the pool? (y/n): ")

            if mine_block_choice != 'y':
                return

            # create a new block
            if len(blocks) == 0:
                new_block = TxBlock(None)  # Genesis block
            else:
                new_block = TxBlock(blocks[-1])

            # add the transactions to the new block
            for i, tx in enumerate(transactions):
                if i < 10:
                    new_block.addTx(tx)
                else:
                    break

            # mine the block
            start_time = time.time()
            new_block.mine(1)
            end_time = time.time()
            mining_time = "{:.1f}".format(end_time - start_time)
            print("Block mined successfully in", mining_time, "seconds!")
            new_block.minedBy = current_user
            new_block.dateOfCreation = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # validate the block
            if not new_block.is_valid():
                print("Block is not valid.")
                input("Press Enter to return to the main menu...")
                return
            
            # add the block to the ledger
            blocks.append(new_block)

            # write the new ledger to the ledger file
            with open(ledger_path, 'wb') as ledger_file:
                pickle.dump(blocks, ledger_file)

            # remove the mined transactions from the pool
            transactions = transactions[5:]

            # write the new pool to the pool file
            with open(pool_path, 'wb') as pool_file:
                pickle.dump(transactions, pool_file)

        print("Block mined successfully!")
        input("Press Enter to return to the main menu...")

    def logout():
        global is_logged_in
        global current_user
        os.system('cls' if os.name == 'nt' else 'clear')
        print("User " + current_user + " logged out successfully!")
        current_user = ""
        is_logged_in = False
        print()
        public_menu()

    def default():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Invalid choice, please try again.")
        print()

    switch = {
        '1': send_goodcoins,
        '2': explore_blockchain,
        '3': check_pool,
        '4': cancel_transaction,
        '5': mine_block,
        '6': logout
    }

    try:
        switch.get(choice, default)()
    except TypeError:
        print("Invalid choice, please try again.")


if __name__ == "__main__":
    while True:
        if is_logged_in:
            logged_in_menu()
        else:
            public_menu()