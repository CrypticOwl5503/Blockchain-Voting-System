from blockchain.block import Block
from blockchain.transaction import Transaction
from mining.proof_of_work import ProofOfWork
from blockchain.voter_registry import VoterRegistry

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.mining_difficulty = 4  # Difficulty target for PoW
        self.voter_registry = VoterRegistry()
        self.votes_cast = set()  # Track voters who have voted
        self.network_node = None  # Initialize network node to None
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
        """Add a transaction to the pending transaction list."""
        if transaction.verify_signature():
            # Check if voter is registered
            voter_address = transaction.sender
            if not self.voter_registry.is_registered(voter_address):
                print(f"Voter {voter_address} is not registered.")
                return False
            # Check if voter has already voted
            if voter_address in self.votes_cast:
                print(f"Voter {voter_address} has already voted.")
                return False
                
            self.pending_transactions.append(transaction)
            self.votes_cast.add(voter_address)
            
            # Broadcast after verification is successful
            if self.network_node:
                self.network_node.broadcast_transaction(transaction)
                
            return True
        return False
    
    def register_voter(self, voter_address):
        return self.voter_registry.register_voter(voter_address)
    
    def mine_pending_transactions(self, miner_address):
        """Mine pending transactions and add them to the blockchain."""
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
        """Validate the blockchain."""
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
