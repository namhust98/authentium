from django.utils import timezone
from django.contrib.auth.models import UserManager, AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models

from authentium_market.common.constants import (
    QUANTITY_PRECISION_MIN, QUANTITY_PRECISION_MAX, ASSET_NAME_MAX_LENGTH, ASSET_DESCRIPTION_MAX_LENGTH,
    TOTAL_SUPPLY_MIN, INSTRUMENT_SYMBOL_MAX_LENGTH, INSTRUMENT_DESCRIPTION_MAX_LENGTH, ORDER_FLOW_DEFAULT,
    TRADE_FLOW_DEFAULT
)


class User(AbstractUser):
    email = models.EmailField(
        "email address", unique=True, default=None, blank=True, null=True
    )
    phone = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        default=None,
        validators=[
            RegexValidator(
                regex="^[0-9-#+()]*$",
                message="Phone number must be 0-9,-,#,+ and ()",
                code="Invalid phone number",
            ),
        ],
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email


class Calendar(models.Model):
    name = models.CharField(max_length=255)
    calendar_id = models.CharField(max_length=255)
    time_zone = models.CharField(max_length=10)
    market_open = models.CharField(max_length=5)
    market_close = models.CharField(max_length=5)
    trading_days = models.JSONField()
    holidays = models.JSONField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar'
        verbose_name = "calendar"
        verbose_name_plural = "calendars"

    def __str__(self):
        return self.name


class Asset(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'Active'
        DISABLED = 'Disabled'

    asset_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=ASSET_NAME_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=ASSET_DESCRIPTION_MAX_LENGTH)
    ledger_system = models.CharField(max_length=255)
    ledger_asset_id = models.IntegerField()
    quantity_precision = models.IntegerField(validators=[
        MaxValueValidator(QUANTITY_PRECISION_MAX),
        MinValueValidator(QUANTITY_PRECISION_MIN)
    ])
    total_supply = models.IntegerField(validators=[MinValueValidator(TOTAL_SUPPLY_MIN)])
    status = models.CharField(max_length=255, choices=StatusChoices.choices)
    url = models.URLField(max_length=255, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'asset'
        verbose_name = "asset"
        verbose_name_plural = "assets"

    def __str__(self):
        return self.name


class Instrument(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'Active'
        DISABLED = 'Disabled'

    instrument_id_broker = models.IntegerField()
    instrument_id_exchange = models.IntegerField()
    symbol = models.CharField(
        max_length=INSTRUMENT_SYMBOL_MAX_LENGTH,
        default=None,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex='^[A-Za-z0-9.-]*$',
                message="Instrument must be 0-9,- and (.)",
                code="Invalid instrument's name"
            )])
    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    description = models.CharField(max_length=INSTRUMENT_DESCRIPTION_MAX_LENGTH)
    base_asset = models.ForeignKey(Asset, models.CASCADE, related_name="base_asset")
    quote_asset = models.ForeignKey(Asset, models.CASCADE, related_name="quote_asset")
    quote_currency = models.CharField(max_length=ASSET_NAME_MAX_LENGTH)
    order_flow = models.CharField(max_length=255, default=ORDER_FLOW_DEFAULT)
    trade_flow = models.CharField(max_length=255, default=TRADE_FLOW_DEFAULT)
    image_urls = models.JSONField(blank=True)
    calendar_ins = models.ForeignKey(Calendar, models.CASCADE)
    price_precision = models.IntegerField(default=0, validators=[MaxValueValidator(10)])
    quantity_precision = models.IntegerField(default=0, validators=[MaxValueValidator(10)])
    min_quantity = models.FloatField()
    max_quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'instrument'
        verbose_name = "instrument"
        verbose_name_plural = "instruments"

    def __str__(self):
        return self.symbol


class Account(models.Model):
    class Meta:
        db_table = 'account'
        verbose_name = "account"
        verbose_name_plural = "accounts"

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        VERIFIED = 'Verified'

    account_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=200, choices=StatusChoices.choices)
    ledger_system = models.CharField(max_length=200)
    ledger_account_id = models.CharField(max_length=200)
    assets = models.ManyToManyField(Asset)
    comp_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TradingFee(models.Model):
    class Meta:
        db_table = 'trading_fee'
        verbose_name = "trading_fee"
        verbose_name_plural = "trading_fees"
        unique_together = ('account', 'instrument')

    account = models.ForeignKey(Account, models.CASCADE)
    instrument = models.ForeignKey(Instrument, models.CASCADE)
    taker_fee = models.IntegerField(default=0)
    maker_fee = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.instrument.symbol


class Order(models.Model):
    class Meta:
        db_table = 'order'
        verbose_name = "order"
        verbose_name_plural = "orders"

    class OrderTypeChoices(models.TextChoices):
        LIMIT = 'Limit'
        MARKET = 'Market'

    class SideChoices(models.TextChoices):
        BUY = 'Buy'
        SELL = 'Sell'

    class TimeInForceChoices(models.TextChoices):
        GTC = 'GTC'
        GTD = 'GTD'
        FOK = 'FOK'
        IOC = 'IOC'

    order_id = models.IntegerField()
    account = models.ForeignKey(Account, models.CASCADE)
    order_type = models.CharField(max_length=10, choices=OrderTypeChoices.choices)
    side = models.CharField(max_length=10, choices=SideChoices.choices)
    instrument = models.ForeignKey(Instrument, models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    time_in_force = models.CharField(max_length=10, choices=TimeInForceChoices.choices)
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Balance(models.Model):
    class Meta:
        db_table = 'balance'
        verbose_name = "balance"
        verbose_name_plural = "balances"
        unique_together = ('account', 'asset')

    account = models.ForeignKey(Account, models.CASCADE)
    asset = models.ForeignKey(Asset, models.CASCADE)
    free = models.FloatField(default=0)
    locked = models.FloatField(default=0)
    total = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account.name


class Permission(models.Model):
    class Meta:
        db_table = 'permission'
        verbose_name = "permission"
        verbose_name_plural = "permissions"

    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name


class Trader(models.Model):
    class Meta:
        db_table = 'trader'
        verbose_name = "trader"
        verbose_name_plural = "traders"

    account = models.ForeignKey(Account, models.CASCADE)
    trader_id = models.CharField(unique=True, max_length=128)
    name = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200, unique=True)
    email = models.EmailField(unique=True)
    permissions = models.ManyToManyField(Permission)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Token(models.Model):
    class TokenTypeChoices(models.TextChoices):
        ADMIN = 'Admin'
        TRADER = 'Trader'

    class Meta:
        db_table = 'token'
        verbose_name = "token"

    token = models.TextField()
    expires_in = models.IntegerField()
    token_type = models.CharField(max_length=10, choices=TokenTypeChoices.choices)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
