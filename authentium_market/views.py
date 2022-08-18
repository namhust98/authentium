from drf_yasg.utils import swagger_auto_schema
from .form.place_order_form import PlaceOrderSerializer, TradingFeeSerializer, CancelPlaceOrderSerializer, \
    OptInSerializer
from .form.instrument_form import InstrumentSerializer, UpdateInstrumentSerializer
from .form.asset import AssetSerializer, AssetCreateSerializer, AssetUpdateSerializer
from .form.calendar import CalendarSerializer, CalendarViewSerializer
from .form.account_form import (
    AccountSerializer,
    RequestAccountSerializer,
    PermissionSerializer,
    RequestPermissionSerializer,
)
from .form.trader_form import (
    TraderSerializer,
    CreateTraderSerializer,
    UpdateTraderSerializer,
)
from .form import BaseSerializer

from .models import Order, TradingFee, Balance, Instrument
from django.db.models import Q
from .constants import Side
from rest_framework.generics import get_object_or_404
from authentium_market.conf.exceptions import APIException
from authentium_market.conf.handlers import json_response
from authentium_market.services.auth import Auth
from django.core.paginator import Paginator, InvalidPage
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from authentium_market.services.nebula_service import NebulaService
from authentium_market.models import Asset, Calendar, Account, Permission, Trader
from authentium_market.common.constants import DATA_PER_PAGE_DEFAULT, PAGE_DEFAULT


class AssetView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=AssetUpdateSerializer)
    def patch(self, request, pk, *args, **kwargs):
        """
        Update an existing asset in Exberry and save its information to Authentium database.
        Example request:
            {
                "status": "Disabled"
            }
        """
        asset = get_object_or_404(Asset, id=pk)

        form = AssetUpdateSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)

        self.nebula_service.update_asset(form.data, asset.asset_id)
        asset.status = form.data.get("status")
        asset.save()
        return json_response(status_code=HTTP_204_NO_CONTENT)

    # get an asset with id
    def get(self, request, pk):
        """
        Get information of an asset in Authentium using id
        """
        asset = get_object_or_404(Asset, id=pk)
        asset_response = AssetSerializer(asset)
        return json_response(data=asset_response.data)


# include create an asset and get all assets
class AssetsView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=AssetCreateSerializer)
    def post(self, request, *args, **kwargs):
        """
        Create a new asset in Exberry and save its information to Authentium's database
        Example request's body
        {
           "name": "Pine"
           "description": "Pineapple"
           "status": "Active"
           "quantity_precision": 5
           "total_supply": 1000
           "url": "https://algoexplorer.io/",
           "is_currency": true
        }
        :return: HTTP response status code
        """
        form = AssetCreateSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        if not form.data.get("is_currency") and form.data.get("quantity_precision") > 0:
            raise APIException(detail="Only currency assets can have decimals")
        asset_data = self.nebula_service.create_asset(form.data)
        # create asset record in database
        Asset(
            asset_id=asset_data["id"],
            name=asset_data["name"],
            description=asset_data["description"],
            ledger_system=asset_data["ledgerSystem"],
            ledger_asset_id=asset_data["ledgerAssetId"],
            quantity_precision=asset_data["quantityPrecision"],
            total_supply=asset_data["totalSupply"],
            status=asset_data["status"],
            url=asset_data["url"]
        ).save()
        return json_response(status_code=HTTP_201_CREATED)

    @swagger_auto_schema(query_serializer=BaseSerializer())
    def get(self, request):
        """
            Get all assets data
            Parameter:
            - "page": page number
            - "per_page": data per page
        """
        page = request.data.get("page", PAGE_DEFAULT)
        per_page = request.data.get("per_page", DATA_PER_PAGE_DEFAULT)
        assets = Asset.objects.all().order_by('id')
        try:
            paginator_asset = Paginator(assets, per_page)
            assets = paginator_asset.get_page(page)
        except InvalidPage as e:
            raise APIException(e)
        response = AssetSerializer(assets, many=True).data
        return json_response(data=response, pagination=assets)


