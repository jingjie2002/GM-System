"""
玩家视图集

ViewSet 是什么？
---------------
ViewSet 是 DRF 提供的"一站式"视图类，自动实现增删改查 (CRUD)：
- list()     → GET /api/players/        获取列表
- retrieve() → GET /api/players/{id}/   获取单个
- create()   → POST /api/players/       创建
- update()   → PUT /api/players/{id}/   更新
- destroy()  → DELETE /api/players/{id}/ 删除
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Player
from .serializers import PlayerSerializer, PlayerListSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    玩家 API 视图集
    
    提供玩家的增删改查接口
    """
    
    queryset = Player.objects.all()  # 查询集：所有玩家
    serializer_class = PlayerSerializer  # 默认使用的序列化器
    
    # 搜索和过滤配置
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nickname']  # 支持按昵称搜索 ?search=xxx
    ordering_fields = ['level', 'gold', 'diamond', 'created_at']  # 支持排序
    ordering = ['-created_at']  # 默认按创建时间倒序
    
    def get_serializer_class(self):
        """
        根据不同操作使用不同的序列化器
        - list: 使用精简版序列化器
        - 其他: 使用完整版序列化器
        """
        if self.action == 'list':
            return PlayerListSerializer
        return PlayerSerializer
    
    # ========== 自定义接口 ==========
    
    @action(detail=True, methods=['post'])
    def add_gold(self, request, pk=None):
        """
        给玩家加金币
        
        POST /api/players/{id}/add_gold/
        Body: {"amount": 100}
        """
        player = self.get_object()
        amount = request.data.get('amount', 0)
        
        if not isinstance(amount, int) or amount <= 0:
            return Response({'error': '金额必须是正整数'}, status=400)
        
        player.gold += amount
        player.save(update_fields=['gold'])
        
        return Response({
            'message': f'成功为 {player.nickname} 增加 {amount} 金币',
            'new_gold': player.gold
        })
    
    @action(detail=True, methods=['post'])
    def ban(self, request, pk=None):
        """
        封禁玩家
        
        POST /api/players/{id}/ban/
        """
        player = self.get_object()
        player.status = Player.Status.BANNED
        player.save(update_fields=['status'])
        
        return Response({
            'message': f'玩家 {player.nickname} 已被封禁',
            'status': player.status
        })
    
    @action(detail=True, methods=['post'])
    def unban(self, request, pk=None):
        """
        解封玩家
        
        POST /api/players/{id}/unban/
        """
        player = self.get_object()
        player.status = Player.Status.NORMAL
        player.save(update_fields=['status'])
        
        return Response({
            'message': f'玩家 {player.nickname} 已解封',
            'status': player.status
        })
