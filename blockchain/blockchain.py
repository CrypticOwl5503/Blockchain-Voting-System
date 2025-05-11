from blockchain.block import Block
from blockchain.transaction import Transaction
from mining.proof_of_work import ProofOfWork
from blockchain.voter_registry import VoterRegistry
from security.homomorphic import HomomorphicEncryption
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.mining_difficulty = 4  # Difficulty target for PoW
        self.voter_registry = VoterRegistry()
        self.votes_cast = set()  # Track voters who have voted
        self.network_node = None  # Initialize network node to None
        self.homomorphic = HomomorphicEncryption()
        self.encrypted_tallies = {}  # Holds encrypted vote counts by candidate
        self._create_genesis_block()
        
    def set_network_node(self, node):
        """Set the network node for this blockchain."""
        self.network_node = node
        
    def _create_genesis_block(self):
        """Create the first block in the chain."""
        genesis_block = Block(0, "0", [])
        self.chain.append(genesis_block)
        return genesis_block
    
    def get_latest_block(self):
        """Return the most recent block in the chain."""
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        """
        Add a transaction to the pending transaction list.
        Includes verification, voter validation, and vote encryption.
        """
        if transaction.verify_signature():
            # Skip voter validation for blockchain reward transactions
            if transaction.sender == "BLOCKCHAIN_REWARD":
                self.pending_transactions.append(transaction)
                return True
                
            # Check if voter is registered
            voter_address = transaction.sender
            if not self.voter_registry.is_registered(voter_address):
                print(f"Voter {voter_address} is not registered.")
                return False
                
            # Check if voter is verified with MFA
            if not self.voter_registry.is_verified(voter_address):
                print(f"Voter {voter_address} has not completed MFA verification.")
                return False
                
            # Check if voter has already voted
            if voter_address in self.votes_cast:
                print(f"Voter {voter_address} has already voted.")
                return False
            
            # Encrypt the vote data before adding to blockchain
            if "vote_for" in transaction.data:
                candidate = transaction.data["vote_for"]
                candidates = self.get_candidates()
                
                # Ensure the candidate exists in our list
                if candidate not in candidates:
                    candidates.append(candidate)
                
                # Create encrypted votes for each candidate (1 for chosen, 0 for others)
                encrypted_votes = {}
                for c in candidates:
                    encrypted_vote = self.homomorphic.encrypt_vote(candidate, c)
                    encrypted_votes[c] = encrypted_vote
                    
                # Update the transaction data to contain encrypted votes
                transaction.data["encrypted_votes"] = encrypted_votes
                transaction.data.pop("vote_for")  # Remove the plaintext vote
            
            self.pending_transactions.append(transaction)
            self.votes_cast.add(voter_address)
            
            # Broadcast after verification is successful
            if self.network_node:
                self.network_node.broadcast_transaction(transaction)
                
            return True
        return False
    
    def register_voter(self, voter_address):
        """
        Register a new voter and generate authentication factors.
        Returns (success, auth_factors) tuple.
        """
        return self.voter_registry.register_voter(voter_address)
    
    def mine_pending_transactions(self, miner_address):
        """
        Mine pending transactions and add them to the blockchain.
        Returns the mined block.
        """
        if not self.pending_transactions:
            print("No transactions to mine")
            return None
            
        # Create reward transaction for the miner
        reward_transaction = Transaction(
            sender="BLOCKCHAIN_REWARD",
            recipient=miner_address,
            data={"type": "REWARD", "amount": 1}
        )
        self.pending_transactions.append(reward_transaction)
        
        # Create a new block
        block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            transactions=self.pending_transactions
        )
        
        # Mine the block (find a valid nonce)
        pow_algorithm = ProofOfWork(block, self.mining_difficulty)
        mined_block = pow_algorithm.mine()
        
        # Add the mined block to the chain
        self.chain.append(mined_block)
        
        # Broadcast the newly mined block to the network
        if self.network_node:
            self.network_node.broadcast_block(mined_block)
        
        # Reset pending transactions
        self.pending_transactions = []
        
        return mined_block
    
    def is_chain_valid(self):
        """
        Validate the blockchain.
        Checks hash integrity, previous hash references, and proof of work.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verify block's hash
            if current_block.hash != current_block.calculate_block_hash():
                return False
                
            # Verify previous hash reference
            if current_block.previous_hash != previous_block.hash:
                return False
                
            # Verify proof of work
            pow_algorithm = ProofOfWork(current_block, self.mining_difficulty)
            if not pow_algorithm.validate():
                return False
                
        return True
        
    def tally_encrypted_votes(self):
        """
        Tally the encrypted votes using homomorphic properties.
        Returns a dictionary of candidate -> vote count.
        """
        candidates = self.get_candidates()
        tally = {c: [] for c in candidates}
        
        # Collect all encrypted votes from the blockchain
        for block in self.chain[1:]:  # Skip genesis block
            for tx in block.transactions:
                if tx.sender != "BLOCKCHAIN_REWARD" and "encrypted_votes" in tx.data:
                    encrypted_votes = tx.data["encrypted_votes"]
                    for candidate, enc_vote in encrypted_votes.items():
                        if candidate in tally:
                            tally[candidate].append(enc_vote)
        
        # Aggregate encrypted votes for each candidate
        results = {}
        for candidate, votes in tally.items():
            if votes:
                aggregated = self.homomorphic.aggregate_encrypted_votes(votes)
                decrypted = self.homomorphic.decrypt_sum(aggregated)
                results[candidate] = decrypted
            else:
                results[candidate] = 0
        
        return results

    def get_candidates(self):
        """
        Get a list of all candidates from transactions.
        Returns a list of candidate names.
        """
        candidates = set()
        
        # Check pending transactions
        for tx in self.pending_transactions:
            if "vote_for" in tx.data:
                candidates.add(tx.data["vote_for"])
        
        # Check blockchain
        for block in self.chain[1:]:  # Skip genesis block
            for tx in block.transactions:
                if tx.sender != "BLOCKCHAIN_REWARD":
                    if "vote_for" in tx.data:
                        candidates.add(tx.data["vote_for"])
                    elif "encrypted_votes" in tx.data:
                        for candidate in tx.data["encrypted_votes"].keys():
                            candidates.add(candidate)
        
        return list(candidates) if candidates else ["Candidate 1", "Candidate 2"]
        
    def replace_chain(self, new_chain):
        """
        Replace the current chain with a new one if it's longer and valid.
        Used in network consensus to sync with other nodes.
        """
        # Check if new chain is longer than the current one
        if len(new_chain) <= len(self.chain):
            return False
            
        # Check if the new chain is valid
        if not self.is_chain_valid():
            return False
            
        # Replace the chain
        self.chain = new_chain
        
        # Rebuild the votes_cast set to prevent double voting
        self.votes_cast = set()
        for block in self.chain[1:]:  # Skip genesis block
            for tx in block.transactions:
                if tx.sender != "BLOCKCHAIN_REWARD":
                    self.votes_cast.add(tx.sender)
                    
        return True
        
    def add_block(self, block):
        """
        Add a block received from the network.
        Validates the block before adding it.
        """
        # Check if the block index is valid
        if block.index != len(self.chain):
            return False
            
        # Check if previous hash references the last block in our chain
        if block.previous_hash != self.get_latest_block().hash:
            return False
            
        # Verify the block's hash
        if block.hash != block.calculate_block_hash():
            return False
            
        # Verify proof of work
        pow_algorithm = ProofOfWork(block, self.mining_difficulty)
        if not pow_algorithm.validate():
            return False
            
        # Add the block to the chain
        self.chain.append(block)
        
        # Update votes_cast set
        for tx in block.transactions:
            if tx.sender != "BLOCKCHAIN_REWARD":
                self.votes_cast.add(tx.sender)
                
        return True
        
    def get_chain_data(self):
        """
        Get a serializable representation of the blockchain.
        Used for network transmission.
        """
        chain_data = []
        for block in self.chain:
            chain_data.append(block.to_dict())
        return chain_data