# Accounts API
class AccountsView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=RequestAccountSerializer)
    def post(self, request):
        """
        Create account in Exberry and save this information to Authentium database.
        Example request:
            {
                "name": "Account1",
                "status": "Pending"
            }
        """
        # Parse request
        form = RequestAccountSerializer(data=request.data)

        if not form.is_valid():
            raise APIException(params=form.errors)

        account_data = self.nebula_service.create_account(form.data)

        Account(
            account_id=account_data["id"],
            name=account_data["name"],
            status=account_data["status"],
            ledger_system=account_data["ledgerSystem"],
            ledger_account_id=account_data["ledgerAccountId"],
            comp_id=account_data["compId"],
        ).save()

        return json_response(status_code=HTTP_201_CREATED)

    @swagger_auto_schema(query_serializer=BaseSerializer())
    def get(self, request):
        """
        Get all account data
        Parameter:
        - "page": page number
        - "per_page": data per page
        """
        page = request.data.get("page", PAGE_DEFAULT)
        per_page = request.data.get("per_page", DATA_PER_PAGE_DEFAULT)

        accounts = Account.objects.all()

        try:
            paginator_account = Paginator(accounts, per_page)
            accounts = paginator_account.get_page(page)
        except InvalidPage as e:
            raise APIException(e)

        response = AccountSerializer(accounts, many=True).data

        return json_response(data=response, pagination=accounts)


# Account API
class AccountView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    def get(self, request, pk):
        """
        Get account from Authentium database using "id"
        """
        # Get account using id
        account = get_object_or_404(Account, id=pk)
        return json_response(data=AccountSerializer(account).data)

    @swagger_auto_schema(request_body=RequestAccountSerializer)
    def patch(self, request, pk):
        """
        Update an existing account in Exberry and save this information to Authentium database.
        Example request:
            {
                "name": "Account1",
                "status": "Pending"
            }
        """
        # Find the account with id
        account = get_object_or_404(Account, id=pk)

        form = RequestAccountSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        self.nebula_service.update_account(form.data, account.account_id)
        account.name = form.data.get("name")
        account.status = form.data.get("status")
        account.save()
        return json_response(status_code=HTTP_204_NO_CONTENT)


# Permission API
class PermissionView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(query_serializer=RequestPermissionSerializer())
    def get(self, request):
        """
        Get all permission data
        You can update permission data before by "update" parameter:
        - "update": "true" or "false"
        """
        form = RequestPermissionSerializer(data=request.query_params)

        if not form.is_valid():
            raise APIException(params=form.errors)

        if form.data.get("update") == "1":
            permission_data = self.nebula_service.get_permission()
            for p in permission_data:
                Permission.objects.update_or_create(
                    name=p["name"],
                    defaults={"description": p["description"]}
                )

        permissions = Permission.objects.all()
        response = PermissionSerializer(permissions, many=True).data

        return json_response(data=response)


class TradersView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=CreateTraderSerializer)
    def post(self, request):
        """
        Create trader in Exberry and save this information to Authentium database.
        Example request:
            {
                "name": "Trader3",
                "email": "trader3@exberry.io",
                "password": "Trader3!@w",
                "account": 9
            }
        """
        # Parse request
        form = CreateTraderSerializer(data=request.data)

        if not form.is_valid():
            raise APIException(params=form.errors)

        # Check if account exists, return 404 if not found
        account = get_object_or_404(Account, pk=form.data.get("account"))
        data = form.data
        data.update({"account": account.account_id})
        # Get all permission
        permission_data = Permission.objects.all()

        # Filter permission from 1 to 3
        permission_list = permission_data.filter(id__in=[1, 2, 3]).values_list('name', flat=True)

        # Call API create trader to Nebula
        trader_data = self.nebula_service.create_trader(data, permission_list)

        # Create trader and save it to database
        trader = Trader.objects.create(
            trader_id=trader_data["id"],
            account_id=account.id,
            name=trader_data["name"],
            password=form.data["password"],
            email=trader_data["email"]
        )

        # Add permissions to trader
        try:
            for p in trader_data["permissions"]:
                permission = permission_data.get(name=p)
                trader.permissions.add(permission)
        except Permission.DoesNotExist as e:
            raise APIException(detail="Permission not found") from e

        return json_response(status_code=HTTP_201_CREATED)

    @swagger_auto_schema(query_serializer=BaseSerializer())
    def get(self, request):
        """
        Get all trader data
        Parameter:
        - "page": page number
        - "data_per_page": data per page
        """
        page = request.data.get("page", PAGE_DEFAULT)
        per_page = request.data.get("per_page", DATA_PER_PAGE_DEFAULT)

        trader_response = Trader.objects.all()

        try:
            paginator_trader = Paginator(trader_response, per_page)
            trader_list = paginator_trader.get_page(page)
        except InvalidPage as e:
            raise APIException(e)

        response = TraderSerializer(trader_list, many=True).data
        return json_response(data=response, pagination=trader_list)


