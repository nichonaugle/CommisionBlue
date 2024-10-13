import os
from commision_blue.crypto_utils import CryptoHandler

## EXAMPLE KEY EXCHANGE FLOW W/ UTILITY USING FILES INSTEAD OF BLE ##

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"


#server and client key-exchange instances
server_crypto_handler = CryptoHandler()
client_crypto_handler = CryptoHandler()


# SERVER OPERATIONS #
server_private_key, server_public_key = server_crypto_handler.generate_key_pair() # public key is 32 raw byte to be sent over BLE

# CLIENT OPERATIONS #

#client creates public/private key set and shared key using server payload
password = b"Nicho's Kittens"
client_private_key, client_public_key = client_crypto_handler.generate_key_pair()
client_shared_key = client_crypto_handler.derive_shared_key(server_public_key)

#client now encrypts password using AES-256 GCM 
nonce, encrypted_msg = client_crypto_handler.encrypt_msg(client_shared_key, password) #nonce is 12 byte, msg is pass byte size + key (16 byte)

#client sends nonce, encrypted_msg (ciphertext + tag), and public key to server via BLE
print(f'{YELLOW}sent public_key in bytes:{RESET}', client_public_key)
print(f'{YELLOW}sent nonce in bytes:{RESET}', nonce)
print(f'{YELLOW}sent encrypted_msg in bytes:{RESET}', encrypted_msg)
print()

#create byte packet to send via BLE
byte_send_packet = client_public_key + nonce + encrypted_msg


# TEST SERVER VERIFICATION OPERATIONS (using files) #
with open('encrypted_data.bin', 'wb') as file:
    file.write(byte_send_packet)
    
with open('encrypted_data.bin', 'rb') as file:
    recv_pub_key = file.read(32)
    recv_nonce = file.read(12)
    combined_msg = file.read() #msg byte length + 16 byte tag

print(f"{YELLOW}Received Public Key:{RESET} {recv_pub_key}")
print(f"{YELLOW}Received Nonce:{RESET} {recv_nonce}")
print(f"{YELLOW}Received Ciphertext:{RESET} {combined_msg}")
print()

server_shared_key = server_crypto_handler.derive_shared_key(recv_pub_key)
print(f"{YELLOW}is server shared key the same as client?:{GREEN} {server_shared_key == client_shared_key}")
print(f"{YELLOW}decrypted msg:{GREEN} {server_crypto_handler.decrypt_msg(server_shared_key, recv_nonce, combined_msg)}")