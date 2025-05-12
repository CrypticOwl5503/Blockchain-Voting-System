import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import base64

# Standalone functions
def generate_key_pair():
    """Generate a new RSA key pair and return (public_key, private_key)."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    # Get public key in PEM format
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # Get private key in PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return public_key.decode('utf-8'), private_key_pem.decode('utf-8')

def sign_data(data, private_key_pem):
    """Sign data with private key."""
    if not private_key_pem:
        raise ValueError("Private key is required")
    if hasattr(private_key_pem, 'private_key') and private_key_pem.private_key:
        # It's likely a Wallet object
        private_key_pem = private_key_pem.private_key
        
    if isinstance(data, str):
        data = data.encode()
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(data, signature, public_key_pem):
    """Verify the signature using the public key."""
    if not public_key_pem:
        raise ValueError("Public key is required")
    if hasattr(public_key_pem, 'public_key') and public_key_pem.public_key:
        # It's likely a Wallet object
        public_key_pem = public_key_pem.public_key
        
    if isinstance(data, str):
        data = data.encode()
    signature = base64.b64decode(signature)
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode()
    )
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def generate_address_from_public_key(public_key):
    """Generate a shortened address from a public key."""
    if not public_key:
        raise ValueError("Public key is required")
    if isinstance(public_key, str):
        public_key = public_key.encode()
    elif hasattr(public_key, 'public_key') and callable(getattr(public_key, 'public_key')):
        # It's a Wallet object
        public_key = public_key.public_key.encode()
    key_hash = hashlib.sha256(public_key).digest()
    address = base64.b64encode(key_hash).decode('utf-8')[:40]
    return address

# Wallet class
class Wallet:
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.generate_key_pair()
    
    def generate_key_pair(self):
        """Generate a new RSA key pair."""
        self.public_key, self.private_key = generate_key_pair()
    
    def generate_public_key(self):
        """Regenerate public key from private key."""
        if not self.private_key:
            raise ValueError("Private key is not set")
        private_key_obj = serialization.load_pem_private_key(
            self.private_key.encode(),
            password=None
        )
        public_key_pem = private_key_obj.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.public_key = public_key_pem.decode('utf-8')
    
    def sign_transaction(self, transaction):
        """Sign a transaction with the wallet's private key."""
        transaction_string = transaction.to_dict(for_signature=True)
        signature = self.sign_data(str(transaction_string))
        transaction.signature = signature
        return True
    
    def sign_data(self, data):
        """Sign data with the wallet's private key."""
        return sign_data(data, self.private_key)
    
    @property
    def address(self):
        """Get the wallet's address."""
        if not self.public_key:
            raise ValueError("Public key is not set")
        return generate_address_from_public_key(self.public_key)
    
    @staticmethod
    def verify_signature(data, signature, public_key_pem):
        """Verify the signature using the public key."""
        return verify_signature(data, signature, public_key_pem)
    
    @staticmethod
    def generate_address(public_key):
        """Generate a shortened address from a public key."""
        return generate_address_from_public_key(public_key)