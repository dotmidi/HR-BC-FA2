from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import *
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import time
import datetime
import sys
import os
import sqlite3

REWARD_VALUE = 50.0
NORMAL = 0
REWARD = 1

class MiscFunctions:
    def get_user_public_key(username):
        database_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'goodchain.db')
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute(
            'SELECT * FROM registered_users WHERE username = ?', (username,))
        user = cursor.fetchone()
        return user[3]

class CBlock:
    data = None
    previousHash = None
    previousBlock = None

    def __init__(self, data, previousBlock):
        self.data = data
        self.blockHash = None
        self.previousBlock = previousBlock
        self.nonce = 0
        self.timeOfCreation = None
        self.minedBy = None
        self.flags = 0
        self.validatedBy = []
        if previousBlock != None:
            self.previousHash = previousBlock.computeHash()

    def computeHash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf8'))
        digest.update(bytes(str(self.previousHash), 'utf8'))
        digest.update(bytes(str(self.nonce), 'utf8'))
        return digest.finalize()

    def is_valid(self):
        if self.previousBlock == None:
            if self.blockHash == self.computeHash():
                return True
            else:
                return False
        else:
            # return self.previousBlock.computeHash() == self.previousHash
            current_block_validity = self.blockHash == self.computeHash()
            previous_block_validity = self.previousBlock.is_valid()
            return current_block_validity and previous_block_validity


class TxBlock (CBlock):
    def __init__(self, previousBlock):
        super(TxBlock, self).__init__([], previousBlock)

    def addTx(self, Tx_in):
        self.data.append(Tx_in)

    def is_valid(self):
        if not super(TxBlock, self).is_valid():
            return False
        for tx in self.data:
            if not tx.is_valid():
                return False
        return True

    def mine(self, leading_zero):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf-8'))
        digest.update(bytes(str(self.previousHash), 'utf-8'))

        found = False
        nonce = 0
        starttime = time.time()
        timing_variable = 1
        while not found:
            h = digest.copy()
            h.update(bytes(str(nonce), 'utf-8'))
            hash_value = h.finalize()

            # If time elapsed and difficulty_timer is less than the desired value, increase difficulty
            if (time.time() - starttime > 10 and timing_variable < 50000):
                # print("Difficulty increased")
                timing_variable *= 2  # Adjust the difficulty based on your criteria

            # Check if hash meets difficulty criteria
            if hash_value[:leading_zero] == bytes('0'*leading_zero, 'utf-8'):
                if int(hash_value[leading_zero]) < timing_variable:
                    found = True
                    self.nonce = nonce
                    break  # Exit loop if the nonce is found
            # Print the nonce being tried
            sys.stdout.write("\rNonce: " + str(nonce))
            sys.stdout.write("\tElapsed time: {:.2f}".format(
                time.time() - starttime))
            sys.stdout.flush()
            nonce += 1

        # Record mined time and compute block hash
        self.blockHash = self.computeHash()
        self.timeOfCreation = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print()


class Tx:
    inputs = None
    outputs = None
    fee = None
    sigs = None
    reqd = None

    def __init__(self, type=NORMAL):
        self.type = type
        self.inputs = []
        self.outputs = []
        self.fee = []
        self.sigs = []
        self.reqd = []

    def add_input(self, from_addr, amount):
        self.inputs.append((from_addr, amount))

    def add_output(self, to_addr, amount):
        self.outputs.append((to_addr, amount))

    def add_fee(self, fee):
        self.fee.append(fee)

    def add_reqd(self, addr):
        self.reqd.append(addr)

    def sign(self, private):
        message = self.__gather()
        newsig = Signature.sig_sign(message, private)
        self.sigs.append(newsig)

    def is_valid(self):
        if self.type == REWARD:
            if len(self.inputs) != 0 and len(self.outputs) != 1:
                return False
            return True
        else:
            total_in = 0
            total_out = 0
            message = self.__gather()
            for addr, amount in self.inputs:
                found = False
                for s in self.sigs:
                    if Signature.verify(message, s, addr):
                        found = True
                if not found:
                    # print ("No good sig found for " + str(message))
                    return False
                if amount < 0:
                    return False
                total_in = total_in + amount
            for addr in self.reqd:
                found = False
                for s in self.sigs:
                    if Signature.verify(message, s, addr):
                        found = True
                if not found:
                    return False
            for addr, amount in self.outputs:
                if amount < 0:
                    return False
                total_out = total_out + amount

            if total_out > total_in:
                # print("Outputs exceed inputs")
                return False

            return True

    def __gather(self):
        data = []
        data.append(self.inputs)
        data.append(self.outputs)
        data.append(self.reqd)
        return data

    def __repr__(self):
        repr_str = "Inputs:\n"
        for addr, amt in self.inputs:
            repr_str += str(amt) + " from " + str(addr) + "\n"
        repr_str += "Outputs:\n"
        for addr, amt in self.outputs:
            repr_str += str(amt) + " to " + str(addr) + "\n"
        repr_str += "Extra Required Signatures:\n"
        for r in self.reqd:
            repr_str += str(r) + "\n"
        repr_str += "Signatures:\n"
        for s in self.sigs:
            repr_str += str(s) + "\n"
        return repr_str


class Signature:
    def generate_keys():
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        pvc_ser = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pbc_ser = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return pvc_ser, pbc_ser

    def sig_sign(message, private_key):
        message = bytes(str(message), 'utf-8')
        private_key = serialization.load_pem_private_key(
            private_key, password=None)
        signature = private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return signature

    def verify(message, signature, pbc_ser):
        message = bytes(str(message), 'utf-8')
        loaded_pbc = MiscFunctions.get_user_public_key(pbc_ser)
        public_key = serialization.load_pem_public_key(loaded_pbc)
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except:
            print("Error executing 'public_key.verify'")
            return False