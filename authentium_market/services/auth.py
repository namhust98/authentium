import contextlib
import json
import time
from requests.compat import urljoin
from authentium_market.services.http_client import HttpClient
from django.conf import settings
from authentium_market.conf.aes_handlers import AESHandlers
from authentium_market.models import Token


class Auth:
    NEBULA_TOKEN = 'NEBULA_TOKEN'

    def __init__(self):
        self.aes_handler = AESHandlers()
        self.random_aes_key = settings.RANDOM_AES_KEY
        self.random_seed = json.loads(settings.RANDOM_SEED)
        self.cypher_nebula_password = settings.CYPHER_NEBULA_PASSWORD

        self.username = settings.NEBULA_USERNAME
        self.password = self.get_password(self.random_aes_key, self.random_seed, self.cypher_nebula_password)

    def get_password(self, random_aes_key, random_seed, cypher_key):
        key = self.aes_handler.convert_key(random_aes_key, random_seed)
        clean_text = self.aes_handler.decrypt_data(cypher_key, key)
        return clean_text

    def login(self):
        # TODO Base Authen for Trader
        with contextlib.suppress(Token.DoesNotExist):
            token = Token.objects.get(token_type="Admin")
            if time.time() - token.created_at.timestamp() < token.expires_in:
                return token.token
        result_json = self.__call_nebula_api(
            'auth/token',
            "Cannot login",
        )
        Token.objects.update_or_create(
            token_type="Admin",
            defaults={
                "token": result_json['token'],
                "expires_in": result_json['expiresIn']
            }
        )
        return result_json['token']

    def __call_nebula_api(self, url_path, error_message):
        url = urljoin(settings.NEBULA_URL, url_path)

        payload = {
            "email": self.username,
            "password": self.password
        }
        headers = {'Content-Type': 'application/json'}

        http = HttpClient().retry_http()
        result = http.post(url, headers=headers, data=json.dumps(payload))

        if result.status_code != 200:
            raise AuthError(result.status_code, error_message, result.reason)

        return result.json()


class AuthError(Exception):

    def __init__(self, status_code, message, errors):
        super().__init__(message)
        self.errors = errors
        self.message = message
        self.status_code = status_code
