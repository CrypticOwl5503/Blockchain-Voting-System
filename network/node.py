import socket
import random
from network.server import Server
from network.peer import Peer
from network.message import Message

class Node:
    
    def __init__(self, blockchain, host='0.0.0.0', port=8333):
        self.blockchain = blockchain
        self.host = host
        self.port = port
        self.server = Server(self, host, port)
        self.peers = []
        self.node_id = random.randint(1000000, 9999999)
        self.known_peers = set()
    
    def start(self):
        #starting node and P2P server
        return self.server.start()
    
    def stop(self):
        self.server.stop()
        
        for peer in list(self.peers):
            peer.disconnect()
            
        self.peers = []
    
    def connect_to_peer(self, host, port):
        peer_addr = (host, port)
        if peer_addr in [(p.address[0], p.address[1]) for p in self.peers]:
            print(f"Already connected to {host}:{port}")
            return False
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            
            self.add_incoming_peer(sock, (host, port))
            self.known_peers.add((host, port))
            
            print(f"Connected to peer {host}:{port}")
            return True
        except Exception as e:
            print(f"Error connecting to peer {host}:{port}: {str(e)}")
            return False
    
    def add_incoming_peer(self, sock, address):
        #adding a new peer
        peer = Peer(sock, address, self)
        self.peers.append(peer)
        
        self.known_peers.add((address[0], address[1]))
        
        #Requesting blockchain from new peer
        self.request_blockchain(peer)
        
        self.request_peers(peer)
    
    def remove_peer(self, peer):
        #removing peer from list
        if peer in self.peers:
            self.peers.remove(peer)
            print(f"Peer {peer.address[0]}:{peer.address[1]} disconnected")
    
    def broadcast(self, message):
        message.sender_id = self.node_id
        
        for peer in list(self.peers):
            peer.send(message)
    
    def broadcast_transaction(self, transaction):
        tx_data = transaction.to_dict()
        message = Message('NEW_TRANSACTION', tx_data, self.node_id)
        self.broadcast(message)
    
    def broadcast_block(self, block):
        block_data = block.to_dict()
        message = Message('NEW_BLOCK', block_data, self.node_id)
        self.broadcast(message)
    
    def request_blockchain(self, peer=None):
        message = Message('GET_CHAIN', {}, self.node_id)
        
        if peer:
            peer.send(message)
        else:
            self.broadcast(message)
    
    def request_peers(self, peer=None):
        message = Message('GET_PEERS', {}, self.node_id)
        
        if peer:
            peer.send(message)
        else:
            self.broadcast(message)
    
    def handle_message(self, message, peer):
        msg_type = message.msg_type
        
        if msg_type == 'GET_CHAIN':
            self.handle_get_chain(message, peer)
        elif msg_type == 'CHAIN':
            self.handle_chain(message, peer)
        elif msg_type == 'NEW_BLOCK':
            self.handle_new_block(message, peer)
        elif msg_type == 'NEW_TRANSACTION':
            self.handle_new_transaction(message, peer)
        elif msg_type == 'GET_PEERS':
            self.handle_get_peers(message, peer)
        elif msg_type == 'PEERS':
            self.handle_peers(message, peer)
    
    def handle_get_chain(self, message, peer):
        chain_data = []
        for block in self.blockchain.chain:
            chain_data.append(block.to_dict())
        
        response = Message('CHAIN', chain_data, self.node_id)
        peer.send(response)
    
    def handle_chain(self, message, peer):
        chain_data = message.data
        
        if len(chain_data) <= len(self.blockchain.chain):
            return
            
        try:
            for block_data in chain_data:
                if not all(k in block_data for k in ['index', 'timestamp', 'previous_hash', 'hash', 'transactions']):
                    print("Invalid block structure in received chain")
                    return
            
            print(f"Received longer blockchain ({len(chain_data)} blocks)")
            # TODO: Replace blockchain with received chain
        except Exception as e:
            print(f"Error processing received blockchain: {str(e)}")
    
    def handle_new_block(self, message, peer):
        block_data = message.data
        print(f"Received new block #{block_data['index']} from peer")
        # TODO: Validate and add block to chain
    
    def handle_new_transaction(self, message, peer):
        tx_data = message.data
        
        from blockchain.transaction import Transaction
        
        try:
            transaction = Transaction(
                sender=tx_data['sender'],
                recipient=tx_data['recipient'],
                data=tx_data['data'],
                signature=tx_data['signature']
            )
            
            if transaction.verify_signature():
                if self.blockchain.add_transaction(transaction):
                    print(f"Added new transaction from peer")
                    
                    for other_peer in self.peers:
                        if other_peer != peer:
                            other_peer.send(message)
            
        except Exception as e:
            print(f"Error processing transaction: {str(e)}")
    
    def handle_get_peers(self, message, peer):
        peer_list = list(self.known_peers)
        response = Message('PEERS', peer_list, self.node_id)
        peer.send(response)
    
    def handle_peers(self, message, peer):
        peer_list = message.data
        
        for peer_info in peer_list:
            try:
                host, port = peer_info
                self.known_peers.add((host, port))
                
                if random.random() < 0.3:  # 30% chance to connect
                    self.connect_to_peer(host, port)
                    
            except Exception as e:
                print(f"Error processing peer info: {str(e)}")
