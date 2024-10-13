import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoHandler:
    """
    A class for handling cryptographic operations, including key generation, 
    shared key derivation, and message encryption using X25519 and AES-GCM.
    """

    def __init__(self):
        """
        Initializes the CryptoHandler with no key pair. The key pair must be 
        generated before performing any cryptographic operations.
        """
        self.private_key = None
        self.public_key = None

    def generate_key_pair(self) -> tuple[X25519PrivateKey, bytes]:
        """
        Generates a new X25519 key pair. This method should be recalled for every full A-B-A transaction.

        Returns:
            tuple[X25519PrivateKey, bytes]: A tuple containing the private key and the raw bytes of the public key.
        """
        self.private_key = X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key().public_bytes_raw()
        return self.private_key, self.public_key

    def derive_shared_key(self, ext_public_key: bytes) -> bytes:
        """
        Derives a shared key using the provided private key and an external public key.

        This function performs a key exchange using the X25519 algorithm to derive a shared secret key.

        Args:
            ext_public_key (bytes): The external public key in bytes format.

        Returns:
            bytes: The derived shared key.
        """
        if self.private_key is None:
            raise ValueError("Private key not generated. Call generate_key_pair() first.")
        
        return self.private_key.exchange(X25519PublicKey.from_public_bytes(ext_public_key))

    def encrypt_msg(self, shared_key: bytes, msg: bytes) -> tuple[bytes, bytes]:
        """
        Encrypts a message using a shared key with AES-GCM.

        Args:
            shared_key (bytes): The shared key used for encryption.
            msg (bytes): The message to be encrypted.

        Returns:
            tuple[bytes, bytes]: A tuple containing the nonce and the encrypted message.
        """
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_key)

        aesgcm = AESGCM(key=derived_key)
        nonce = os.urandom(12)  # never reuse nonce key combo
        encrypted_msg = aesgcm.encrypt(nonce, msg, None)  # Tag is last 16 bytes
        return nonce, encrypted_msg
    
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