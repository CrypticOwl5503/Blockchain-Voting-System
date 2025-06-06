from blockchain.blockchain import Blockchain
from blockchain.wallet import Wallet
from network.node import Node
from web.app import start_web_server
import threading
import time

def main():
    # Initializing blockchain
    blockchain = Blockchain()
    
    # Initializing network node
    node = Node(blockchain)
    blockchain.set_network_node(node)
    
    network_thread = threading.Thread(target=node.start)
    network_thread.daemon = True
    network_thread.start()
    
    # Waiting for network to initialize
    print("Starting network node...")
    time.sleep(1)
    
    # Starting web server
    print("Starting web interface on http://localhost:5000")
    start_web_server(blockchain)

if __name__ == "__main__":
    main()
