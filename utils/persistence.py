"""
Data persistence utilities for blockchain voting system.
"""
import json
import os
import time
import pickle

def save_blockchain_immediately(blockchain, filename="blockchain.pickle"):
    """Save blockchain immediately after important changes."""
    from cryptography.hazmat.primitives import serialization
    import copy
    import inspect
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    filepath = os.path.join(data_dir, filename)
    
    try:
        # Create a deep copy to avoid modifying the original blockchain
        blockchain_copy = copy.deepcopy(blockchain)
        
        # Function to recursively search for and serialize RSA keys in an object
        def serialize_keys_in_object(obj):
            if hasattr(obj, '__dict__'):
                for attr_name, attr_value in list(obj.__dict__.items()):
                    # Check if the attribute is an RSA key that needs serialization
                    if str(type(attr_value)).find('RSAPrivateKey') >= 0:
                        try:
                            # Serialize the private key
                            key_pem = attr_value.private_bytes(
                                encoding=serialization.Encoding.PEM,
                                format=serialization.PrivateFormat.PKCS8,
                                encryption_algorithm=serialization.NoEncryption()
                            )
                            # Replace the key with its serialized form
                            setattr(obj, attr_name, key_pem)
                        except Exception as e:
                            print(f"Warning: Could not serialize RSA key in {attr_name}: {e}")
                    elif str(type(attr_value)).find('RSAPublicKey') >= 0:
                        try:
                            # Serialize the public key
                            key_pem = attr_value.public_bytes(
                                encoding=serialization.Encoding.PEM,
                                format=serialization.PublicFormat.SubjectPublicKeyInfo
                            )
                            # Replace the key with its serialized form
                            setattr(obj, attr_name, key_pem)
                        except Exception as e:
                            print(f"Warning: Could not serialize RSA key in {attr_name}: {e}")
                    elif isinstance(attr_value, (list, tuple)):
                        # Process lists/tuples
                        for item in attr_value:
                            serialize_keys_in_object(item)
                    elif isinstance(attr_value, dict):
                        # Process dictionaries
                        for k, v in attr_value.items():
                            serialize_keys_in_object(v)
                    elif hasattr(attr_value, '__dict__'):
                        # Recursively process nested objects
                        serialize_keys_in_object(attr_value)
        
        # Start the recursive search from the blockchain object
        serialize_keys_in_object(blockchain_copy)
        
        # Save the prepared blockchain
        with open(filepath, 'wb') as f:
            pickle.dump(blockchain_copy, f)
        print("Blockchain state saved successfully")
        return True
    except Exception as e:
        print(f"Error saving blockchain: {str(e)}")
        return False



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
