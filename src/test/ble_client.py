from commision_blue.crypto_utils import ExchangeHandler

crypto_handler = ExchangeHandler()

#key generation
client_private_key, client_public_key = crypto_handler.generate_key_pair()

# recv_server_pub_key = ble_util.req_server_key() #TODO

#derive shared key from ECDH
shared_key = crypto_handler.derive_shared_key(recv_server_pub_key)

#send encrypted pass
password = b"Nicho's Kittens"
nonce, encr_msg = crypto_handler.encrypt_msg(shared_key, password)

#send [client pub key, nonce, encrypt msg (with 16 byte tag)] to server
# ble_util.send(client_public_key, nonce, encr_msg) #TODO
