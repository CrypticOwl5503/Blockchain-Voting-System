import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import base64

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
    if isinstance(public_key, str):
        public_key = public_key.encode()
        
    key_hash = hashlib.sha256(public_key).digest()
    address = base64.b64encode(key_hash).decode('utf-8')[:40]
    return address
