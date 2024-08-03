from cryptography.fernet import Fernet
from PIL import Image
import os

def generate_key():
    """生成并保存密钥文件"""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """加载密钥文件"""
    return open("secret.key", "rb").read()

def encrypt_image(image_path, output_path):
    """加密图像文件"""
    key = load_key()
    fernet = Fernet(key)

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    encrypted_data = fernet.encrypt(image_data)

    with open(output_path, "wb") as enc_file:
        enc_file.write(encrypted_data)

def decrypt_image(encrypted_path, output_path):
    """解密图像文件"""
    key = load_key()
    fernet = Fernet(key)

    with open(encrypted_path, "rb") as enc_file:
        encrypted_data = enc_file.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    with open(output_path, "wb") as dec_file:
        dec_file.write(decrypted_data)

def decrypt_image_to_bytes(encrypted_path):
    """解密图像文件并返回字节数据"""
    key = load_key()
    fernet = Fernet(key)

    with open(encrypted_path, "rb") as enc_file:
        encrypted_data = enc_file.read()

    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data
