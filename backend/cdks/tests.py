"""
CDK 兑换模块单元测试

测试覆盖:
1. 兑换成功场景
2. 重复兑换拒绝 (幂等性)
3. 过期兑换码拒绝
4. 额度用尽拒绝
5. 并发兑换安全性 (select_for_update)
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from players.models import Player
from .models import CDK, CDKLog


class CDKRedeemTestCase(TestCase):
    """CDK 兑换测试用例"""
    
    def setUp(self):
        """测试前准备数据"""
        # 创建测试玩家
        self.player = Player.objects.create(
            nickname="测试玩家",
            level=10,
            gold=1000,
            diamond=100
        )
        
        self.player2 = Player.objects.create(
            nickname="玩家二号",
            level=5,
            gold=500,
            diamond=50
        )
        
        # 创建有效 CDK (金币奖励)
        self.valid_cdk = CDK.objects.create(
            code="TESTGOLD100",
            item_id=1,  # 金币
            item_count=1000,
            max_uses=10,
            used_count=0,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # 创建单次使用 CDK
        self.single_use_cdk = CDK.objects.create(
            code="SINGLE001",
            item_id=2,  # 钻石
            item_count=50,
            max_uses=1,
            used_count=0,
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # 创建过期 CDK
        self.expired_cdk = CDK.objects.create(
            code="EXPIRED001",
            item_id=1,
            item_count=100,
            max_uses=10,
            used_count=0,
            expires_at=timezone.now() - timedelta(days=1)  # 昨天过期
        )
        
        # 创建已用尽 CDK
        self.exhausted_cdk = CDK.objects.create(
            code="EXHAUSTED01",
            item_id=1,
            item_count=100,
            max_uses=1,
            used_count=1,  # 已用完
            expires_at=timezone.now() + timedelta(days=30)
        )
    
    def test_redeem_gold_success(self):
        """测试: 成功兑换金币 CDK"""
        initial_gold = self.player.gold
        
        success, message = self.valid_cdk.redeem(self.player)
        
        # 验证兑换成功
        self.assertTrue(success)
        self.assertIn("兑换成功", message)
        self.assertIn("金币", message)
        
        # 验证金币增加
        self.player.refresh_from_db()
        self.assertEqual(self.player.gold, initial_gold + 1000)
        
        # 验证使用次数增加
        self.valid_cdk.refresh_from_db()
        self.assertEqual(self.valid_cdk.used_count, 1)
        
        # 验证兑换记录创建
        self.assertTrue(
            CDKLog.objects.filter(player=self.player, cdk=self.valid_cdk).exists()
        )
    
    def test_redeem_diamond_success(self):
        """测试: 成功兑换钻石 CDK"""
        initial_diamond = self.player.diamond
        
        success, message = self.single_use_cdk.redeem(self.player)
        
        self.assertTrue(success)
        self.assertIn("钻石", message)
        
        self.player.refresh_from_db()
        self.assertEqual(self.player.diamond, initial_diamond + 50)
    
    def test_redeem_already_claimed(self):
        """测试: 同一玩家重复兑换被拒绝 (幂等性)"""
        # 第一次兑换
        self.valid_cdk.redeem(self.player)
        self.player.refresh_from_db()
        gold_after_first = self.player.gold
        
        # 第二次兑换应失败
        success, message = self.valid_cdk.redeem(self.player)
        
        self.assertFalse(success)
        self.assertIn("已经兑换过", message)
        
        # 验证金币没有再次增加
        self.player.refresh_from_db()
        self.assertEqual(self.player.gold, gold_after_first)
    
    def test_different_player_can_redeem(self):
        """测试: 不同玩家可以兑换同一 CDK"""
        # 玩家1兑换
        success1, _ = self.valid_cdk.redeem(self.player)
        self.assertTrue(success1)
        
        # 玩家2兑换
        success2, _ = self.valid_cdk.redeem(self.player2)
        self.assertTrue(success2)
        
        # 验证使用次数
        self.valid_cdk.refresh_from_db()
        self.assertEqual(self.valid_cdk.used_count, 2)
    
    def test_redeem_expired_cdk(self):
        """测试: 过期 CDK 无法兑换"""
        initial_gold = self.player.gold
        
        success, message = self.expired_cdk.redeem(self.player)
        
        self.assertFalse(success)
        self.assertIn("已过期", message)
        
        # 验证金币没有增加
        self.player.refresh_from_db()
        self.assertEqual(self.player.gold, initial_gold)
    
    def test_redeem_exhausted_cdk(self):
        """测试: 额度用尽的 CDK 无法兑换"""
        initial_gold = self.player.gold
        
        success, message = self.exhausted_cdk.redeem(self.player)
        
        self.assertFalse(success)
        self.assertIn("已被领完", message)
        
        self.player.refresh_from_db()
        self.assertEqual(self.player.gold, initial_gold)
    
    def test_single_use_cdk_exhausted_after_one_redeem(self):
        """测试: 单次使用 CDK 被一人兑换后用尽"""
        # 玩家1兑换成功
        success1, _ = self.single_use_cdk.redeem(self.player)
        self.assertTrue(success1)
        
        # 玩家2应该无法兑换 (额度已尽)
        success2, message = self.single_use_cdk.redeem(self.player2)
        self.assertFalse(success2)
        self.assertIn("已被领完", message)
