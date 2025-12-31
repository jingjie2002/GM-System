from django.contrib import admin, messages
from django.utils import timezone
from .models import CDK, CDKLog
from audit.mixins import AuditLogMixin


@admin.register(CDK)
class CDKAdmin(AuditLogMixin, admin.ModelAdmin):
    """
    CDK 兑换码管理界面
    
    功能:
    1. 列表页显示兑换码状态
    2. 批量生成随机码 Action
    """
    
    # ========== 列表页配置 ==========
    list_display = [
        'code',           # 兑换码
        'item_id',        # 道具ID
        'item_count',     # 道具数量
        'max_uses',       # 总额度
        'used_count',     # 已使用
        'remaining_uses', # 剩余次数
        'is_valid',       # 是否有效
        'expires_at',     # 过期时间
        'created_at',     # 创建时间
    ]
    
    list_filter = ['item_id', 'created_at']
    search_fields = ['code']
    readonly_fields = ['used_count', 'created_at']
    
    # ========== 自定义 Actions ==========
    actions = ['generate_10_random_codes']
    
    # ========== 编辑页字段分组 ==========
    fieldsets = (
        ('🎫 兑换码', {
            'fields': ('code',)
        }),
        ('🎁 奖励设置', {
            'fields': ('item_id', 'item_count'),
            'description': '💡 道具ID: 1=金币, 2=钻石'
        }),
        ('🔢 使用限制', {
            'fields': ('max_uses', 'used_count')
        }),
        ('⏰ 有效期', {
            'fields': ('expires_at',)
        }),
        ('🔍 系统信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # ========== 自定义显示方法 ==========
    
    @admin.display(description='剩余次数')
    def remaining_uses(self, obj):
        """显示剩余可用次数"""
        remaining = obj.max_uses - obj.used_count
        if remaining <= 0:
            return '❌ 已用完'
        return remaining
    
    # ========== 自定义 Action: 批量生成随机码 ==========
    
    @admin.action(description="🎲 批量生成 10 个随机码")
    def generate_10_random_codes(self, request, queryset):
        """
        批量生成 10 个随机 8 位大写字母兑换码
        
        生成规则:
        - 码长度: 8 位大写字母
        - 道具: 100 金币 (item_id=1)
        - 额度: 每个码可用 1 次
        - 有效期: 30 天
        """
        # 默认 30 天后过期
        expires_at = timezone.now() + timezone.timedelta(days=30)
        
        # 批量生成
        created_cdks = CDK.batch_generate(
            count=10,
            item_id=1,
            item_count=100,
            max_uses=1,
            expires_at=expires_at
        )
        
        # 显示生成的码
        codes = [cdk.code for cdk in created_cdks]
        self.message_user(
            request,
            f"✅ 成功生成 10 个兑换码: {', '.join(codes)}",
            messages.SUCCESS
        )
    
    # 让 Action 在不选择任何对象时也可用
    generate_10_random_codes.acts_on_all = True


@admin.register(CDKLog)
class CDKLogAdmin(admin.ModelAdmin):
    """CDK 兑换记录管理界面"""
    
    list_display = ['player', 'cdk', 'redeemed_at']
    list_filter = ['redeemed_at']
    search_fields = ['player__nickname', 'cdk__code']
    readonly_fields = ['player', 'cdk', 'redeemed_at']
    
    def has_add_permission(self, request):
        """禁止手动添加兑换记录"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改兑换记录"""
        return False
