from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

REWARD_VALUE = 50.0
NORMAL = 0
REWARD = 1
timing_variable = 10

class CBlock:
    data = None
    previousHash = None
    previousBlock = None

    def __init__(self, data, previousBlock):
        self.data = data
        self.blockHash = None
        self.previousBlock = previousBlock
        self.nonce = 0
        if previousBlock != None:
            self.previousHash = previousBlock.computeHash()

    def computeHash(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data), 'utf8'))
        digest.update(bytes(str(self.previousHash), 'utf8'))
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


class Tx:
    inputs = None
    outputs = None
    sigs = None
    reqd = None
    def __init__(self, type = NORMAL):
        self.type = type
        self.inputs = []
        self.outputs = []
        self.sigs = []
        self.reqd = []

    def add_input(self, from_addr, amount):
        self.inputs.append((from_addr, amount))

    def add_output(self, to_addr, amount):
        self.outputs.append((to_addr, amount))

    def add_reqd(self, addr):
        self.reqd.append(addr)

    def sign(self, private):
        message = self.__gather()
        newsig = Signature.sig_sign(message, private)
        self.sigs.append(newsig)
               
    def is_valid(self):
        if self.type == REWARD:
            if len(self.inputs)!=0 and len(self.outputs)!=1:
                return False
            return True
        else:
            total_in = 0
            total_out = 0
            message = self.__gather()
            for addr,amount in self.inputs:
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
            for addr,amount in self.outputs:
                if amount < 0:
                    return False
                total_out = total_out + amount

            if total_out > total_in:
                # print("Outputs exceed inputs")
                return False
            
            return True

    def __gather(self):
        data=[]
        data.append(self.inputs)
        data.append(self.outputs)
        data.append(self.reqd)
        return data


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
        while not found:
            h = digest.copy()
            h.update(bytes(str(nonce), 'utf-8'))
            hash = h.finalize()
            if hash[:leading_zero] == bytes('0'*leading_zero, 'utf-8'):
                if int(hash[leading_zero]) < timing_variable:
                    found = True
                    self.nonce = nonce
            nonce += 1
            del h
        self.blockHash = self.computeHash()


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
        print(pbc_ser)
        public_key = serialization.load_pem_public_key(pbc_ser)
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
