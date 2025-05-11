from blockchain.wallet import generate_key_pair
public_key, private_key = generate_key_pair()
print(f"Public Key: {public_key}")
print(f"Private Key: {private_key}")
