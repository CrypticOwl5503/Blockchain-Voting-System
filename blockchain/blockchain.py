from blockchain.block import Block
from blockchain.transaction import Transaction
from mining.proof_of_work import ProofOfWork
from blockchain.voter_registry import VoterRegistry

class Blockchain:
    def __init__(self):
        # initializing chain, mempool, and difficulty
        # setting up voter tracking and network node
        self.chain = []
        self.pending_transactions = []
        self.mining_difficulty = 4
        self.voter_registry = VoterRegistry()
        self.votes_cast = set()
        self.network_node = None
        self._create_genesis_block()
        
    def set_network_node(self, node):
        # setting the node reference for network communication
        self.network_node = node
        
    def _create_genesis_block(self):
        # creating the first block of the chain with index 0 and empty txns
        genesis_block = Block(0, "0", [])
        self.chain.append(genesis_block)
        return genesis_block
    
    def get_latest_block(self):
        # fetching the last block in the current chain
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        # verifying the signature before doing anything else
        if transaction.verify_signature():
            voter_address = transaction.sender

            # checking if the sender is in the registry
            if not self.voter_registry.is_registered(voter_address):
                print(f"Voter {voter_address} is not registered.")
                return False

            # preventing the same voter from voting more than once
            if voter_address in self.votes_cast:
                print(f"Voter {voter_address} has already voted.")
                return False

            # adding transaction to the mempool and marking as voted
            self.pending_transactions.append(transaction)
            self.votes_cast.add(voter_address)

            # broadcasting the transaction if a node is connected
            if self.network_node:
                self.network_node.broadcast_transaction(transaction)

            return True

        return False
    
    def register_voter(self, voter_address):
        # adding a voter to the registry
        return self.voter_registry.register_voter(voter_address)
    
    def mine_pending_transactions(self, miner_address):
        # appending a reward transaction for the miner
        reward_transaction = Transaction(
            sender="BLOCKCHAIN_REWARD",
            recipient=miner_address,
            data={"type": "REWARD", "amount": 1}
        )
        self.pending_transactions.append(reward_transaction)
        
        # creating the new block with pending transactions
        block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            transactions=self.pending_transactions
        )
        
        # doing the actual mining using proof of work
        pow_algorithm = ProofOfWork(block, self.mining_difficulty)
        mined_block = pow_algorithm.mine()
        
        # saving the block to the chain
        self.chain.append(mined_block)

        # letting the network know about the new block
        if self.network_node:
            self.network_node.broadcast_block(mined_block)
        
        # clearing the mempool after mining
        self.pending_transactions = []
        
        return mined_block
    
    def is_chain_valid(self):
        # walking through the chain to verify hashes and proof of work
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # checking if the stored hash matches the recalculated one
            if current_block.hash != current_block.calculate_block_hash():
                return False

            # making sure the chain is linked correctly
            if current_block.previous_hash != previous_block.hash:
                return False

            # verifying that the PoW solution is still valid
            pow_algorithm = ProofOfWork(current_block, self.mining_difficulty)
            if not pow_algorithm.validate():
                return False

        return True
