import base64

from Crypto.Util import Counter

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class AESHandlers:
    def __init__(self):
        self.aes_mode = AES.MODE_CTR
        self.counter_size = 128

        # Size of AES key. It must be 16, 24 or 32 respectively for AES-128, AES-192 and AES-256.
        self.key_size = 32

    def get_random_key(self):
        """
        Return a random key
        :return: AES key in base64_encode format
        """
        key = get_random_bytes(self.key_size)
        str_key = base64.b64encode(key).decode("utf-8")
        return str_key

    def encrypt_data(self, data):
        """
        Encrypt string data
        :param data: data in string format
        :return: cipher text in base64_encode format + AES key in base64_encode format
        """
        base64_key = self.get_random_key()
        key = base64.b64decode(base64_key.encode("utf-8"))

        cipher = AES.new(key=key, mode=self.aes_mode, counter=Counter.new(self.counter_size))

        cipher_text = cipher.encrypt(data.encode("utf-8"))
        cipher_text = base64.b64encode(cipher_text).decode("utf-8")

        return cipher_text, base64_key

    def decrypt_data(self, cipher_key, key):
        """
        Decrypt data from cipher text in base64_encode format
        :param cipher_key: cipher text in base64_encode format
        :param key: key in base64_encode format
        :return: original data
        """
        key = base64.b64decode(key.encode("utf-8"))
        cipher_key = base64.b64decode(cipher_key.encode("utf-8"))

        cipher = AES.new(key=key, mode=self.aes_mode, counter=Counter.new(self.counter_size))
        clean_text = cipher.decrypt(cipher_key)
        clean_text = clean_text.decode("utf-8")

        return clean_text

    def convert_key(self, random_string_list, seed):
        """
        Convert key from random_string_list
        :param random_string_list: random string list (generated from swapping
        the positions of the characters in the key)
        :param seed: the array stores the positions of the key's characters
        :return: the AES key
        """
        key_list = [random_string_list[seed.index(i)] for i in range(len(seed))]
        key = "".join(key_list)
        return key
