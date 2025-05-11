import json
from utils.hash_util import calculate_hash

class Transaction:
    def __init__(self, sender, recipient, data, signature=None):
        self.sender = sender
        self.recipient = recipient
        self.data = data  # For a vote, this could be candidate ID or name
        self.signature = signature
    
    def calculate_hash(self):
        """Calculate hash of the transaction."""
        return calculate_hash(
            self.sender,
            self.recipient,
            json.dumps(self.data, sort_keys=True)
        )
    
    def sign_transaction(self, private_key):
        """Sign the transaction with sender's private key."""
        from blockchain.wallet import sign_data
        transaction_hash = self.calculate_hash()
        self.signature = sign_data(transaction_hash, private_key)
        
    def verify_signature(self):
        """Verify the transaction signature."""
        if self.sender == "BLOCKCHAIN_REWARD":
            return True  # System rewards don't need signatures
            
        from blockchain.wallet import verify_signature
        transaction_hash = self.calculate_hash()
        return verify_signature(transaction_hash, self.signature, self.sender)
        
    def to_dict(self):
        """Convert transaction to dictionary for serialization."""
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'data': self.data,
            'signature': self.signature
        }
