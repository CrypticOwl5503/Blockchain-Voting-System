import json
from utils.hash_util import calculate_hash

class Transaction:
    def __init__(self, sender, recipient, data, signature=None):
        # setting up transaction participants and payload
        self.sender = sender
        self.recipient = recipient
        self.data = data
        self.signature = signature
    
    def calculate_hash(self):
        # generating hash using transaction content
        return calculate_hash(
            self.sender,
            self.recipient,
            json.dumps(self.data, sort_keys=True)
        )
    
    def sign_transaction(self, private_key):
        # signing the transaction using sender's private key
        from blockchain.wallet import sign_data
        transaction_hash = self.calculate_hash()
        self.signature = sign_data(transaction_hash, private_key)
        
    def verify_signature(self):
        # checking if the signature is valid
        if self.sender == "BLOCKCHAIN_REWARD":
            return True

        from blockchain.wallet import verify_signature
        transaction_hash = self.calculate_hash()
        return verify_signature(transaction_hash, self.signature, self.sender)
        
    def to_dict(self):
        # converting the transaction into a serializable dict
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'data': self.data,
            'signature': self.signature
        }
