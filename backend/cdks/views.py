"""CDK 视图集"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import timedelta  # 🟢 1. 必须新增这一行！
from players.models import Player
from .models import CDK
from .serializers import CDKSerializer, CDKRedeemSerializer
from audit.mixins import AuditLogMixin


class CDKViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """
    CDK API 视图集

    继承自 ModelViewSet 以支持增删改查 (CRUD)
    并自动记录审计日志
    """

    queryset = CDK.objects.all().order_by('-created_at')
    serializer_class = CDKSerializer
    # 默认需要登录权限 (保护管理接口)
    permission_classes = [IsAuthenticated]

    # ========== 1. 批量生成接口 (管理员) ==========
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        批量生成 CDK
        POST /api/cdks/generate/
        Body: { "count": 10, "item_id": 1, "item_count": 100, "max_uses": 1, "days": 30 }
        """
        try:
            # 获取参数并设置默认值
            count = int(request.data.get('count', 1))
            item_id = int(request.data.get('item_id', 1))
            item_count = int(request.data.get('item_count', 100))
            max_uses = int(request.data.get('max_uses', 1))
            days = int(request.data.get('days', 30))

            # 安全限制
            if count > 100:
                return Response({'error': '单次生成数量不能超过 100 个'}, status=status.HTTP_400_BAD_REQUEST)

            # 🟢 2. 修正这里：直接使用 timedelta，不要加 timezone. 前缀
            expires_at = timezone.now() + timedelta(days=days)

            # 调用模型自带的批量生成方法
            cdks = CDK.batch_generate(
                count=count,
                item_id=item_id,
                item_count=item_count,
                max_uses=max_uses,
                expires_at=expires_at
            )

            # 手动记录批量操作日志
            if cdks:
                self._record_log(request, cdks[0], '批量生成', f"批量生成了 {len(cdks)} 个礼包码 (包含: {cdks[0].code} 等)")

            return Response({
                'message': f'成功生成 {len(cdks)} 个兑换码',
                'data': CDKSerializer(cdks, many=True).data
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== 2. 兑换接口 (玩家) ==========
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def redeem(self, request):
        """
        兑换礼包码 (保持原逻辑不变)
        POST /api/cdks/redeem/
        """
        serializer = CDKRedeemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data['code']
        player_id = serializer.validated_data['player_id']

        try:
            cdk = CDK.objects.get(code=code)
        except CDK.DoesNotExist:
            return Response({'error': '兑换码不存在'}, status=status.HTTP_404_NOT_FOUND)

        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response({'error': '玩家不存在'}, status=status.HTTP_404_NOT_FOUND)

        success, message = cdk.redeem(player)

        if success:
            return Response({'message': message, 'cdk': CDKSerializer(cdk).data})
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)