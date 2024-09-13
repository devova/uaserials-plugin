import base64
import json

from cryptography.hazmat.primitives import ciphers, padding, hashes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def decrypt(ciphertext, iv, salt, password):
    """
    Decrypts a JSON string using AES-CBC with PBKDF2HMAC key derivation.

    Args:
        ciphertext (str): The base64-encoded ciphertext.
        iv (str): The base64-encoded initialization vector.
        salt (str): The base64-encoded salt.
        password (str): The password used for key derivation.

    Returns:
        str: The decrypted JSON string.

    Raises:
        ValueError: If the ciphertext, IV, or salt are not valid base64 strings.
        ValueError: If the password is empty.
        ValueError: If the decryption fails.
    """

    # Validate input
    if not all(isinstance(x, str) for x in (ciphertext, iv, salt)):
        raise ValueError("Ciphertext, IV, and salt must be strings.")
    if not password:
        raise ValueError("Password cannot be empty.")

    # Decode base64
    ciphertext = base64.b64decode(ciphertext)
    iv = bytes.fromhex(iv)
    salt = bytes.fromhex(salt)

    # Derive key using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,  # 256-bit key for AES-256
        salt=salt,
        iterations=0x3E7,
    )
    key = kdf.derive(password.encode())

    # Create cipher
    cipher = ciphers.Cipher(algorithm=AES(key), mode=CBC(iv))
    decryptor = cipher.decryptor()

    # Pad and decrypt
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(AES.block_size).unpadder()
    unpadded_plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    # # Decode JSON
    decrypted_json = json.loads(unpadded_plaintext.decode().strip())

    return decrypted_json
