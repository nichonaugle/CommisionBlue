![bluebird open source BLE commissioning](images/bluebird.png)
# **BLE Commissioning Service with ECDH and AES-GCM**

This open source Python service runs over **D-Bus** and uses **BLE (Bluetooth Low Energy)** to allow devices like a Linux server or SBC (like a raspberry pi) to be **commissioned** securely with encrypted network credentials using **asymmetric** cryptography (ECDH with X25519 or X448) for the shared key and **symmetric** encryption (AES-256 in GCM mode) for sending credentials. The service advertises the public key over BLE, allowing a client (e.g., a Mobile application) to securely encrypt credentials that can only be decrypted by the server in a one way transaction. Protection measures are also improved through server side public key cycling if an unsuccessful commissioning attempt occurs and message authentication codes in the encrypted AES payload to prevent attacks. Furthermore, the selected encryption techniques optimize the avaliable resources on edge computers and most BLE protocols with minimal configuration required, streamlining implementation.

## Overview
--------

### Key Concepts:

1.  **ECDH (Elliptic Curve Diffie-Hellman) with X25519 Curve**:
    -   **ECDH** is an asymmetric cryptography technique used for generating shared secrets between two parties over a public network. In this implementation, the X25519 curve is chosen for its security and performance benefits. Reference [Elliptic Curves for Security - RFC7748][2]
    -   **X25519** is a highly secure elliptic curve, offering a 128-bit security level, which is resistant to both classical and newer quantum attacks. You can find more information in the [NIST Status Update on Elliptic Curves and Post-Quantum Cryptography][1].
2.  **AES-256 in GCM Mode**:
    -   **AES (Advanced Encryption Standard)** is used for symmetric encryption of sensitive data (like passwords). AES-256 refers to the 256-bit key size, providing a high level of security.
    -   **GCM (Galois/Counter Mode)** provides both encryption and integrity, ensuring the data is encrypted while also protecting against tampering.
3.  **BLE Characteristics**:
    -   The following characteristics are exposed over BLE:
        -   **SSID**: Transmitted in plaintext.
        -   **Password**: Encrypted with AES-256.
        -   **Public Key**: Server public key, hashed and refreshed with every communication, ensuring security for each transaction.
        -   **Client Public Key**: Client public key, hashed and refreshed with every communication, ensuring security for each transaction.

### Process Flow:
1.  **ECDH Key Exchange**:
    -   The service uses **ECDH** with **X25519** or **X448**to generate a public-private key pair on the server.
    -   The server advertises its **public key** as a BLE characteristic.
    -   The client (e.g., a smartphone application) retrieves this **public key**.
2.  **Client Key Generation**:
    -   The client also generates its **own ECDH key pair**.
    -   Using ECDH, the client combines its private key with the server's public key to compute the **shared secret**.
    -   This shared secret will be the **symmetric key** used for AES encryption.
3.  **AES Encryption with Shared Secret**:
    -   The client encrypts the password using **AES-256 in GCM mode**. The shared secret derived from ECDH is used as the encryption key.
    -   AES-GCM not only encrypts the password but also provides integrity checks, preventing tampering during transmission, and stores **IV** in the payload.
4.  **Data Transmission**:
    -   The **SSID** is sent in plaintext over BLE as a characteristic.
    -   The **encrypted password** is sent as a BLE characteristic, where the server can decrypt it with the matching shared secret.
    -   The **client public key** is sent as a BLE characteristic, allowing the server to derive the shared key
    -   The **client AES payload** is sent as a BLE characteristic, allowing the server to decrypt the **encrypted password**
5.  **Server Decryption**:
    -   Once all characteristics have been written to, the server uses its ECDH private key combined with the client's public key to compute the same shared secret.
    -   This shared secret, along with the AES paylod, is then used to decrypt the password, enabling secure commissioning of the device.

### Mathematical Concepts Explained:
-   **Elliptic Curve Diffie-Hellman (ECDH)**:
    -   ECDH allows two parties (server and client) to establish a shared secret over an insecure channel.
    -   Both parties generate key pairs using the elliptic curve X25519 or X448.
    -   The server's private key $$k_{\text{server}}$$ and public key $$P_{\text{server}} = k_{\text{server}} \cdot G$$ where $$G$$ is the agreed generator point on the curve.
    -   The client's private key $$k_{\text{client}}$$ and public key $$P_{\text{client}} = k_{\text{client}} \cdot G$$.
    -   The shared secret is derived as: $$S_{\text{shared}} = k_{\text{server}} \cdot P_{\text{client}} = k_{\text{client}} \cdot P_{\text{server}}$$
-   **AES-256 with GCM Mode**:
    -   AES-256 is a symmetric cipher that encrypts data in blocks using a 256-bit key.
    -   GCM mode enhances AES by incorporating both encryption and integrity (via a Message Authentication Code or MAC). It ensures that encrypted data hasn't been altered during transmission.
    -   Encryption uses the shared secret from ECDH as the AES key, ensuring that only devices with the matching shared secret can decrypt the message.

### Security Considerations:
1.  **Elliptic Curve ED25519**:
    -   X25519 is a highly secure elliptic curve, resistant to many classical and quantum attacks. Its use ensures strong protection against potential vulnerabilities in lower-security curves like P-256.
2.  **Asymmetric Key Generation and Exchange**:
    -   The use of ECDH with X25519 allows the creation of a shared secret that never needs to be transmitted over the air, significantly reducing the risk of interception by an attacker.
3.  **AES-256 Encryption**:
    -   AES-256 provides a high level of security, and when combined with GCM, it ensures that data is both confidential and tamper-resistant to many common attacks.
4.  **Public Key Hashing**:
    -   The Server's public key is hashed with every communication to prevent replay attacks and ensure that each session is unique and secure.

### BLE Characteristics Summary:

| Characteristic | Description | Security | Type |
| --- | --- | --- | --- |
| SSID | Plaintext SSID for the device network | Plaintext | Write |
| Password | AES-256 GCM encrypted password | Encrypted | Write |
| Public Key | Server's ECDH public key, hashed per use | Plaintext | Read |
| Client Public Key | Client's ECDH public key, hashed per use | Plaintext | Write |
| Client AES Payload | Client's AES Payload, hashed per use | Plaintext | Write |

### Pre-requisites:
Install the following packages
sudo apt install build-essential libpython3-dev libdbus-1-dev libdbus-glib-1-dev libgirepository1.0-dev python3-gi python3-gi-cairo gir1.2-gtk-3.0 libcairo2-dev libxt-dev
Then install the requirements.txt
pip install -r requirements.txt
### Future Enhancements:

-   Integration of additional security checks (e.g., HMAC for further integrity verification).
-   Extension of the service to support additional device configuration parameters.
-   Developing sublibararies to support Flutter, Swift and Kotlin for easy mobile applicaiton integration

[1]: https://csrc.nist.gov/CSRC/media/Presentations/NIST-Status-Update-on-Elliptic-Curves-and-Post-Qua/images-media/moody-dustin-threshold-crypto-workshop-March-2019.pdf
[2]: https://www.rfc-editor.org/rfc/rfc7748
