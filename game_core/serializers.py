from rest_framework import serializers
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        # 这里定义你想暴露给 Unity 的字段
        # '__all__' 表示全部字段（id, username, level, gold...）
        fields = '__all__'