class TraderView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    def get(self, request, pk):
        """
        Get trader from Authentium database using "id"
        """
        # Get trader using id (id in Authentium database, not Exberry id)
        trader = get_object_or_404(Trader, id=pk)
        return json_response(data=TraderSerializer(trader).data)

    @swagger_auto_schema(request_body=UpdateTraderSerializer)
    def put(self, request, pk):
        """
        Update an existing account in Exberry and save this information to Authentium database.
        pk = "auth0|62d0e0ff1430df99ffc6297a"
        Example request:
            {
                "name": "Trader11",
                "email": "trader11@exberry.io",
                "account": 39,
                "permissions": [1, 2, 3]
            }
        """

        form = UpdateTraderSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)

        # Find the trader with id, return 404 if not found
        trader = get_object_or_404(Trader, id=pk)

        # Find add permission
        permissions = Permission.objects.filter(id__in=form.data.get("permissions"))

        # Call API update trader to Nebula
        self.nebula_service.update_trader(form.data, permissions.values_list('name', flat=True), pk)

        # Update trader to database
        trader.name = form.data.get("name")
        trader.email = form.data.get("email")
        trader.account_id = form.data.get("account")
        trader.save()

        # Set new permissions to trader
        trader.permissions.set(permissions)

        return json_response(status_code=HTTP_204_NO_CONTENT)


class CalendarView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    # update an existing calendar
    @swagger_auto_schema(request_body=CalendarSerializer)
    def put(self, request, pk, *args, **kwargs):
        """
        Update an existing calendar in Exberry and save its information to Authentium database.
        Example request:
            {
                "tradingDays": [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Thursday",
                    "Friday",
                    "Saturday"
                ],
                "name": "Sotatek",
                "timeZone": "+00:00",
                "marketOpen": "08:00",
                "marketClose": "16:30",
                "holidays": [
                    {
                        "date": "2022-01-01",
                        "closeTime": "13:00",
                        "name": "New Year"
                    }
                ]
            }
        """
        form = CalendarSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)

        calendar = get_object_or_404(Calendar, id=pk)
        self.nebula_service.update_calendar(form.data, calendar.calendar_id)
        calendar.name = form.data.get("name")
        calendar.time_zone = form.data.get("time_zone")
        calendar.market_open = form.data.get("market_open")
        calendar.market_close = form.data.get("market_close")
        calendar.trading_days = form.data.get("trading_days")
        calendar.holidays = form.data.get("holidays", [])
        calendar.save()
        return json_response(status_code=HTTP_204_NO_CONTENT)

    # get a calendar with id
    def get(self, request, pk):
        """
        Get information of a calendar in Authentium using id
        """
        calendar = get_object_or_404(Calendar, id=pk)
        return json_response(data=CalendarViewSerializer(calendar).data)


class CalendarsView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=CalendarSerializer)
    def post(self, request, *args, **kwargs):
        """
        Create a new calendar in Exberry and save its information to Authentium's database
        Example request:
            {
                "trading_days": [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Thursday",
                    "Friday",
                    "Saturday"
                ],
                "name": "Sotatek3",
                "time_zone": "+00:00",
                "market_open": "08:00",
                "market_close": "16:30",
                "holidays": [
                    {
                        "date": "2022-01-01",
                        "closeTime": "13:00",
                        "name": "New Year"
                    }
                ]
            }
        """
        form = CalendarSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        calendar_data = self.nebula_service.create_calendar(form.data)

        # create calendar record in database
        Calendar(
            name=calendar_data["name"],
            calendar_id=calendar_data["id"],
            time_zone=calendar_data["timeZone"],
            market_open=calendar_data["marketOpen"],
            market_close=calendar_data["marketClose"],
            trading_days=calendar_data["tradingDays"],
            holidays=calendar_data["holidays"]
        ).save()
        return json_response(data=f'Calendar {calendar_data["name"]} create successful')

    @swagger_auto_schema(query_serializer=BaseSerializer())
    def get(self, request):
        """
        Get all calendars data
        Parameter:
        - "page": page number
        - "data_per_page": data per page
        """
        page = request.GET.get("page", PAGE_DEFAULT)
        per_page = request.GET.get("per_page", DATA_PER_PAGE_DEFAULT)
        calendar_response = Calendar.objects.all().order_by("id")
        try:
            paginator_calendar = Paginator(calendar_response, per_page)
            calendars = paginator_calendar.get_page(page)
        except InvalidPage as e:
            raise APIException(e)
        response = CalendarViewSerializer(calendars, many=True).data
        return json_response(data=response, pagination=calendars)


