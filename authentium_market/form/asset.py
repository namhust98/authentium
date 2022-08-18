from rest_framework import serializers
from authentium_market.models import Asset


class AssetCreateSerializer(serializers.ModelSerializer):
    is_currency = serializers.BooleanField(default=False)

    class Meta:
        model = Asset
        fields = [
            'name',
            'description',
            'quantity_precision',
            'total_supply',
            'status',
            'url',
            'is_currency'
        ]


class AssetUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['status']


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
