"""
Simple OTP code storage for testing purposes.
"""
import json
import os

OTP_FILE = "data/otp_codes.json"

def save_otp(voter_id, otp_code):
    """Save OTP code for a voter."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    codes = {}
    if os.path.exists(OTP_FILE):
        with open(OTP_FILE, 'r') as f:
            try:
                codes = json.load(f)
            except:
                # File exists but is invalid, start fresh
                codes = {}
    
    # Add the new code
    codes[voter_id] = otp_code
    
    # Save to file
    with open(OTP_FILE, 'w') as f:
        json.dump(codes, f)
    print(f"OTP code for {voter_id} saved to file")
    
def verify_otp(voter_id, otp_code):
    """Verify an OTP code for a voter."""
    if not os.path.exists(OTP_FILE):
        print("No OTP codes file exists")
        return False
    
    with open(OTP_FILE, 'r') as f:
        try:
            codes = json.load(f)
        except:
            print("Invalid OTP codes file")
            return False
    
    # Check if voter exists and codes match
    if voter_id in codes and codes[voter_id] == otp_code:
        # Remove the code after successful verification (one-time use)
        codes.pop(voter_id)
        with open(OTP_FILE, 'w') as f:
            json.dump(codes, f)
        return True
    
    return False
