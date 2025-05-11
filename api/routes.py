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
    """Set the global blockchain instance."""
    global blockchain
    blockchain = blockchain_instance

def get_election_info():
    """Get current election information."""
    if not blockchain:
        return {
            "title": "Election Not Configured",
            "description": "Please start the blockchain node first.",
            "state": "SETUP",
            "candidates": []
        }
    
    # Get election data from blockchain
    if hasattr(blockchain, 'election'):
        return {
            "title": blockchain.election.config.get("title", "Blockchain Election"),
            "description": blockchain.election.config.get("description", ""),
            "state": blockchain.election.get_state(),
            "candidates": blockchain.election.get_candidates(),
            "registered_voters": len(blockchain.voter_registry.registered_voters),
            "votes_cast": len(blockchain.votes_cast)
        }
    else:
        # Fallback if election data not available
        candidates = []
        for candidate in blockchain.get_candidates():
            candidates.append({"name": candidate, "info": {}})
            
        return {
            "title": "Blockchain Voting",
            "description": "Secure voting on blockchain",
            "state": "VOTING",  # Assume voting is open
            "candidates": candidates,
            "registered_voters": len(blockchain.voter_registry.registered_voters),
            "votes_cast": len(blockchain.votes_cast)
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
    
    # TODO: Verify password against stored hash
    # For demo, we'll accept any password for registered voters
    
    # Generate OTP for second factor
    otp = blockchain.voter_registry.mfa.generate_otp(voter_id)
    
    return True, {"message": "Login successful", "otp": otp}

def cast_vote(voter_id, candidate):
    """Cast a vote for a candidate."""
    if not blockchain:
        return False, "Blockchain not initialized"
    
    # Check if voting is open
    election_info = get_election_info()
    if election_info['state'] != 'VOTING':
        return False, "Voting is not currently open"
    
    # Check if voter has already voted
    if voter_id in blockchain.votes_cast:
        return False, "You have already voted"
    
    try:
        # Create a vote transaction
        vote = Transaction(
            sender=voter_id,
            recipient="ELECTION_ADDRESS",
            data={"vote_for": candidate}
        )
        
        # Sign the transaction
        # In a real implementation, the frontend would sign this with the voter's private key
        # For demo purposes, we're bypassing proper signing
        vote.signature = "DEMO_SIGNATURE"
        
        # Add transaction to blockchain
        success = blockchain.add_transaction(vote)
        
        if not success:
            return False, "Failed to add vote to blockchain"
        
        # Mine the transaction immediately for demo purposes
        blockchain.mine_pending_transactions("MINER_ADDRESS")
        
        return True, "Vote cast successfully"
        
    except Exception as e:
        return False, f"Error casting vote: {str(e)}"

def get_results():
    """Get election results."""
    if not blockchain:
        return False, "Blockchain not initialized"
    
    election_info = get_election_info()
    if election_info['state'] not in ['TALLYING', 'CLOSED']:
        return False, "Results not available yet"
    
    # Get results from blockchain
    results = blockchain.tally_encrypted_votes()
    
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
