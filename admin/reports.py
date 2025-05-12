"""
Reporting and visualization module for blockchain voting system.
"""
import json
import os
import time
import datetime
import hashlib

class ReportGenerator:
    def __init__(self, blockchain, election_manager):
        self.blockchain = blockchain
        self.election = election_manager
        
    def generate_voter_report(self, output_file="voter_report.json"):
        """Generate a report on voter registration and participation."""
        registered_voters = len(self.blockchain.voter_registry.registered_voters)
        verified_voters = len(self.blockchain.voter_registry.verified_voters)
        votes_cast = len(self.blockchain.votes_cast)
        
        report = {
            "timestamp": time.time(),
            "date": datetime.datetime.now().isoformat(),
            "election_state": self.election.get_state(),
            "registered_voters": registered_voters,
            "verified_voters": verified_voters,
            "votes_cast": votes_cast,
            "participation_rate": (votes_cast / registered_voters) if registered_voters > 0 else 0
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return True, f"Voter report generated at {output_file}"
    
    def generate_result_report(self, output_file="election_results.json"):
        
        success, results = self.election.get_results()
        
        if not success:
            return False, "Results not available yet"
            
        total_votes = sum(candidate["votes"] for candidate in results)
        
        # Add percentage to each candidate
        for candidate in results:
            candidate["percentage"] = (candidate["votes"] / total_votes) * 100 if total_votes > 0 else 0
            
        # Sort by votes (descending)
        results.sort(key=lambda x: x["votes"], reverse=True)
        
        report = {
            "timestamp": time.time(),
            "date": datetime.datetime.now().isoformat(),
            "election_title": self.election.config["title"],
            "election_state": self.election.get_state(),
            "total_votes": total_votes,
            "candidates": len(results),
            "results": results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return True, f"Election results report generated at {output_file}"
    
    def generate_blockchain_report(self, output_file="blockchain_report.json"):
       
        chain_length = len(self.blockchain.chain)
        is_valid = self.blockchain.is_chain_valid()
        
        total_transactions = 0
        votes_by_block = []
        
        for i, block in enumerate(self.blockchain.chain):
            if i == 0:  # Skip genesis block
                continue
                
            block_votes = 0
            for tx in block.transactions:
                total_transactions += 1
                if tx.sender != "BLOCKCHAIN_REWARD":
                    block_votes += 1
                    
            votes_by_block.append({
                "block_index": block.index,
                "timestamp": block.timestamp,
                "votes": block_votes,
                "hash": block.hash[:10] + "..."
            })
            
        report = {
            "timestamp": time.time(),
            "date": datetime.datetime.now().isoformat(),
            "chain_length": chain_length,
            "chain_valid": is_valid,
            "total_transactions": total_transactions,
            "votes_by_block": votes_by_block,
            "average_votes_per_block": sum(b["votes"] for b in votes_by_block) / len(votes_by_block) if votes_by_block else 0
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return True, f"Blockchain report generated at {output_file}"
    
