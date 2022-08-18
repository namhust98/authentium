from rest_framework import serializers
from ..models import TradingFee, Order, Balance


class PlaceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('created_at', 'updated_at', 'order_id', 'status',)


class TradingFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingFee
        fields = "__all__"


class CancelPlaceOrderSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    instrument = serializers.CharField(max_length=10)


class OptInSerializer(serializers.ModelSerializer):
    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks"""
        return []

    class Meta:
        model = Balance
        fields = '__all__'
