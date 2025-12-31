"""邮件视图集"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from .models import Mail
from .serializers import MailSerializer, MailListSerializer


class MailViewSet(viewsets.ModelViewSet):
    """邮件 API 视图集"""
    
    queryset = Mail.objects.all()
    serializer_class = MailSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MailListSerializer
        return MailSerializer
    
    def get_queryset(self):
        """支持按玩家过滤邮件"""
        queryset = Mail.objects.all()
        player_id = self.request.query_params.get('player_id')
        if player_id:
            # 返回该玩家的私人邮件 + 全服邮件
            queryset = queryset.filter(
                models.Q(receiver_id=player_id) | models.Q(is_global=True)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """
        领取邮件附件
        
        POST /api/mails/{id}/claim/
        """
        mail = self.get_object()
        
        # 如果是全服邮件，暂不支持
        if mail.is_global:
            return Response(
                {'error': '全服邮件暂不支持 API 领取'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 调用模型中的事务逻辑
        success, message = mail.claim_attachment()
        
        if success:
            return Response({'message': message})
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
