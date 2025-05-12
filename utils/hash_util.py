import hashlib
import json

def calculate_hash(*args):
    # Convert all arguments to strings and join
    hash_content = []
    for arg in args:
        if isinstance(arg, list):
            # For lists (like transactions), convert each item to dict if possible
            serialized_list = []
            for item in arg:
                if hasattr(item, 'to_dict'):
                    serialized_list.append(item.to_dict())
                else:
                    serialized_list.append(item)
            hash_content.append(json.dumps(serialized_list, sort_keys=True))
        elif hasattr(arg, 'to_dict'):
            # If it has to_dict method (like our custom objects)
            hash_content.append(json.dumps(arg.to_dict(), sort_keys=True))
        else:
            # Otherwise, convert to string
            hash_content.append(str(arg))
    
    # Join all strings and hash
    hash_string = "".join(hash_content)
    return hashlib.sha256(hash_string.encode()).hexdigest()
