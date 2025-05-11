"""
Candidate management module for blockchain voting system.
"""
import json
import os

class CandidateManager:
    def __init__(self, election_manager):
        self.election = election_manager
    
    def list_candidates(self):
        """List all candidates in the election."""
        return self.election.get_candidates()
    
    def add_candidate(self, name, party=None, bio=None, image_url=None):
        """Add a new candidate to the election."""
        info = {
            "party": party,
            "bio": bio,
            "image_url": image_url
        }
        return self.election.add_candidate(name, info)
    
    def remove_candidate(self, candidate_id):
        """Remove a candidate from the election."""
        return self.election.remove_candidate(candidate_id)
    
    def update_candidate(self, candidate_id, name=None, party=None, bio=None, image_url=None):
        """Update candidate information."""
        if self.election.get_state() != "SETUP":
            return False, "Cannot update candidates after setup phase"
            
        candidates = self.election.get_candidates()
        
        for i, candidate in enumerate(candidates):
            if candidate["id"] == candidate_id:
                if name:
                    candidate["name"] = name
                
                if not candidate.get("info"):
                    candidate["info"] = {}
                    
                if party:
                    candidate["info"]["party"] = party
                if bio:
                    candidate["info"]["bio"] = bio
                if image_url:
                    candidate["info"]["image_url"] = image_url
                    
                self.election.config["candidates"][i] = candidate
                return self.election.save_config(), "Candidate updated successfully"
                
        return False, "Candidate not found"
    
    def import_candidates(self, json_file):
        """Import candidates from a JSON file."""
        if self.election.get_state() != "SETUP":
            return False, "Cannot import candidates after setup phase"
            
        if not os.path.exists(json_file):
            return False, "File not found"
            
        try:
            with open(json_file, 'r') as f:
                candidates = json.load(f)
                
            success_count = 0
            for candidate in candidates:
                if "name" in candidate:
                    name = candidate["name"]
                    info = {k: v for k, v in candidate.items() if k != "name"}
                    success, _ = self.election.add_candidate(name, info)
                    if success:
                        success_count += 1
                        
            return True, f"Imported {success_count} candidates successfully"
            
        except Exception as e:
            return False, f"Error importing candidates: {str(e)}"
