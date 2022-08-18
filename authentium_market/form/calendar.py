from rest_framework import serializers
from authentium_market.models import Calendar


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ['name', 'time_zone', 'market_open', 'market_close', 'trading_days', 'holidays']


class CalendarViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        exclude = ('created_at', 'updated_at',)
