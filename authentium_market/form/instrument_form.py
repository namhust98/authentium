from rest_framework import serializers
from ..models import Instrument


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        exclude = (
            'instrument_id_broker',
            'instrument_id_exchange',
            'quote_currency',
            'created_at',
            'updated_at',
        )


class UpdateInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        exclude = (
            'instrument_id_broker',
            'instrument_id_exchange',
            'base_asset',
            'quote_asset',
            'order_flow',
            'trade_flow',
            'image_urls',
            'created_at',
            'updated_at',
            'quote_currency',
        )


class InstrumentViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'
