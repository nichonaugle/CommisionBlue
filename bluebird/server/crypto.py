import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x448 import X448PrivateKey, X448PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from bluebird.util import CurveType
from typing import Union, Tuple
    
class ServerExchangeHandler:
    """
    A class for handling cryptographic operations, including key generation, 
    shared key derivation, and message encryption using X25519 and AES-GCM or X448 and AES-GCM.

    This class supports both X25519 and X448 curves, which have different key sizes and payload sizes.
    - X25519: Public key size is 32 bytes.
    - X448: Public key size is 56 bytes.

    Note: The payload size will vary depending on the curve used.
    """

    def __init__(self, curve_type: CurveType):
        """
        Initializes the ExchangeHandler with the specified curve type. The curve type 
        determines the cryptographic curve (X25519 or X448) to be used for key generation 
        and cryptographic operations.

        Args:
            curve_type (CurveType): The type of curve to use (CurveType.CURVE25519 or CurveType.CURVE448).

        Raises:
            ValueError: If an unsupported curve type is provided.
        """
        self.curve_type = curve_type
        self.private_key = None
        self.public_key = None
        if self.curve_type == CurveType.CURVE25519:
            self.private_curve_type = X25519PrivateKey
            self.public_curve_type = X25519PublicKey
        elif self.curve_type == CurveType.CURVE448:
            self.private_curve_type = X448PrivateKey
            self.public_curve_type = X448PublicKey
        else:
            raise ValueError("Unsupported CurveType. Select either X25519 or X448")

    def generate_key_pair(self) -> Tuple[Union[X25519PrivateKey, X448PrivateKey], bytes]:
        """
        Generates a new key pair based on the specified curve type.

        Returns:
            tuple[Union[X25519PrivateKey, X448PrivateKey], bytes]: A tuple containing the private key and the raw bytes of the public key.
            
            - For CurveType.CURVE25519: The public key size is 32 bytes.
            - For CurveType.CURVE448: The public key size is 56 bytes.
        """
        self.private_key = self.private_curve_type.generate()
        self.public_key = self.private_key.public_key().public_bytes_raw()
        return self.private_key, self.public_key

    def derive_shared_key(self, ext_public_key: bytes) -> bytes:
        """
        Derives a shared key using the provided private key and an external public key.

        This function performs a key exchange using the specified curve algorithm (X25519 or X448) 
        to derive a shared secret key.

        Args:
            ext_public_key (bytes): The external public key in bytes format.

        Returns:
            bytes: The derived shared key.

        Raises:
            ValueError: If the private key has not been generated.
        """
        if self.private_key is None:
            raise ValueError("Server private key not generated. Must use generate_key_pair() first.")

        return self.private_key.exchange(self.public_curve_type.from_public_bytes(ext_public_key))
    
    def decrypt_msg(self, shared_key: bytes, nonce: bytes, encrypted_msg: bytes) -> bytes:
        """
        Decrypts a message using a shared key with AES-GCM.

        Args:
            shared_key (bytes): The shared key used for decryption.
            nonce (bytes): The nonce used during encryption.
            encrypted_msg (bytes): The encrypted message with the tag.

        Returns:
            bytes: The decrypted message.
        """
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_key)

        aesgcm = AESGCM(key=derived_key)
        decrypted_msg = aesgcm.decrypt(nonce, encrypted_msg, None)
        return decrypted_msg
    
    def decrypt_payload(self, client_payload: bytes) -> str:
        """
        Decrypts the given client payload based on the curve type.

        Args:
            client_payload (bytes): The encrypted payload from the client.

        Returns:
            str: The decrypted plaintext message.

        Raises:
            ValueError: If the curve type is not defined by the server.
        """
        if (self.curve_type == CurveType.CURVE25519):
            ext_public_key = client_payload[0:32]
            nonce = client_payload[32:44]
            message = client_payload[44:]
        elif (self.curve_type == CurveType.CURVE448):
            ext_public_key = client_payload[0:56]
            nonce = client_payload[56:68]
            message = client_payload[68:]
        else:
            raise ValueError("Curve Type not defined by the server!")
        try:
            shared_key = self.derive_shared_key(ext_public_key)
            plaintext_message = self.decrypt_msg(shared_key, nonce, message)
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

        return plaintext_message
