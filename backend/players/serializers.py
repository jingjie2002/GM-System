"""
玩家序列化器

序列化 (Serialization) 是什么？
-----------------------------
通俗来说，序列化就是把 Python 对象"翻译"成 JSON 字符串，让前端能读懂。

例如：
    Python 对象:  player.nickname = "小明", player.level = 10
    JSON 字符串:  {"nickname": "小明", "level": 10, "gold": 1000}

反过来，前端发来的 JSON 字符串也能"翻译"回 Python 对象，这叫反序列化。
"""

from rest_framework import serializers
from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    """
    玩家序列化器
    
    ModelSerializer 会自动根据 Player 模型生成字段定义，
    省去手动一个个定义字段的麻烦。
    """
    
    class Meta:
        model = Player  # 关联的模型
        fields = '__all__'  # 序列化所有字段
        # 也可以指定具体字段:
        # fields = ['id', 'nickname', 'level', 'gold', 'diamond', 'status']
        
        # 只读字段（前端不能修改）
        read_only_fields = ['id', 'created_at', 'updated_at']


class PlayerListSerializer(serializers.ModelSerializer):
    """
    玩家列表序列化器（精简版）
    
    用于列表接口，只返回关键字段，减少数据传输
    """
    
    class Meta:
        model = Player
        fields = ['id', 'nickname', 'level', 'gold', 'diamond', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
