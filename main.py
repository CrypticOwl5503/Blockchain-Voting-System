from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from blockchain.wallet import generate_key_pair, generate_address_from_public_key
from network.node import Node
from admin.interface import run_admin_interface
from utils.persistence import BlockchainPersistence
import sys
import threading
import time

def start_node(blockchain, port):
    """Start a P2P network node."""
    node = Node(blockchain, port=port)
    blockchain.set_network_node(node)
    node.start()
    return node

def start_admin_interface(blockchain):
    """Start the admin interface."""
    run_admin_interface(blockchain)

def start_web_frontend(blockchain):
    """Start the web frontend."""
    from frontend.app import app
    from api.routes import set_blockchain
    
    # Set blockchain instance for API
    set_blockchain(blockchain)
    
    # Run Flask app
    app.run(debug=True)

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Admin interface: python main.py admin [data_file]")
        print("  P2P node: python main.py node <port> [peer_port] [peer_host]")
        print("  Web frontend: python main.py web [port]")
        return
        
    mode = sys.argv[1]
    
    # Load or create blockchain
    persistence = BlockchainPersistence()
    blockchain = persistence.load_blockchain()
    
    if blockchain is None:
        print("Creating new blockchain...")
        blockchain = Blockchain()
    else:
        print("Loaded existing blockchain")
    
    if mode == "admin":
        # Start admin interface
        start_admin_interface(blockchain)
        
        # Save blockchain after admin session
        persistence.save_blockchain(blockchain)
        
    elif mode == "node":
        if len(sys.argv) < 3:
            print("Node mode requires a port number")
            return
            
        port = int(sys.argv[2])
        
        # Start node
        node = start_node(blockchain, port)
        
        # Connect to peer if specified
        if len(sys.argv) > 3:
            peer_port = int(sys.argv[3])
            peer_host = sys.argv[4] if len(sys.argv) > 4 else 'localhost'
            
            if peer_port != port:
                print(f"Connecting to peer at {peer_host}:{peer_port}")
                node.connect_to_peer(peer_host, peer_port)
        
        # Keep node running
        try:
            while True:
                cmd = input("Node command (q to quit): ")
                if cmd.lower() == 'q':
                    break
        except KeyboardInterrupt:
            pass
            
        # Stop node and save blockchain
        print("Stopping node...")
        node.stop()
        persistence.save_blockchain(blockchain)
        print("Blockchain saved")
    
    elif mode == "web":
        # Start web frontend
        print("Starting web frontend...")
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        
        # Start the web server
        start_web_frontend(blockchain)
        
    else:
        print(f"Unknown mode: {mode}")
        print("Use 'admin' for admin interface, 'node' for P2P node, or 'web' for web frontend")

if __name__ == "__main__":
    main()
