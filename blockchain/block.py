import time
from utils.hash_util import calculate_hash

class Block:
    def __init__(self, index, previous_hash, transactions, timestamp=None, nonce=0):
        self.index = index
        self.timestamp = timestamp if timestamp else time.time()
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_block_hash()
        
    def calculate_block_hash(self):
        # generating the hash for the block using all key attributes
        return calculate_hash(
            self.index,
            self.previous_hash,
            self.timestamp,
            self.transactions,
            self.nonce
        )
    
    def to_dict(self):
        # converting block into a dictionary, mostly for serialization
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'nonce': self.nonce,
            'hash': self.hash
        }