class InstrumentView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=InstrumentSerializer)
    def post(self, request, *args, **kwargs):
        form = InstrumentSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        data = form.data
        data.update({
            "base_asset": Asset.objects.get(pk=form.data.get("base_asset")).asset_id,
            "quote_asset": Asset.objects.get(pk=form.data.get("quote_asset")).asset_id,
            "calendar_ins": Calendar.objects.get(pk=form.data.get("calendar_ins")).calendar_id,
        })
        data_broker, data_exchange = self.nebula_service.create_instrument_broker(data)
        Instrument(
            instrument_id_broker=data_broker["id"],
            instrument_id_exchange=data_exchange["id"],
            symbol=data_exchange["symbol"],
            quote_currency=data_exchange["quoteCurrency"],
            calendar_ins_id=form.data.get("calendar_ins"),
            price_precision=int(data_exchange["pricePrecision"]),
            quantity_precision=int(data_exchange["quantityPrecision"]),
            min_quantity=float(data_exchange["minQuantity"]),
            max_quantity=float(data_exchange["maxQuantity"]),
            status=data_exchange["status"],
            description=data_exchange["description"],
            base_asset_id=form.data.get("base_asset"),
            quote_asset_id=form.data.get("quote_asset"),
            order_flow=data_broker["orderFlow"],
            trade_flow=data_broker["tradeFlow"],
            image_urls=data_broker["imageUrls"]
        ).save()

        return json_response(status_code=HTTP_201_CREATED)

    def get(self, request):

        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", DATA_PER_PAGE_DEFAULT)
        instrument_response = Instrument.objects.all().order_by("id")

        try:
            paginator_instrument = Paginator(instrument_response, per_page)
            instruments = paginator_instrument.get_page(page)
        except InvalidPage as e:
            raise APIException(e)

        response = InstrumentSerializer(instruments, many=True).data
        return json_response(data=response, pagination=instruments)


class InstrumentsView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=UpdateInstrumentSerializer)
    def put(self, request, pk):
        form = UpdateInstrumentSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)

        instrument = get_object_or_404(Instrument, pk=pk)
        data = form.data
        data.update({"calendar_ins": Calendar.objects.get(pk=form.data.get("calendar_ins")).calendar_id})

        data_broker = self.nebula_service.update_instrument_broker(instrument.instrument_id_broker, data)
        data_exchange = self.nebula_service.update_instrument_exchange(
            instrument.instrument_id_exchange,
            data,
            data_broker
        )
        Instrument.objects.filter(id=pk).update(
            symbol=data_exchange["symbol"],
            quote_currency=data_exchange['quoteCurrency'],
            calendar_ins_id=form.data.get("calendar_ins"),
            price_precision=int(data_exchange['pricePrecision']),
            quantity_precision=int(data_exchange["quantityPrecision"]),
            min_quantity=float(data_exchange["minQuantity"]),
            max_quantity=float(data_exchange["maxQuantity"]),
            status=data_exchange['status'],
            description=data_exchange['description'],
            quote_asset_id=Asset.objects.get(name=data_exchange['quoteCurrency']).id
        )
        return json_response(status_code=HTTP_204_NO_CONTENT)

    def get(self, request, pk):
        """
        Get information of a instrument in Authentium using id
        """
        instrument = get_object_or_404(Instrument, id=pk)
        return json_response(data=InstrumentSerializer(instrument).data)


