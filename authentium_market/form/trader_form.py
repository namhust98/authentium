from rest_framework import serializers
from authentium_market.models import Trader


class TraderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trader
        fields = '__all__'


class CreateTraderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trader
        exclude = ("permissions", "trader_id")


class UpdateTraderSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Trader
        fields = ("name", "email", "account", "permissions",)
