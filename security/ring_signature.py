"""
Ring signature implementation for anonymity in the tallying process.
This allows any authorized member to sign without revealing who signed.
"""
import random
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class RingSignature:
    def __init__(self, num_members=5, key_size=2048):
        # Generate key pairs for all ring members
        self.members = []
        for i in range(num_members):
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Store public key and private key numbers for ring operations
            n = private_key.private_numbers().public_numbers.n
            e = private_key.private_numbers().public_numbers.e
            d = private_key.private_numbers().d
            
            self.members.append({
                'n': n,
                'e': e,
                'd': d,
                'public_key': public_key,
                'private_key': private_key
            })
    
    def get_public_keys(self):
        """Return all public keys in the ring."""
        return [member['public_key'] for member in self.members]
    
    def sign(self, message, signer_index):
        """
        Create a ring signature for a message using the key at signer_index.
        Returns the signature and the ring of public keys.
        """
        if not 0 <= signer_index < len(self.members):
            raise ValueError("Invalid signer index")
        
        # Get signer's key
        signer = self.members[signer_index]
        
        # Convert message to bytes if it's a string
        if isinstance(message, str):
            message = message.encode()
        
        # Start with random values for each member
        k = len(self.members)
        v = random.randint(1, 2**256)
        x = [random.randint(1, 2**256) for _ in range(k)]
        
        # Compute ring function values
        y = []
        for i in range(k):
            member = self.members[i]
            # y[i] = g^x[i] mod n[i]
            y.append(pow(v, x[i], member['n']))
        
        # Compute the ring "glue" value
        glue_data = message + b''.join([str(val).encode() for val in y])
        glue = int(hashlib.sha256(glue_data).hexdigest(), 16)
        
        # Solve for the signer's x value
        r = [0] * k
        for i in range(k):
            if i != signer_index:
                r[i] = x[i]
        
        # Compute signer's r value to complete the ring
        r_sum = sum(r)
        r[signer_index] = (glue - r_sum) % (2**256)
        
        return {
            'r': r,
            'glue': glue,
            'public_keys': self.get_public_keys()
        }
    
    def verify(self, message, signature):
        """
        Verify a ring signature.
        Returns True if the signature is valid, False otherwise.
        """
        r = signature['r']
        glue = signature['glue']
        public_keys = signature['public_keys']
        
        if len(r) != len(public_keys):
            return False
        
        # Convert message to bytes if it's a string
        if isinstance(message, str):
            message = message.encode()
        
        # Recompute y values
        k = len(public_keys)
        y = []
        for i in range(k):
            # Extracting n and e from public key
            key_numbers = public_keys[i].public_numbers()
            n = key_numbers.n
            e = key_numbers.e
            
            # y[i] = v^r[i] mod n
            v = pow(2, r[i], n)
            y.append(v)
        
        # Recompute the glue value
        glue_data = message + b''.join([str(val).encode() for val in y])
        computed_glue = int(hashlib.sha256(glue_data).hexdigest(), 16)
        
        # Verify the ring is complete
        return computed_glue == glue
