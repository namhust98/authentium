from django.contrib import admin
from authentium_market.models import (
    Account,
    Trader,
    TradingFee,
    Order, Balance,
    Permission,
    Asset,
    Calendar,
    Instrument,
    User,
)

admin.site.register(User)
admin.site.register(Account)
admin.site.register(Trader)
admin.site.register(Order)
admin.site.register(Balance)
admin.site.register(Permission)
admin.site.register(Asset)
admin.site.register(Calendar)
admin.site.register(TradingFee)
admin.site.register(Instrument)
