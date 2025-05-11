"""
Multi-factor authentication for voter verification.
"""
import hashlib
import random
import time
import qrcode
from io import BytesIO

class MultiFactorAuth:
    def __init__(self):
        self.auth_codes = {}  # Map of user_id -> (code, expiry)
        
    def generate_otp(self, user_id, expiry_seconds=300):
        """Generate a one-time password for a user."""
        # Generate a 6-digit code
        code = str(random.randint(100000, 999999))
        
        # Store code with expiry time
        expiry = time.time() + expiry_seconds
        self.auth_codes[user_id] = (code, expiry)
        
        return code
        
    def verify_otp(self, user_id, submitted_code):
        """Verify a submitted OTP code."""
        print(f"DEBUG: Verifying OTP for {user_id}. Submitted: {submitted_code}")
        print(f"DEBUG: All auth codes: {self.auth_codes}")
        
        if user_id not in self.auth_codes:
            print(f"DEBUG: No OTP found for user {user_id}")
            return False
            
        stored_code, expiry = self.auth_codes[user_id]
        print(f"DEBUG: Stored code: {stored_code}, Expiry: {expiry}, Current time: {time.time()}")
        
        # Check if code has expired
        if time.time() > expiry:
            print("DEBUG: OTP has expired")
            del self.auth_codes[user_id]
            return False
            
        # Check if code matches
        if stored_code != submitted_code:
            print("DEBUG: OTP does not match")
            return False
            
        # Code is valid - remove it to prevent reuse
        print("DEBUG: OTP verification successful")
        del self.auth_codes[user_id]
        return True

        
    def generate_qr_auth(self, user_id):
        """Generate a QR code for authentication."""
        # Create a unique secret for this user
        secret = hashlib.sha256(f"{user_id}:{time.time()}".encode()).hexdigest()
        
        # Create QR code data (normally would be a proper TOTP URI)
        qr_data = f"otpauth://totp/BlockchainVote:{user_id}?secret={secret}&issuer=BlockchainVote"
        
        # Generate QR code
        img = qrcode.make(qr_data)
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer)
        
        return buffer.getvalue(), secret
        
    def generate_auth_factors(self, voter_address):
        """Generate all authentication factors for a voter."""
        # Factor 1: OTP code
        otp = self.generate_otp(voter_address)
        
        # Factor 2: QR code for app authentication
        qr_code, secret = self.generate_qr_auth(voter_address)
        
        return {
            "otp": otp,
            "qr_code": qr_code,
            "secret": secret
        }
