from commision_blue.crypto_utils import CryptoHandler

crypto_handler = CryptoHandler()

#keys
server_private_key, server_public_key = crypto_handler.generate_key_pair()

#send server public key to client
# ble_util.send(server_public_key) #TODO


#receive full msg payload from client
# recv_pub_key, nonce, encr_msg = ble_util.req_client_payload() #TODO

#decrypt msg
shared_key = crypto_handler.derive_shared_key(server_private_key, recv_pub_key)
decr_msg = crypto_handler.decrypt_msg(shared_key, nonce, encr_msg)
print(f"Decrypted msg: {decr_msg}")

