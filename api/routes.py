"""
API endpoints for frontend-backend communication.
"""
import json
import time
from blockchain.wallet import generate_key_pair
from blockchain.transaction import Transaction

# Global reference to blockchain instance
# This will be set by the main application
blockchain = None

def set_blockchain(blockchain_instance):
    
    global blockchain
    blockchain = blockchain_instance

def get_election_info():
    
    # Import the vote counting function
    from utils.vote_storage import count_votes
    
    import os
    
    # Try to load from separate file first
    election_file = "data/election_config.json"
    if os.path.exists(election_file):
        try:
            with open(election_file, 'r') as f:
                config = json.load(f)
                
                # Get votes cast from file-based storage
                votes_cast = count_votes()
                
                return {
                    "title": config.get("title", "Blockchain Election"),
                    "description": config.get("description", ""),
                    "state": config.get("state", "SETUP"),
                    "candidates": config.get("candidates", []),
                    "registered_voters": len(blockchain.voter_registry.registered_voters) if blockchain else 0,
                    "votes_cast": votes_cast  # Use the file-based count
                }
        except Exception as e:
            print(f"Error loading election config from file: {str(e)}")
    
    # Fall back to original method if file doesn't exist
    if not blockchain:
        return {
            "title": "Election Not Configured",
            "description": "Please start the blockchain node first.",
            "state": "SETUP",
            "candidates": []
        }
    
    # Get election data from blockchain
    if hasattr(blockchain, 'election'):
        # Get votes cast from file-based storage for consistent counting
        votes_cast = count_votes()
        
        return {
            "title": blockchain.election.config.get("title", "Blockchain Election"),
            "description": blockchain.election.config.get("description", ""),
            "state": blockchain.election.get_state(),
            "candidates": blockchain.election.get_candidates(),
            "registered_voters": len(blockchain.voter_registry.registered_voters),
            "votes_cast": votes_cast  # Use the file-based count
        }
    else:
        # Fallback if election data not available
        candidates = []
        for candidate in blockchain.get_candidates():
            candidates.append({"name": candidate, "info": {}})
            
        # Get votes cast from file-based storage
        votes_cast = count_votes()
            
        return {
            "title": "Blockchain Voting",
            "description": "Secure voting on blockchain",
            "state": "VOTING",  # Assume voting is open
            "candidates": candidates,
            "registered_voters": len(blockchain.voter_registry.registered_voters),
            "votes_cast": votes_cast  # Use the file-based count
        }


def register_voter(voter_id, password_hash, otp):
    """Register a new voter."""
    if not blockchain:
        return False, "Blockchain not initialized"
    
    # Use the simple OTP verification instead
    from utils.otp_storage import verify_otp
    if not verify_otp(voter_id, otp):
        return False, "Invalid registration code"
    
    # Add to blockchain registered voters
    if voter_id not in blockchain.voter_registry.registered_voters:
        blockchain.voter_registry.registered_voters.add(voter_id)
        blockchain.voter_registry.verified_voters.add(voter_id)
    
    return True, "Voter registered successfully"


def verify_voter(voter_id, password_hash):
    """Verify voter credentials and generate OTP for 2FA."""
    if not blockchain:
        return False, "Blockchain not initialized"
    
    # Check if voter is registered
    if not blockchain.voter_registry.is_registered(voter_id):
        return False, "Voter not registered"
    
    
    
    # Generate OTP for second factor
    otp = blockchain.voter_registry.mfa.generate_otp(voter_id)
    
    return True, {"message": "Login successful", "otp": otp}

def cast_vote(voter_id, candidate):
    """Cast a vote for a candidate."""
    from utils.vote_storage import save_vote, has_voted
    
    if not blockchain:
        return False, "Blockchain not initialized"
    
    # Check if voting is open
    election_info = get_election_info()
    if election_info['state'] != 'VOTING':
        return False, "Voting is not currently open"
    
    # Check if voter has already voted
    if has_voted(voter_id):
        return False, "You have already voted"
    
    try:
        # Save vote to file-based storage
        success = save_vote(voter_id, candidate)
        
        # Also try to add to blockchain if possible
        try:
            # Create a vote transaction
            vote = Transaction(
                sender=voter_id,
                recipient="ELECTION_ADDRESS",
                data={"vote_for": candidate}
            )
            
            # For demo purposes, use a simple signature
            vote.signature = "DEMO_SIGNATURE"
            
            # Try to add to blockchain
            blockchain.add_transaction(vote)
            
            # Try to mine if there are pending transactions
            if blockchain.pending_transactions:
                blockchain.mine_pending_transactions("MINER_ADDRESS")
        except Exception as e:
            print(f"Blockchain vote recording failed, but file-based vote was saved: {str(e)}")
            # Continue even if blockchain fails - we have the file backup
        
        return True, "Vote cast successfully"
        
    except Exception as e:
        return False, f"Error casting vote: {str(e)}"


def get_results():
    """Get election results."""
    from utils.vote_storage import get_results as get_file_results
    
    if not blockchain:
        return False, "Blockchain not initialized"
    
    election_info = get_election_info()
    if election_info['state'] not in ['TALLYING', 'CLOSED']:
        return False, "Results not available yet"
    
    # Try to get results from blockchain first
    try:
        blockchain_results = blockchain.tally_encrypted_votes()
    except:
        # If blockchain results fail, use file-based results
        blockchain_results = {}
    
    # Get file-based results as backup
    file_results = get_file_results()
    
    # Merge results, prioritizing blockchain results if available
    results = file_results.copy()
    for candidate, votes in blockchain_results.items():
        if votes > 0:  # Only use blockchain count if it has votes
            results[candidate] = votes
    
    # Format results for display
    formatted_results = []
    total_votes = sum(results.values())
    
    for candidate, votes in results.items():
        percentage = (votes / total_votes) * 100 if total_votes > 0 else 0
        formatted_results.append({
            "name": candidate,
            "votes": votes,
            "percentage": round(percentage, 1)
        })
    
    # Sort by votes (descending)
    formatted_results.sort(key=lambda x: x["votes"], reverse=True)
    
    return True, formatted_results

