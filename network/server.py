import socket
import threading

class Server:
    # Creating the P2P server for blockchain network
    
    def __init__(self, node, host='0.0.0.0', port=8333):
        self.node = node
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.thread = None
    
    def start(self):
        # Starting the P2P server
        if self.running:
            return False
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            
            self.running = True
            
            self.thread = threading.Thread(target=self._listen)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"P2P server started on {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Error starting P2P server: {str(e)}")
            return False
    
    def _listen(self):
        # Listening for incoming connections
        self.sock.settimeout(1.0)
        
        while self.running:
            try:
                client_sock, address = self.sock.accept()
                print(f"New connection from {address[0]}:{address[1]}")
                
                self.node.add_incoming_peer(client_sock, address)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {str(e)}")
    
    def stop(self):
        # Stopping the P2P server
        self.running = False
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            
        if self.thread:
            self.thread.join(2.0)
            
        print("P2P server stopped")
