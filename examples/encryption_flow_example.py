from bluebird import ClientExchangeHandler, ServerExchangeHandler, CurveType

""" 
Server is initialized with the desired curve type 
 -> Sends out server_public_key_to_send
"""
server = ServerExchangeHandler(CurveType.CURVE448)
_, server_public_key_to_send = server.generate_key_pair()
print(f"Server Public Key (bytes): {server_public_key_to_send}")


""" 
Client is initialized with the desired curve type 
 <- Receives server public key
 -> Sends out payload with client public key, encrypted password, nonce, and tag all in one
"""
client = ClientExchangeHandler(CurveType.CURVE448)
wifi_password = "MyWiFiPass12345!"
client_payload_to_send = client.create_encrypted_payload(wifi_password, server_public_key_to_send)
print(f"Payload To Send From Client to Server (bytes): {client_payload_to_send}")


""" 
Server 
 <- Receives payload and extracts plaintext in bytes
"""
decrypted_msg = server.decrypt_payload(client_payload_to_send)
print(f"Decrypted Message From Client (bytes): {decrypted_msg}")
print(f"Decrypted Message From Client: {decrypted_msg.decode()}")