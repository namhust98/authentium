from rest_framework import serializers

from authentium_market.models import Permission, Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class RequestAccountSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=200)


class RequestPermissionSerializer(serializers.Serializer):
    update = serializers.ChoiceField(required=False, choices=["1", "0"])
