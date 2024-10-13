import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# https://cryptography.io/en/latest/hazmat/primitives/asymmetric/x25519/
# https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM


#each full transaction has to have recreated private/public key combos


#server creates public/private key set and prepares to send public key to client
server_private_key = X25519PrivateKey.generate()
server_public_key = server_private_key.public_key()
server_sendable_pkey = server_public_key.public_bytes_raw() # 32 raw byte public key to be sent over BLE


#client creates public/private key set and shared key using server public key
password = b"Nicho's Kittens"
client_private_key = X25519PrivateKey.generate()
client_public_key = client_private_key.public_key()
client_shared_key = client_private_key.exchange(X25519PublicKey.from_public_bytes(server_sendable_pkey)) #create shared key using 32 byte key received over BLE

#client encrypts password w/ AES-256 GCM using a derivation of ECDH shared key 
aesgcm = AESGCM(key=client_shared_key) #shared key is 256 bit size #should we still use a KDF on the shared_key?
nonce = os.urandom(12) # never reuse nonce key combo
encrypted_msg = aesgcm.encrypt(nonce, password, None) #tag is last 16 bytes

#client sends nonce, encrypted_msg (ciphertext + tag), and public key to server via BLE
print('sent public_key in bytes:', client_public_key.public_bytes_raw())
print('sent nonce in bytes:', nonce)
print('sent encrypted_msg in bytes:', encrypted_msg)
print()

byte_send_packet = client_public_key.public_bytes_raw() + nonce + encrypted_msg


#testing w/ files instead of BLE
with open('encrypted_data.bin', 'wb') as file:
    file.write(byte_send_packet)
    

#server receives payload and decrypts
with open('encrypted_data.bin', 'rb') as file:
    recv_pub_key = file.read(32)
    recv_nonce = file.read(12)
    combined_msg = file.read() #msg byte length + 16 byte tag
    
print(f"Received Public Key: {recv_pub_key}")
print(f"Received Nonce: {recv_nonce}")
print(f"Received Ciphertext: {combined_msg}")
print()

server_shared_key = server_private_key.exchange(X25519PublicKey.from_public_bytes(recv_pub_key))
print(f"is server shared key the same as client?: {server_shared_key == client_shared_key}")
server_aesgcm = AESGCM(server_shared_key)
print(f"decrypted msg: {server_aesgcm.decrypt(recv_nonce, combined_msg, None)}")