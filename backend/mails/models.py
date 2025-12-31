from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from players.models import Player
import logging

# 配置日志
logger = logging.getLogger(__name__)


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
        db_index=True,  # 过滤全服/私人邮件
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
        db_index=True,  # 过期查询优化
        verbose_name='过期时间'
    )
    
    is_claimed = models.BooleanField(
        default=False,
        db_index=True,  # 查询未领取邮件
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
    
    # ========== 业务逻辑方法 ==========
    
    def claim_attachment(self):
        """
        领取邮件附件 - 核心业务逻辑
        
        使用 transaction.atomic() + select_for_update() 保证:
        1. 数据一致性: 玩家道具增加 和 邮件状态更新 要么同时成功，要么同时回滚
        2. 并发安全: 行级锁防止高并发下的重复领取
        
        Returns:
            tuple: (success: bool, message: str)
                - success: 是否领取成功
                - message: 结果描述信息
        """
        # ===== 1. 快速验证：全服邮件暂不支持 (无需加锁) =====
        if self.is_global:
            return False, "全服邮件需单独处理，暂不支持批量领取"
        
        # ===== 2. 快速验证：必须有接收者 (无需加锁) =====
        if not self.receiver:
            return False, "邮件没有指定接收者"
        
        # ===== 3. 原子事务 + 行级锁：领取道具 =====
        # transaction.atomic() 确保以下操作要么全部成功，要么全部回滚
        with transaction.atomic():
            # ⭐ 使用 select_for_update() 锁定邮件行，防止并发重复领取
            mail = Mail.objects.select_for_update().get(pk=self.pk)
            
            # 在锁内再次检查状态（悲观检查）
            if mail.is_claimed:
                return False, "邮件已被领取"
            
            if mail.expires_at <= timezone.now():
                return False, "邮件已过期"
            
            # 获取玩家并加锁（防止并发修改玩家资产）
            player = Player.objects.select_for_update().get(pk=mail.receiver_id)
            item_name = None
            
            # 根据 item_id 分发道具
            if mail.item_id == 1:  # 金币
                player.gold += mail.item_count
                player.save(update_fields=['gold'])
                item_name = f"金币 x{mail.item_count}"
                
            elif mail.item_id == 2:  # 钻石
                player.diamond += mail.item_count
                player.save(update_fields=['diamond'])
                item_name = f"钻石 x{mail.item_count}"
                
            elif mail.item_id is not None:
                # 其他道具类型暂未实现，记录日志但不报错
                logger.warning(f"[邮件领取] 未实现的道具类型: item_id={mail.item_id}, mail_id={mail.id}")
                item_name = f"未知道具(ID:{mail.item_id}) x{mail.item_count}"
            
            # 标记邮件为已领取
            mail.is_claimed = True
            mail.save(update_fields=['is_claimed'])
        
        # 构建成功消息
        if item_name:
            return True, f"领取成功！玩家 [{player.nickname}] 获得 {item_name}"
        else:
            return True, f"领取成功！邮件无附件道具"

