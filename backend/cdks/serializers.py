"""CDK 序列化器"""

from rest_framework import serializers
from .models import CDK, CDKLog


class CDKSerializer(serializers.ModelSerializer):
    """CDK 序列化器"""
    
    remaining_uses = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CDK
        fields = [
            'id', 'code', 'item_id', 'item_count',
            'max_uses', 'used_count', 'remaining_uses',
            'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'used_count', 'remaining_uses', 'created_at']


class CDKRedeemSerializer(serializers.Serializer):
    """CDK 兑换请求序列化器"""
    
    code = serializers.CharField(max_length=50, help_text='兑换码')
    player_id = serializers.UUIDField(help_text='玩家ID')


class CDKLogSerializer(serializers.ModelSerializer):
    """CDK 兑换记录序列化器"""
    
    player_name = serializers.CharField(source='player.nickname', read_only=True)
    cdk_code = serializers.CharField(source='cdk.code', read_only=True)
    
    class Meta:
        model = CDKLog
        fields = ['id', 'player', 'player_name', 'cdk', 'cdk_code', 'redeemed_at']
