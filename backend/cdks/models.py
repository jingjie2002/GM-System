from django.db import models, transaction
from django.utils import timezone
from players.models import Player
import logging
import string
import random

logger = logging.getLogger(__name__)


class CDK(models.Model):
    """
    CDK 兑换码模型
    
    用于礼包码/激活码系统:
    - 支持设置奖励内容 (道具ID和数量)
    - 支持限制使用次数 (max_uses)
    - 支持设置过期时间 (expires_at)
    """
    
    # ========== 兑换码 ==========
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='兑换码',
        help_text='唯一兑换码，如 KURO666'
    )
    
    # ========== 奖励内容 ==========
    item_id = models.IntegerField(
        default=1,
        verbose_name='道具ID',
        help_text='1=金币, 2=钻石'
    )
    
    item_count = models.PositiveIntegerField(
        default=100,
        verbose_name='道具数量'
    )
    
    # ========== 使用限制 ==========
    max_uses = models.PositiveIntegerField(
        default=1,
        verbose_name='总额度',
        help_text='最多可被兑换次数'
    )
    
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name='已使用次数'
    )
    
    # ========== 有效期 ==========
    expires_at = models.DateTimeField(
        verbose_name='过期时间'
    )
    
    # ========== 时间戳 ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        db_table = 'cdks'
        verbose_name = 'CDK兑换码'
        verbose_name_plural = 'CDK兑换码列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} (剩余: {self.max_uses - self.used_count})"
    
    # ========== 业务方法 ==========
    
    @property
    def remaining_uses(self):
        """剩余可用次数"""
        return self.max_uses - self.used_count
    
    def is_valid(self):
        """判断 CDK 是否有效（未过期且有剩余额度）"""
        return timezone.now() < self.expires_at and self.remaining_uses > 0
    is_valid.boolean = True
    is_valid.short_description = '是否有效'
    
    def redeem(self, player):
        """
        玩家兑换 CDK
        
        使用 transaction.atomic() 保证原子性:
        - 所有数据库操作要么全部成功，要么全部回滚
        - 防止并发兑换导致的超额问题
        
        Args:
            player: Player 实例，要兑换的玩家
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # ===== 1. 检查有效期 =====
        if timezone.now() >= self.expires_at:
            return False, "兑换码已过期"
        
        # ===== 2. 检查额度 =====
        if self.used_count >= self.max_uses:
            return False, "兑换码已被领完"
        
        # ===== 3. 原子事务：兑换操作 =====
        with transaction.atomic():
            # 使用 select_for_update 锁定行，防止并发问题
            cdk = CDK.objects.select_for_update().get(pk=self.pk)
            
            # 再次检查额度（防止并发）
            if cdk.used_count >= cdk.max_uses:
                return False, "兑换码已被领完"
            
            # 检查是否已经兑换过
            if CDKLog.objects.filter(player=player, cdk=cdk).exists():
                return False, "您已经兑换过该兑换码"
            
            # 4. 扣除额度
            cdk.used_count += 1
            cdk.save(update_fields=['used_count'])
            
            # 5. 增加兑换记录
            CDKLog.objects.create(player=player, cdk=cdk)
            
            # 6. 调用玩家加钱逻辑
            item_name = None
            if cdk.item_id == 1:  # 金币
                player.gold += cdk.item_count
                player.save(update_fields=['gold'])
                item_name = f"金币 x{cdk.item_count}"
            elif cdk.item_id == 2:  # 钻石
                player.diamond += cdk.item_count
                player.save(update_fields=['diamond'])
                item_name = f"钻石 x{cdk.item_count}"
            else:
                logger.warning(f"[CDK兑换] 未实现的道具类型: item_id={cdk.item_id}")
                item_name = f"未知道具(ID:{cdk.item_id}) x{cdk.item_count}"
        
        return True, f"兑换成功！获得 {item_name}"
    
    @classmethod
    def generate_random_code(cls, length=8):
        """
        生成随机兑换码
        
        Args:
            length: 码长度，默认 8 位
            
        Returns:
            str: 随机大写字母组成的兑换码
        """
        return ''.join(random.choices(string.ascii_uppercase, k=length))
    
    @classmethod
    def batch_generate(cls, count=10, item_id=1, item_count=100, max_uses=1, expires_at=None):
        """
        批量生成兑换码
        
        Args:
            count: 生成数量
            item_id: 道具ID
            item_count: 道具数量
            max_uses: 每个码的使用次数
            expires_at: 过期时间
            
        Returns:
            list: 生成的 CDK 对象列表
        """
        if expires_at is None:
            # 默认 30 天后过期
            expires_at = timezone.now() + timezone.timedelta(days=30)
        
        created_cdks = []
        for _ in range(count):
            # 确保生成唯一码
            while True:
                code = cls.generate_random_code()
                if not cls.objects.filter(code=code).exists():
                    break
            
            cdk = cls.objects.create(
                code=code,
                item_id=item_id,
                item_count=item_count,
                max_uses=max_uses,
                expires_at=expires_at
            )
            created_cdks.append(cdk)
        
        return created_cdks


class CDKLog(models.Model):
    """
    CDK 兑换记录
    
    用途:
    1. 防止同一玩家重复兑换同一 CDK
    2. 审计追踪：记录谁在什么时候兑换了什么码
    """
    
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='cdk_logs',
        verbose_name='玩家'
    )
    
    cdk = models.ForeignKey(
        CDK,
        on_delete=models.CASCADE,
        related_name='redeem_logs',
        verbose_name='兑换码'
    )
    
    redeemed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='兑换时间'
    )
    
    class Meta:
        db_table = 'cdk_logs'
        verbose_name = 'CDK兑换记录'
        verbose_name_plural = 'CDK兑换记录'
        # 联合唯一约束：同一玩家只能兑换同一 CDK 一次
        unique_together = ['player', 'cdk']
        ordering = ['-redeemed_at']
    
    def __str__(self):
        return f"{self.player.nickname} 兑换 {self.cdk.code}"
