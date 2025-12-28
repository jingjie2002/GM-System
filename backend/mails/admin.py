from django.contrib import admin, messages
from .models import Mail


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    """
    邮件管理界面
    
    核心功能:
    1. 列表页显示关键字段，支持过滤和搜索
    2. 编辑页分组展示字段，提升用户体验
    3. 保存时自动将当前登录管理员设置为 sender
    4. 自定义 Action: 批量领取邮件附件
    """
    
    # ========== 列表页配置 ==========
    list_display = [
        'title',        # 邮件标题
        'sender',       # 发送者(管理员)
        'receiver',     # 接收者(玩家)
        'is_global',    # 是否全服
        'is_claimed',   # 是否已领取
        'expires_at',   # 过期时间
        'created_at',   # 创建时间
    ]
    
    # 右侧过滤器
    list_filter = ['is_global', 'is_claimed', 'created_at']
    
    # 搜索字段（支持按标题、内容、玩家昵称搜索）
    search_fields = ['title', 'content', 'receiver__nickname']
    
    # 只读字段（sender 自动填充，不可手动修改）
    readonly_fields = ['sender', 'created_at']
    
    # ========== 自定义 Actions ==========
    actions = ['claim_attachments_action']
    
    # ========== 编辑页字段分组 ==========
    fieldsets = (
        ('📧 邮件内容', {
            'fields': ('title', 'content')
        }),
        ('👤 收件人设置', {
            'fields': ('receiver', 'is_global'),
            'description': '💡 选择具体玩家发送私人邮件，或勾选"全服邮件"发给所有人'
        }),
        ('🎁 道具附件', {
            'fields': ('item_id', 'item_count'),
            'classes': ('collapse',),  # 默认折叠
            'description': '💡 道具ID: 1=金币, 2=钻石'
        }),
        ('⏰ 邮件状态', {
            'fields': ('expires_at', 'is_claimed')
        }),
        ('🔍 审计信息', {
            'fields': ('sender', 'created_at'),
            'classes': ('collapse',),  # 默认折叠
            'description': '💡 系统自动记录，无需手动填写'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        重写保存方法
        
        自动设置 sender 为当前登录的管理员用户
        - request.user: Django 请求中的当前登录用户
        - change: False 表示新建，True 表示编辑
        
        仅在创建新邮件时设置 sender，编辑时不覆盖
        """
        if not change:  # 仅在创建新邮件时设置
            obj.sender = request.user
        super().save_model(request, obj, form, change)
    
    # ========== 自定义 Action: 处理并领取附件 ==========
    
    @admin.action(description="🎁 处理并领取附件")
    def claim_attachments_action(self, request, queryset):
        """
        批量领取邮件附件的 Admin Action
        
        使用方法:
        1. 在邮件列表页勾选要领取的邮件
        2. 在"动作"下拉菜单中选择"🎁 处理并领取附件"
        3. 点击"执行"按钮
        
        Args:
            request: HTTP 请求对象
            queryset: 选中的邮件 QuerySet
        """
        success_count = 0
        fail_messages = []
        
        # 遍历选中的邮件，逐个调用领取方法
        for mail in queryset:
            success, msg = mail.claim_attachment()
            if success:
                success_count += 1
            else:
                fail_messages.append(f"[{mail.title}]: {msg}")
        
        # 显示成功消息
        if success_count:
            self.message_user(
                request, 
                f"✅ 成功领取 {success_count} 封邮件的附件", 
                messages.SUCCESS
            )
        
        # 显示失败消息
        if fail_messages:
            self.message_user(
                request, 
                f"⚠️ 以下邮件领取失败: {'; '.join(fail_messages)}", 
                messages.WARNING
            )

