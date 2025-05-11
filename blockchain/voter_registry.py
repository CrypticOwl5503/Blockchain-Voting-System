from security.multi_factor_auth import MultiFactorAuth

class VoterRegistry:
    def __init__(self):
        self.registered_voters = set()
        self.mfa = MultiFactorAuth()
        self.verified_voters = set()  # Voters that have completed MFA

    def register_voter(self, voter_address):
        if voter_address in self.registered_voters:
            return False  # Already registered
        self.registered_voters.add(voter_address)
        
        # Generate authentication factors
        auth_factors = self.mfa.generate_auth_factors(voter_address)
        return True, auth_factors
    
    def verify_voter_otp(self, voter_address, otp):
        """Verify voter using OTP code."""
        if not self.is_registered(voter_address):
            return False
            
        result = self.mfa.verify_otp(voter_address, otp)
        if result:
            self.verified_voters.add(voter_address)
        return result
    
    def is_registered(self, voter_address):
        return voter_address in self.registered_voters
        
    def is_verified(self, voter_address):
        """Check if voter has completed MFA verification."""
        return voter_address in self.verified_voters
