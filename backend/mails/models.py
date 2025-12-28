from django.db import models
from django.contrib.auth.models import User
from players.models import Player


class Mail(models.Model):
    """
    邮件模型 - 支持单人邮件和全服邮件
    
    外键关系说明:
    1. sender → User (Django内置用户模型)
       - 记录发送邮件的后台管理员
       - on_delete=SET_NULL: 管理员被删除时，邮件保留但sender变为NULL
       - 反向查询: user.sent_mails.all() 获取该管理员发送的所有邮件
    
    2. receiver → Player (players app的玩家模型)
       - 接收邮件的玩家，为空时表示全服邮件
       - on_delete=CASCADE: 玩家被删除时，相关邮件也删除
       - 反向查询: player.received_mails.all() 获取该玩家收到的所有邮件
    """
    
    # ========== 邮件内容 ==========
    title = models.CharField(
        max_length=100,
        verbose_name='邮件标题'
    )
    
    content = models.TextField(
        verbose_name='邮件内容'
    )
    
    # ========== 发送者 - 后台管理员 (Django User) ==========
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # 管理员删除后，邮件保留，sender置空
        null=True,
        related_name='sent_mails',  # 反向查询名称
        verbose_name='发送者(管理员)'
    )
    
    # ========== 接收者 - 玩家 (允许为空表示全服邮件) ==========
    receiver = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,   # 玩家删除后，相关邮件也删除
        null=True,
        blank=True,                 # 允许表单中留空
        related_name='received_mails',
        verbose_name='接收者(玩家)'
    )
    
    # ========== 全服邮件标识 ==========
    is_global = models.BooleanField(
        default=False,
        verbose_name='全服邮件'
    )
    
    # ========== 道具附件 (预留字段) ==========
    item_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='道具ID'
    )
    
    item_count = models.PositiveIntegerField(
        default=0,
        verbose_name='道具数量'
    )
    
    # ========== 邮件状态 ==========
    expires_at = models.DateTimeField(
        verbose_name='过期时间'
    )
    
    is_claimed = models.BooleanField(
        default=False,
        verbose_name='已领取'
    )
    
    # ========== 时间戳 ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        db_table = 'mails'
        verbose_name = '邮件'
        verbose_name_plural = '邮件列表'
        ordering = ['-created_at']  # 默认按创建时间倒序
    
    def __str__(self):
        """
        邮件的字符串表示
        - 全服邮件显示: [全服] 邮件标题
        - 私人邮件显示: [私人] 邮件标题 -> 玩家昵称
        """
        if self.is_global:
            return f"[全服] {self.title}"
        return f"[私人] {self.title} -> {self.receiver}"
