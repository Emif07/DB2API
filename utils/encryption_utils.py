from cryptography.fernet import Fernet

def load_key():
    """Loads the encryption key from a file."""
    return open("secret.key", "rb").read()

def encrypt_password(password, key):
    """Encrypts the password using the provided key."""
    f = Fernet(key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password.decode('utf-8')

def decrypt_password(encrypted_password, key):
    """Decrypts the password using the provided key."""
    f = Fernet(key)
    decrypted_password = f.decrypt(encrypted_password.encode()).decode('utf-8')
    return decrypted_password
