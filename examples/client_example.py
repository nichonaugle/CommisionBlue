from bluebird import ClientExchangeHandler, CurveType

pick_your_curve = CurveType.CURVE448  # Either CurveType.CURVE25519 or CurveType.CURVE448
wifi_password = "MyWiFiPass12345!"      # Add Message to send here
public_key_from_server = b''            # Add public key here

def client_example() -> str:
    """ 
    Client is initialized with the desired curve type 
    <- Receives server public key
    -> Sends out payload with client public key, encrypted password, nonce, and tag all in one
    """
    client = ClientExchangeHandler(pick_your_curve)
    client_payload_to_send = client.create_encrypted_payload(wifi_password, public_key_from_server)
    print(f"Payload To Send From Client to Server (bytes): {client_payload_to_send}")
    return client_payload_to_send