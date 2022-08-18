from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False)
    per_page = serializers.IntegerField(required=False)
