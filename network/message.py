import json
import time

class Message:
    """Message class for P2P communication in the blockchain network."""
    
    def __init__(self, msg_type, data, sender_id=None):
        self.msg_type = msg_type
        self.data = data
        self.sender_id = sender_id
        self.timestamp = time.time()
    
    def to_json(self):
        """Convert message to JSON for network transmission."""
        return json.dumps({
            'msg_type': self.msg_type,
            'data': self.data,
            'sender_id': self.sender_id,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_data):
        """Create a Message object from JSON data."""
        data = json.loads(json_data)
        return cls(
            msg_type=data['msg_type'],
            data=data['data'],
            sender_id=data['sender_id']
        )
