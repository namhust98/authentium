from django.urls import path

from authentium_market import views

urlpatterns = [

    path('place_order', views.PlaceOrderView.as_view(), name='place-order'),
    path('trade_fee', views.TraderFeeView.as_view(), name='trade-fee'),
    path('opt_in', views.OptInView.as_view(), name='opt-in'),
    path('deposit', views.DepositView.as_view(), name='deposit'),

    path('accounts/<int:pk>', views.AccountView.as_view(), name='account-detail'),
    path('accounts', views.AccountsView.as_view(), name='account'),
    path('permissions', views.PermissionView.as_view(), name='permission'),
    path('assets/<int:pk>', views.AssetView.as_view(), name="asset-detail"),
    path('assets', views.AssetsView.as_view(), name="asset"),
    path('traders/<str:pk>', views.TraderView.as_view(), name='trader-detail'),

    path('traders', views.TradersView.as_view(), name='trader'),
    path('calendars/<int:pk>', views.CalendarView.as_view(), name="calendar-detail"),
    path('calendars', views.CalendarsView.as_view(), name="calendar"),

    path('instruments/<int:pk>', views.InstrumentsView.as_view(), name="instrument"),
    path('instruments', views.InstrumentView.as_view(), name="instruments")

]
