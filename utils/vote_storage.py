"""
Simple vote storage for testing purposes.
"""
import json
import os

VOTES_FILE = "data/votes.json"

def save_vote(voter_id, candidate):
    """Save a vote for a voter."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    votes = {}
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            try:
                votes = json.load(f)
            except:
                votes = {}
    
    # Add the new vote
    votes[voter_id] = candidate
    
    # Save to file
    with open(VOTES_FILE, 'w') as f:
        json.dump(votes, f)
    print(f"Vote for {candidate} by {voter_id} saved to file")
    return True
    
def get_votes():
    """Get all votes."""
    if not os.path.exists(VOTES_FILE):
        return {}
    
    with open(VOTES_FILE, 'r') as f:
        try:
            votes = json.load(f)
            return votes
        except:
            return {}

def count_votes():
    """Count the total number of votes cast."""
    votes = get_votes()
    return len(votes)

def has_voted(voter_id):
    """Check if a voter has already voted."""
    votes = get_votes()
    return voter_id in votes

def get_results():
    """Tally votes and return results."""
    votes = get_votes()
    results = {}
    
    for voter, candidate in votes.items():
        if candidate in results:
            results[candidate] += 1
        else:
            results[candidate] = 1
    
    return results
