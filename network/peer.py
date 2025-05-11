import socket
import threading
import time
from network.message import Message

class Peer:
    """Represents a connection to a peer in the blockchain network."""
    
    def __init__(self, sock, address, node):
        self.sock = sock
        self.address = address
        self.node = node
        self.running = True
        self.buffer = b''
        
        # Start listening for messages
        self.thread = threading.Thread(target=self._listen)
        self.thread.daemon = True
        self.thread.start()
    
    def _listen(self):
        """Listen for incoming messages from the peer."""
        while self.running:
            try:
                self.sock.settimeout(1.0)
                data = self.sock.recv(4096)
                
                if not data:
                    self.disconnect()
                    break
                
                self.buffer += data
                self._process_buffer()
                
            except socket.timeout:
                continue
            except ConnectionError:
                self.disconnect()
                break
            except Exception as e:
                print(f"Error receiving data from {self.address}: {str(e)}")
                self.disconnect()
                break
    
    def _process_buffer(self):
        """Process received data in buffer."""
        try:
            messages = self.buffer.split(b'\n')
            
            for i in range(len(messages) - 1):
                msg_data = messages[i].decode('utf-8')
                message = Message.from_json(msg_data)
                self.node.handle_message(message, self)
            
            self.buffer = messages[-1]
        except Exception as e:
            print(f"Error processing message from {self.address}: {str(e)}")
    
    def send(self, message):
        """Send a message to the peer."""
        try:
            data = message.to_json() + '\n'
            self.sock.sendall(data.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message to {self.address}: {str(e)}")
            self.disconnect()
            return False
    
    def disconnect(self):
        """Disconnect from the peer."""
        if not self.running:
            return
            
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        
        self.node.remove_peer(self)
