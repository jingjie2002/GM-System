import uuid
from django.db import models


class Player(models.Model):
    """
    玩家模型 - 存储游戏玩家的核心数据
    """
    
    # 账号状态选项
    class Status(models.TextChoices):
        NORMAL = 'normal', '正常'
        BANNED = 'banned', '封禁'
    
    # 主键：使用 UUID 作为玩家唯一标识
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='玩家ID'
    )
    
    # 基础信息
    nickname = models.CharField(
        max_length=50,
        verbose_name='昵称'
    )
    
    # 游戏数据
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='等级'
    )
    
    gold = models.BigIntegerField(
        default=0,
        verbose_name='金币'
    )
    
    diamond = models.BigIntegerField(
        default=0,
        verbose_name='钻石'
    )
    
    # 账号状态
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.NORMAL,
        verbose_name='账号状态'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='注册时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='最后更新时间'
    )
    
    class Meta:
        db_table = 'players'  # 指定数据库表名
        verbose_name = '玩家'
        verbose_name_plural = '玩家列表'
        ordering = ['-created_at']  # 默认按注册时间倒序排列
    
    def __str__(self):
        return f"{self.nickname} (Lv.{self.level})"
