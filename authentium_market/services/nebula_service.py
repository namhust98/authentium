import requests
import json
import logging
from requests.compat import urljoin
from rest_framework.exceptions import APIException
from .auth import Auth
from authentium_market.common.constants import NEBULA_TRADER_EXISTS, NEBULA_ACCOUNT_EXISTS
from authentium_market.services.http_client import HttpClient
from django.conf import settings
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from authentium_market.conf.exceptions import APIException
from ..constants import PlaceOrderStatus

from authentium_market.common.constants import ORDER_FLOW_DEFAULT, TRADE_FLOW_DEFAULT

logger = logging.getLogger('Log')


class NebulaService:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

    def create_account(self, data):
        url = urljoin(settings.NEBULA_URL, 'broker/accounts')

        payload = json.dumps({
            "name": data.get("name"),
            "status": data.get("status")
        })

        headers = self.get_headers()

        # Create account in Exberry
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)

        # If account already exists, return
        if (response.status_code == HTTP_500_INTERNAL_SERVER_ERROR) and \
                (response.json()["code"] == NEBULA_ACCOUNT_EXISTS):
            raise APIException(detail="Account name already exists")
        # If response code is 200, save account to Authentium database
        elif response.status_code == HTTP_200_OK:
            return response.json()

        # If response code is not 200 or 500
        else:
            raise APIException(detail="Unable to process the request")

    def update_account(self, data, pk):
        url = urljoin(settings.NEBULA_URL, f"broker/accounts/{pk}")

        payload = json.dumps({
            "name": data.get("name"),
            "status": data.get("status")
        })

        headers = self.get_headers()

        # Update account in Exberry
        http = HttpClient().retry_http()
        response = http.patch(url, headers=headers, data=payload)

        # If update account success, save it to Authentium database
        if response.status_code == HTTP_200_OK:
            return

        # If response code is not 200
        else:
            raise APIException(detail="Unable to process the request")

    def get_permission(self):
        url = urljoin(settings.NEBULA_URL, 'broker/traders/permissions')

        headers = self.get_headers()

        http = HttpClient().retry_http()
        response = http.get(url, headers=headers)

        if response.status_code == HTTP_200_OK:
            return response.json()

        else:
            raise APIException(detail="Unable to process the request")

    def create_trader(self, data, permission_list):
        url = urljoin(settings.NEBULA_URL, 'broker/traders')

        payload = json.dumps({
            "name": data.get("name"),
            "email": data.get("email"),
            "password": data.get("password"),
            "accountId": data.get("account"),
            "permissions": list(permission_list)
        })

        headers = self.get_headers()

        # Create trader in Exberry
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)

        # If trader already exists, return
        if (response.status_code == HTTP_400_BAD_REQUEST) and (response.json()["code"] == NEBULA_TRADER_EXISTS):
            raise APIException(detail=f'{response.json()["message"]}')

        # If response code is 200, save trader to Authentium database
        elif response.status_code == HTTP_200_OK:
            return response.json()

        # If response code is not 200 or 400
        else:
            raise APIException(detail="Unable to process the request")

    def update_trader(self, data, permission_list, pk):
        url = urljoin(settings.NEBULA_URL, f"broker/traders/{pk}")

        payload = json.dumps({
            "name": data.get("name"),
            "email": data.get("email"),
            "accountId": data.get("accountId"),
            "permissions": list(permission_list)
        })

        headers = self.get_headers()

        # Update trader in Exberry
        http = HttpClient().retry_http()
        response = http.put(url, headers=headers, data=payload)

        # If update account success, save it to Authentium database
        if response.status_code == HTTP_200_OK:
            return

        # If response code is not 200
        else:
            raise APIException(detail="Unable to process the request")

    def create_asset(self, data):
        url = urljoin(settings.NEBULA_URL, 'broker/assets')
        payload = json.dumps({
            "name": data.get("name"),
            "description": data.get("description"),
            "status": data.get("status"),
            "quantityPrecision": data.get("quantity_precision"),
            "totalSupply": data.get("total_supply"),
            "url": data.get("url", ""),

        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)

        if response.status_code == HTTP_200_OK:
            return response.json()
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the request. Message: {message}")

    def update_asset(self, data, asset_id):
        url = urljoin(settings.NEBULA_URL, f"broker/assets/{asset_id}")
        payload = json.dumps({
            "status": data.get("status")
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.patch(url, headers=headers, data=payload)
        if response.status_code == HTTP_200_OK:
            return
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the request. Message: {message}")

    def create_calendar(self, data):
        url = urljoin(settings.NEBULA_URL, 'calendars')
        payload = json.dumps({
            "name": data.get("name"),
            "timeZone": data.get("time_zone"),
            "marketOpen": data.get("market_open"),
            "marketClose": data.get("market_close"),
            "tradingDays": data.get("trading_days"),
            "holidays": data.get("holidays", [])
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        if response.status_code == HTTP_200_OK:
            return response.json()
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the request. Message: {message}")

    def update_calendar(self, data, calendar_id):
        url = urljoin(settings.NEBULA_URL, f"calendars/{calendar_id}")
        payload = json.dumps({
            "name": data.get("name"),
            "timeZone": data.get("time_zone"),
            "marketOpen": data.get("market_open"),
            "marketClose": data.get("market_close"),
            "tradingDays": data.get("trading_days"),
            "holidays": data.get("holidays", [])
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.put(url, headers=headers, data=payload)
        if response.status_code == HTTP_200_OK:
            return response.json()
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the request. Message: {message}")

    def create_instrument_broker(self, data):
        url = urljoin(settings.NEBULA_URL, "broker/instruments")
        payload = json.dumps({
            "exchangeInstrumentSymbol": data.get("symbol"),
            "status": data.get("status"),
            "baseAssetId": data.get("base_asset"),
            "quoteAssetId": data.get("quote_asset"),
            "orderFlow": data.get("order_flow", ORDER_FLOW_DEFAULT),
            "tradeFlow": data.get("trade_flow", TRADE_FLOW_DEFAULT),
            "description": data.get("description"),
            "imageUrls": data.get("image_urls"),
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        if response.status_code == HTTP_200_OK:
            return self.create_instrument_exchange(data, response.json())
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the create instrument in broker request. Message: {message}")

    def create_instrument_exchange(self, data, resp):
        url = urljoin(settings.NEBULA_URL, "instruments")

        payload = json.dumps({
            "symbol": data.get("symbol"),
            "quoteCurrency": resp["quoteAsset"],
            "calendarId": str(data.get("calendar_ins")),
            "pricePrecision": str(data.get("price_precision")),
            "quantityPrecision": str(data.get("quantity_precision")),
            "minQuantity": str(data.get("min_quantity")),
            "maxQuantity": str(data.get("max_quantity")),
            "status": data.get("status"),
            "description": data.get("description"),
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        if response.status_code == HTTP_200_OK:
            return resp, response.json()
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the create instrument in exchange request. Message: {message}")

    def update_instrument_broker(self, instrument_id, data):
        url = urljoin(settings.NEBULA_URL, f"broker/instruments/{instrument_id}")
        payload = json.dumps({
            "exchangeInstrumentSymbol": data["symbol"],
            "status": data["status"],
            "description": data["description"]
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.patch(url, headers=headers, data=payload)
        if response.status_code == HTTP_200_OK:
            return response.json()
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the update instrument in broker request. Message: {message}")

    def update_instrument_exchange(self, instrument_id, data, resp):

        url = urljoin(settings.NEBULA_URL, f"instruments/{instrument_id}")
        payload = json.dumps({
            "symbol": data.get("symbol"),
            "quoteCurrency": resp["quoteAsset"],
            "calendarId": str(data.get("calendar_ins")),
            "pricePrecision": str(data.get("price_precision")),
            "quantityPrecision": str(data.get("quantity_precision")),
            "minQuantity": str(data.get("min_quantity")),
            "maxQuantity": str(data.get("max_quantity")),
            "status": data.get("status"),
            "description": data.get("description"),
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.put(url, headers=headers, data=payload)
        if response.status_code == HTTP_200_OK:
            return response.json()
        message = json.loads(response.text)["message"]
        raise APIException(detail=f"Unable to process the update instrument in exchange request. Message: {message}")

    def opt_in_asset(self, account_id, asset_id):
        """
        OpIn an asset to an account
        :param asset_id: str
        :return: dict
        """
        url = urljoin(settings.NEBULA_URL, f'broker/accounts/{account_id}/opt-in')

        payload = json.dumps({
            "assetId": asset_id
        })
        headers = self.get_headers()

        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        result = json.loads(response.content)
        if response.status_code == HTTP_200_OK:
            return
        logger.debug("Opt in asset for user error:")
        if result.get("code") == 100:
            raise APIException(detail=f'{result.get("message")}')

    def send_asset(self, account_id, asset_id, amount_asset):
        """
        send asset/currency to seller/buyer
        :param asset_id: str
        :param amount_asset: int if asset is amount of products and float if currency
        :return:
        """
        url = urljoin(settings.NEBULA_URL, f'broker/accounts/{account_id}/deposit')

        payload = json.dumps({
            "assetId": asset_id,
            "amount": amount_asset
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        result = json.loads(response.content)
        if response.status_code == HTTP_200_OK:
            return result
        logger.debug("Send asset for user error:")
        if result.get("code") == 100:
            raise APIException(f'{result.get("message")}')

    def lock_asset(self, account_id, asset_id, amount_asset):
        """
        lock asset for seller or lock currency for buyer in nebula
        :param asset_id int
        :param amount_asset int
        :return results
        """
        url = urljoin(settings.NEBULA_URL, f'broker/accounts/{account_id}/withdraw')

        payload = json.dumps({
            "assetId": asset_id,
            "amount": amount_asset
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        result = json.loads(response.content)
        if response.status_code == HTTP_200_OK:
            return result
        logger.debug("Lock asset for user error:")
        if result.get("code") == 100:
            raise APIException(f'{result.get("message")}')

    def set_trading_fees(self, account_id, instrument_id, taker_fee, maker_fee):
        """
        :param instrument_id int
        :param taker_fee float
        :param maker_fee float
        :return
        """
        url = urljoin(settings.NEBULA_URL, f'broker/accounts/{account_id}/fees')

        payload = json.dumps({
            "instrumentId": instrument_id,
            "takerFee": taker_fee,
            "makerFee": maker_fee
        })
        headers = self.get_headers()

        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        result = json.loads(response.content)
        if response.status_code == HTTP_200_OK:
            return result
        logger.debug("Set trading fee for user error:")
        if result.get("code") == 100:
            raise APIException(f'{result.get("message")}')

    def place_order(self, account_id, order_type, side, instrument, quantity, price, time_in_force):
        # TODO  handle error if status code !=200
        url = urljoin(settings.NEBULA_URL, f'broker/accounts/{account_id}/orders')

        payload = json.dumps({
            "orderType": order_type,
            "side": side,
            "instrument": instrument,
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force
        })
        headers = self.get_headers()
        http = HttpClient().retry_http()
        response = http.post(url, headers=headers, data=payload)
        result = json.loads(response.content)
        if response.status_code == HTTP_200_OK:
            return result
        if response.status_code == 500 and result.get("code") == PlaceOrderStatus.MISSING_INVALID_PARAM.value:
            raise APIException(f'{result.get("message")}')
        if response.status_code == 500 and result.get("code") == PlaceOrderStatus.MARKET_CLOSE.value:
            raise APIException(f'{result.get("message")}')
        logger.debug("Opt in asset for user error:")
        if result.get("code") == PlaceOrderStatus.MISSING_INVALID_PARAM.value or \
                result.get("code") == PlaceOrderStatus.INSTRUMENT_NOT_FOUND.value or \
                result.get("code") == PlaceOrderStatus.ACCOUNT_NOT_OPT_IN.value or \
                result.get("code") == PlaceOrderStatus.INSUFFICIENT_BALANCE.value:
            raise APIException(f'{result.get("message")}')

    def cancel_place_order(self, account_id, order_id, instrument):
        url = urljoin(settings.NEBULA_URL, f'broker/accounts/{account_id}/orders/{order_id}')
        payload = json.dumps({
            "instrument": instrument,
        })
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        http = HttpClient().retry_http()
        response = http.delete(url, headers=headers, data=payload)
        result = json.loads(response.content)
        if response.status_code == HTTP_200_OK:
            return result
        logger.debug("Opt in asset for user error:")
        if result.get("code") == PlaceOrderStatus.MISSING_INVALID_PARAM.value or result.get(
                "code") == PlaceOrderStatus.INSTRUMENT_NOT_FOUND.value:
            raise APIException(f'{result.get("message")}')
