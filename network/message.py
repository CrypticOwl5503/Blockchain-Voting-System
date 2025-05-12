import json
import time

class Message:
    def __init__(self, msg_type, data, sender_id=None):
        self.msg_type = msg_type
        self.data = data
        self.sender_id = sender_id
        self.timestamp = time.time()
    
    def to_json(self):
        return json.dumps({
            'msg_type': self.msg_type,
            'data': self.data,
            'sender_id': self.sender_id,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            msg_type=data['msg_type'],
            data=data['data'],
            sender_id=data['sender_id']
        )
