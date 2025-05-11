"""
Blind signature implementation for voter privacy.
Allows voters to get their ballots signed without revealing their vote.
"""
import random
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class BlindSignature:
    def __init__(self, key_size=2048):
        # Generate election authority key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Get modulus and public exponent
        self.n = self.private_key.private_numbers().public_numbers.n
        self.e = self.private_key.private_numbers().public_numbers.e
        self.d = self.private_key.private_numbers().d
        
    def blind(self, message, blinding_factor=None):
        """
        Blind a message using a random blinding factor.
        Returns the blinded message and the blinding factor.
        """
        if blinding_factor is None:
            # Generate a random blinding factor that is coprime to n
            while True:
                r = random.randint(2, self.n - 1)
                if gcd(r, self.n) == 1:
                    break
        else:
            r = blinding_factor
            
        # Compute blinded message: m' = m * r^e mod n
        blinded_msg = (int.from_bytes(message, 'big') * pow(r, self.e, self.n)) % self.n
        
        return blinded_msg, r
        
    def sign_blinded(self, blinded_msg):
        """
        Sign a blinded message.
        This is done by the election authority.
        """
        # s' = (m')^d mod n
        return pow(blinded_msg, self.d, self.n)
        
    def unblind(self, blinded_signature, blinding_factor):
        """
        Unblind the signature.
        Done by the voter after receiving the blinded signature.
        """
        # s = s' * r^(-1) mod n
        r_inv = pow(blinding_factor, -1, self.n)
        signature = (blinded_signature * r_inv) % self.n
        
        return signature
        
    def verify_signature(self, message, signature):
        """
        Verify a signature using the public key.
        Anyone can verify this.
        """
        # Convert message to integer
        m = int.from_bytes(message, 'big')
        
        # Verify: m == s^e mod n
        m_verify = pow(signature, self.e, self.n)
        
        return m == m_verify

# Helper function for GCD
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
