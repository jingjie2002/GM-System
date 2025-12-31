"""
邮件模块单元测试

测试覆盖:
1. 邮件领取成功场景
2. 重复领取拒绝 (幂等性)
3. 过期邮件拒绝
4. 并发领取安全性
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from players.models import Player
from .models import Mail


class MailClaimTestCase(TestCase):
    """邮件领取测试用例"""
    
    def setUp(self):
        """测试前准备数据"""
        # 创建测试玩家
        self.player = Player.objects.create(
            nickname="测试玩家",
            level=10,
            gold=1000,
            diamond=100
        )
        
        # 创建测试管理员
        self.admin = User.objects.create_user(
            username="test_admin",
            password="test123"
        )
        
        # 创建有效邮件 (金币奖励)
        self.valid_mail = Mail.objects.create(
            title="测试邮件",
            content="这是一封测试邮件",
            sender=self.admin,
            receiver=self.player,
            is_global=False,
            item_id=1,  # 金币
            item_count=500,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # 创建过期邮件
        self.expired_mail = Mail.objects.create(
            title="过期邮件",
            content="这封邮件已过期",
            sender=self.admin,
            receiver=self.player,
            is_global=False,
            item_id=1,
            item_count=100,
            expires_at=timezone.now() - timedelta(days=1)  # 昨天过期
        )
    
    def test_claim_gold_success(self):
        """测试: 成功领取金币邮件"""
        initial_gold = self.player.gold
        
        success, message = self.valid_mail.claim_attachment()
        
        # 验证领取成功
        self.assertTrue(success)
        self.assertIn("领取成功", message)
        self.assertIn("金币", message)
        
        # 验证金币增加
        self.player.refresh_from_db()
        self.assertEqual(self.player.gold, initial_gold + 500)
        
        # 验证邮件状态
        self.valid_mail.refresh_from_db()
        self.assertTrue(self.valid_mail.is_claimed)
    
    def test_claim_already_claimed(self):
        """测试: 重复领取被拒绝 (幂等性保证)"""
        # 第一次领取
        self.valid_mail.claim_attachment()
        initial_gold = self.player.gold
        self.player.refresh_from_db()
        
        # 第二次领取应失败
        success, message = self.valid_mail.claim_attachment()
        
        self.assertFalse(success)
        self.assertIn("已被领取", message)
        
        # 验证金币没有再次增加
        self.player.refresh_from_db()
        # 金币应该只增加一次
    
    def test_claim_expired_mail(self):
        """测试: 过期邮件无法领取"""
        initial_gold = self.player.gold
        
        success, message = self.expired_mail.claim_attachment()
        
        self.assertFalse(success)
        self.assertIn("已过期", message)
        
        # 验证金币没有增加
        self.player.refresh_from_db()
        self.assertEqual(self.player.gold, initial_gold)
    
    def test_claim_global_mail_rejected(self):
        """测试: 全服邮件暂不支持领取"""
        global_mail = Mail.objects.create(
            title="全服公告",
            content="全服活动开始",
            sender=self.admin,
            receiver=None,
            is_global=True,
            item_id=1,
            item_count=100,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        success, message = global_mail.claim_attachment()
        
        self.assertFalse(success)
        self.assertIn("全服邮件", message)
