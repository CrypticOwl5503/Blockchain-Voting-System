import time

class ProofOfWork:
    def __init__(self, block, difficulty):
        self.block = block
        self.difficulty = difficulty
        self.target = '0' * difficulty  
        # Target with leading zeros
        
    def mine(self):
        nonce = 0
        start_time = time.time()
        
        while True:
            self.block.nonce = nonce
            current_hash = self.block.calculate_block_hash()
            
            if current_hash.startswith(self.target):
                end_time = time.time()
                print(f"Block mined! Nonce: {nonce}, Hash: {current_hash}")
                print(f"Mining took: {end_time - start_time:.2f} seconds")
                self.block.hash = current_hash
                return self.block
                
            nonce += 1
            
    def validate(self):
        return self.block.hash.startswith(self.target)
