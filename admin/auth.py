"""
Admin authentication module for blockchain voting system.
"""
import hashlib
import os
import json
import time
from security.multi_factor_auth import MultiFactorAuth

class AdminAuth:
    def __init__(self, admin_file="admin_credentials.json"):
        self.admin_file = admin_file
        self.admins = self._load_admins()
        self.mfa = MultiFactorAuth()
        self.active_sessions = {}  # token -> (admin_id, expiry)
        
    def _load_admins(self):
        """Load admin credentials from file."""
        if os.path.exists(self.admin_file):
            with open(self.admin_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_admins(self):
        """Save admin credentials to file."""
        with open(self.admin_file, 'w') as f:
            json.dump(self.admins, f, indent=2)
    
    def create_admin(self, username, password, role="admin"):
        """Create a new admin account."""
        if username in self.admins:
            return False, "Admin already exists"
            
        # Generate salt and hash password
        salt = os.urandom(16).hex()
        password_hash = self._hash_password(password, salt)
        
        # Create admin record
        self.admins[username] = {
            "password_hash": password_hash,
            "salt": salt,
            "role": role,
            "created_at": time.time()
        }
        
        self._save_admins()
        return True, "Admin created successfully"
    
    def authenticate(self, username, password):
        """Authenticate an admin."""
        if username not in self.admins:
            return False, "Invalid credentials"
            
        admin = self.admins[username]
        salt = admin["salt"]
        stored_hash = admin["password_hash"]
        
        # Check password
        if self._hash_password(password, salt) != stored_hash:
            return False, "Invalid credentials"
            
        # Generate OTP for second factor
        otp = self.mfa.generate_otp(username)
        
        return True, {"message": "OTP sent", "otp": otp}
    
    def verify_otp(self, username, otp):
        """Verify OTP and create session."""
        if username not in self.admins:
            return False, "Admin not found"
            
        if not self.mfa.verify_otp(username, otp):
            return False, "Invalid OTP"
            
        # Create session token
        token = os.urandom(32).hex()
        expiry = time.time() + 3600  # 1 hour session
        
        self.active_sessions[token] = (username, expiry)
        return True, {"token": token, "expiry": expiry}
    
    def verify_session(self, token):
        """Verify a session token is valid."""
        if token not in self.active_sessions:
            return False, "Invalid session"
            
        username, expiry = self.active_sessions[token]
        
        if time.time() > expiry:
            del self.active_sessions[token]
            return False, "Session expired"
            
        return True, {"username": username, "role": self.admins[username]["role"]}
    
    def logout(self, token):
        """End an admin session."""
        if token in self.active_sessions:
            del self.active_sessions[token]
        return True
    
    def _hash_password(self, password, salt):
        """Hash a password with salt."""
        if isinstance(password, str):
            password = password.encode()
        if isinstance(salt, str):
            salt = salt.encode()
            
        return hashlib.pbkdf2_hmac('sha256', password, salt, 100000).hex()
