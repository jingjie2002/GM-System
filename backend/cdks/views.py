"""CDK 视图集"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from players.models import Player
from .models import CDK, CDKLog
from .serializers import CDKSerializer, CDKRedeemSerializer


class CDKViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CDK API 视图集
    
    主要功能: 兑换接口 /api/cdks/redeem/
    """
    
    queryset = CDK.objects.all()
    serializer_class = CDKSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def redeem(self, request):
        """
        兑换礼包码
        
        POST /api/cdks/redeem/
        Body: {"code": "KURO666", "player_id": "uuid"}
        """
        # 验证请求数据
        serializer = CDKRedeemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['code']
        player_id = serializer.validated_data['player_id']
        
        # 查找 CDK
        try:
            cdk = CDK.objects.get(code=code)
        except CDK.DoesNotExist:
            return Response(
                {'error': '兑换码不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 查找玩家
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response(
                {'error': '玩家不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 执行兑换（调用模型中的事务逻辑）
        success, message = cdk.redeem(player)
        
        if success:
            return Response({
                'message': message,
                'cdk': CDKSerializer(cdk).data
            })
        else:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )
