from django.contrib.auth import get_user_model
from rest_framework import serializers

from stock.models import Player


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        player = Player.objects.create_user(username=validated_data['username'], password=validated_data['password'])
        return player
