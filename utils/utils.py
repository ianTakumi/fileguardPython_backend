from cryptography.fernet import Fernet

ENCRYPTION_KEY = b"XWv6Zz0K2bMiDzI9v6tCBf9tnokSmxzqQ9LTH2qZb0M="
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_file(file_path):
    """Encrypt the uploaded file in place."""
    with open(file_path, 'rb') as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)

    with open(file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)


def decrypt_file(file_path):
    """Return decrypted bytes of the file."""
    with open(file_path, 'rb') as enc_file:
        encrypted_data = enc_file.read()

    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data
