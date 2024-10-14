from bluebird import ServerExchangeHandler, CurveType

pick_your_curve = CurveType.CURVE448  # Either CurveType.CURVE25519 or CurveType.CURVE448

def server_setup() -> bytes:
    """ 
    Server is initialized with the desired curve type 
    -> Sends out server_public_key_to_send
    """
    server = ServerExchangeHandler(pick_your_curve)
    _, server_public_key_to_send = server.generate_key_pair()
    print(f"Server Public Key (bytes): {server_public_key_to_send}")
    return server_public_key_to_send

def server_decrypt_payload() -> str:
    """ 
    Server 
    <- Receives payload and extracts plaintext in bytes
    """
    decrypted_msg = server.decrypt_payload(client_payload_to_send)
    print(f"Decrypted Message From Client (bytes): {decrypted_msg}")
    print(f"Decrypted Message From Client: {decrypted_msg.decode()}")
    return decrypted_msg.decode()