class PlaceOrderView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=PlaceOrderSerializer)
    def post(self, request, *args, **kwargs):

        form = PlaceOrderSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)

        account = form.data.get('account')
        order_type = form.data.get('order_type')
        side = form.data.get('side')
        instrument = form.data.get('instrument')
        quantity = form.data.get('quantity', 0)
        price = form.data.get('price', 0)
        time_in_force = form.data.get('time_in_force')

        account = Account.objects.get(pk=account)
        symbol_instrument = Instrument.objects.get(pk=instrument)
        base_asset_id = Asset.objects.get(pk=symbol_instrument.base_asset_id).asset_id
        quote_asset_id = Asset.objects.get(pk=symbol_instrument.quote_asset_id).asset_id

        base_asset = symbol_instrument.base_asset_id
        quote_asset = symbol_instrument.quote_asset_id
        # DONE opt in asset for buyer and currency for seller

        query_set = Balance.objects.filter(Q(account_id=account.id))
        if not query_set.filter(Q(asset_id=quote_asset)):  # seller
            _ = self.nebula_service.opt_in_asset(account.account_id, quote_asset_id)
            Balance(account_id=account.id, asset_id=quote_asset).save()
        elif not query_set.filter(Q(asset_id=base_asset)):  # buyer
            _ = self.nebula_service.opt_in_asset(account.account_id, base_asset_id)
            Balance(account_id=account.id, asset_id=base_asset).save()
        if (query_set.get(asset_id=quote_asset).free < quantity * price and side == Side.BUY.value) or (query_set.get(
                asset_id=base_asset).free < quantity and side == Side.SELL.value):
            raise APIException(detail="The balance asset is not enough")

            # DONE lock asset in authentiumELL
        self.__locked_db(side,
                         query_set,
                         quantity,
                         price,
                         base_asset,
                         quote_asset)

        # place order
        place_order = self.nebula_service.place_order(account.account_id,
                                                      order_type,
                                                      side,
                                                      symbol_instrument.symbol,
                                                      quantity,
                                                      price,
                                                      time_in_force)
        Order(
            account_id=account.id,
            order_id=place_order["orderId"],
            order_type=order_type,
            side=side,
            instrument_id=symbol_instrument.id,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            status=place_order["status"]
        ).save()
        return json_response(data=f"The place order is added")

    def __locked_db(self, side, query_set, quantity, price, base_asset, quote_asset):
        locked_object = query_set
        amount_asset = 0
        asset_id = -1
        if side == Side.BUY.value:  # lock asset for seller
            amount_asset = quantity * price
            locked_object = query_set.get(asset_id=quote_asset)
            asset_id = quote_asset
        if side == Side.SELL.value:  # lock currency for buyer
            amount_asset = quantity
            locked_object = query_set.get(asset_id=base_asset)
            asset_id = base_asset
        locked_amount = locked_object.locked + amount_asset
        free_amount = locked_object.free - amount_asset
        query_set.filter(asset_id=asset_id).update(locked=locked_amount, free=free_amount)

    def __locked_asset_admin(self, trader_id, asset_id, amount_asset):
        # TODO lock currency of seller get user id of seller in db and crawl
        pass

    def delete(self, request, *args, **kwargs):
        # TODO wait exberry process cancel place order
        # TODO PENDING.....
        form = CancelPlaceOrderSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        account_id = form.data.get('account_id')
        order_id = form.data.get('order_id')
        instrument = form.data.get('instrument')
        if Order.objects.get(order_id=order_id).status != 'Executed':
            place_order = self.nebula_service.cancel_place_order(account_id, order_id, instrument)
            Order.objects.filter(order_id=order_id).update(status='Canceled')
            return json_response(data='the place order is canceled')
        else:
            return json_response(data='Unsuccessful')


class TraderFeeView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=TradingFeeSerializer)
    def post(self, request, *args, **kwargs):
        form = TradingFeeSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        account = form.data.get("account")
        instrument = form.data.get("instrument")
        taker_fee = form.data.get("taker_fee", 0)
        maker_fee = form.data.get("maker_fee", 0)

        instrument_id = Instrument.objects.get(pk=instrument).instrument_id_broker

        account_id = Account.objects.get(pk=account).account_id
        _ = self.nebula_service.set_trading_fees(account_id, instrument_id, taker_fee, maker_fee)

        _, _ = TradingFee.objects.update_or_create(
            account_id=form.data.get("account"),
            instrument_id=form.data.get("instrument"),
            defaults={
                "taker_fee": taker_fee,
                "maker_fee": maker_fee
            }
        )

        return json_response(status_code=HTTP_201_CREATED)


class OptInView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=OptInSerializer)
    def post(self, request, *args, **kwargs):
        form = OptInSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        account = form.data.get('account')
        asset = form.data.get('asset')
        account_id = Account.objects.get(pk=account).account_id
        asset_id = Asset.objects.get(pk=asset).asset_id

        self.nebula_service.opt_in_asset(account_id, asset_id)
        if not Balance.objects.filter(account_id=account, asset_id=asset):
            Balance(account_id=account, asset_id=asset).save()
        return json_response(data="The asset is opted in.")


class DepositView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nebula_service = NebulaService(Auth().login())

    @swagger_auto_schema(request_body=OptInSerializer)
    def post(self, request, *args, **kwargs):
        form = OptInSerializer(data=request.data)
        if not form.is_valid():
            raise APIException(params=form.errors)
        account = form.data.get('account')
        asset = form.data.get('asset')
        account_id = Account.objects.get(pk=account).account_id
        asset_id = Asset.objects.get(pk=asset).asset_id
        total = form.data.get('total')
        _ = self.nebula_service.send_asset(account_id, asset_id, total)

        bl = get_object_or_404(Balance, account_id=account, asset_id=asset)
        bl.free += total
        bl.total += total
        bl.save()
        return json_response(data=f"The asset is sent {total} asset ")
