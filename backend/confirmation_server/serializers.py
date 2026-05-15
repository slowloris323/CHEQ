from rest_framework import serializers
from .models import ResourceUriCheqMapping

class ResourceUriCheqMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceUriCheqMapping
        fields = '__all__'

