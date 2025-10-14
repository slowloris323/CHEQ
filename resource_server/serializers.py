from rest_framework import serializers
from .models import Resource, ResourceToConfirmationMapping

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'


class ResourceToConfirmationMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceToConfirmationMapping
        fields = '__all__'