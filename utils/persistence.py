"""
Data persistence utilities for blockchain voting system.
"""
import json
import os
import time
import pickle

class BlockchainPersistence:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_blockchain(self, blockchain, filename="blockchain.pickle"):
        """Save blockchain to file."""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(blockchain, f)
            return True
        except Exception as e:
            print(f"Error saving blockchain: {str(e)}")
            return False
    
    def load_blockchain(self, filename="blockchain.pickle"):
        """Load blockchain from file."""
        filepath = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    return pickle.load(f)
            return None
        except Exception as e:
            print(f"Error loading blockchain: {str(e)}")
            return None
