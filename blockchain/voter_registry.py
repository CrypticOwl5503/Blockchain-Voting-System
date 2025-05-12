class VoterRegistry:
    def __init__(self):
        self.registered_voters = set()

    def register_voter(self, voter_address):
        if voter_address in self.registered_voters:
            return False 
        self.registered_voters.add(voter_address)
        return True

    def is_registered(self, voter_address):
        return voter_address in self.registered_voters
