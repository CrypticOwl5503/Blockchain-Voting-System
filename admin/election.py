"""
Election management module for blockchain voting system.
"""
import json
import time
import os

class Election:
    STATES = ["SETUP", "REGISTRATION", "VOTING", "TALLYING", "CLOSED"]
    
    def __init__(self, blockchain, election_file="election_config.json"):
        self.blockchain = blockchain
        self.election_file = election_file
        
        # Default election configuration
        self.config = {
            "title": "Blockchain Election",
            "description": "A secure blockchain-based election",
            "start_time": None,
            "end_time": None,
            "state": "SETUP",
            "candidates": [],
            "admin_keys": []
        }
        
        self.load_config()
    
    def load_config(self):
        
        if os.path.exists(self.election_file):
            try:
                with open(self.election_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading election config: {str(e)}")
    
    def save_config(self):
        
        try:
            # Save to the normal config file
            with open(self.election_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Also save to a separate file for the web interface
            if not os.path.exists("data"):
                os.makedirs("data")
                
            with open("data/election_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving election config: {str(e)}")
            return False
    
    def set_title(self, title):
       
        self.config["title"] = title
        return self.save_config()
    
    def set_description(self, description):
      
        self.config["description"] = description
        return self.save_config()
    
    def set_dates(self, start_time, end_time):
       
        self.config["start_time"] = start_time
        self.config["end_time"] = end_time
        return self.save_config()
    
    def change_state(self, new_state):
       
        if new_state not in self.STATES:
            return False, f"Invalid state. Must be one of: {', '.join(self.STATES)}"
            
        current_state = self.config["state"]
        valid_transition = False
        
        # Check if this is a valid state transition
        if current_state == "SETUP" and new_state in ["REGISTRATION", "VOTING"]:
            valid_transition = True
        elif current_state == "REGISTRATION" and new_state in ["VOTING", "CLOSED"]:
            valid_transition = True
        elif current_state == "VOTING" and new_state in ["TALLYING", "CLOSED"]:
            valid_transition = True
        elif current_state == "TALLYING" and new_state in ["CLOSED"]:
            valid_transition = True
        elif current_state == new_state:
            return True, f"Election already in {new_state} state"
        
        if not valid_transition:
            return False, f"Invalid state transition from {current_state} to {new_state}"
            
        self.config["state"] = new_state
        
        # Special actions for state transitions
        if new_state == "TALLYING":
            self._tally_votes()
            
        if new_state == "CLOSED":
            self.config["end_time"] = time.time()
            
        return self.save_config(), f"Election state changed to {new_state}"
    
    def get_state(self):
       
        return self.config["state"]
    
    def add_candidate(self, name, info=None):
       
        if self.config["state"] != "SETUP":
            return False, "Cannot add candidates after setup phase"
            
        # Check for duplicate
        for candidate in self.config["candidates"]:
            if candidate["name"] == name:
                return False, "Candidate already exists"
                
        self.config["candidates"].append({
            "id": len(self.config["candidates"]) + 1,
            "name": name,
            "info": info or {}
        })
        
        return self.save_config(), f"Candidate {name} added successfully"
    
    def remove_candidate(self, candidate_id):
       
        if self.config["state"] != "SETUP":
            return False, "Cannot remove candidates after setup phase"
            
        for i, candidate in enumerate(self.config["candidates"]):
            if candidate["id"] == candidate_id:
                del self.config["candidates"][i]
                return self.save_config(), f"Candidate removed successfully"
                
        return False, "Candidate not found"
    
    def get_candidates(self):
        
        return self.config["candidates"]
    
    def _tally_votes(self):
        """Tally votes and store results in election config."""
        results = self.blockchain.tally_encrypted_votes()
        
        # Map results to candidate names
        candidate_results = []
        for candidate in self.config["candidates"]:
            name = candidate["name"]
            votes = results.get(name, 0)
            candidate_results.append({
                "id": candidate["id"],
                "name": name,
                "votes": votes
            })
            
        self.config["results"] = candidate_results
        self.save_config()
        
    def get_results(self):
        """Get election results."""
        if self.config["state"] not in ["TALLYING", "CLOSED"]:
            return False, "Results not available yet"
            
        return True, self.config.get("results", [])
    
    def get_election_status(self):
        """Get comprehensive election status."""
        return {
            "title": self.config["title"],
            "description": self.config["description"],
            "state": self.config["state"],
            "start_time": self.config["start_time"],
            "end_time": self.config["end_time"],
            "registered_voters": len(self.blockchain.voter_registry.registered_voters),
            "votes_cast": len(self.blockchain.votes_cast),
            "candidates": len(self.config["candidates"]),
            "blockchain_height": len(self.blockchain.chain),
            "blockchain_valid": self.blockchain.is_chain_valid()
        }
