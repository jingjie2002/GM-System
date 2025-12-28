from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """
    公告管理界面
    
    功能:
    1. 列表页显示关键字段和当前生效状态
    2. 支持按状态和类型过滤
    3. 支持按标题和内容搜索
    """
    
    # ========== 列表页配置 ==========
    list_display = [
        'title',           # 公告标题
        'notice_type',     # 公告类型
        'status',          # 状态
        'priority',        # 优先级
        'is_active',       # 当前是否生效（动态计算）
        'start_time',      # 生效时间
        'end_time',        # 失效时间
        'created_at',      # 创建时间
    ]
    
    # 右侧过滤器
    list_filter = ['status', 'notice_type', 'created_at']
    
    # 搜索字段
    search_fields = ['title', 'content']
    
    # 可直接在列表页编辑的字段
    list_editable = ['priority', 'status']
    
    # 只读字段
    readonly_fields = ['created_at']
    
    # 默认排序
    ordering = ['-priority', '-created_at']
    
    # ========== 编辑页字段分组 ==========
    fieldsets = (
        ('📢 公告内容', {
            'fields': ('title', 'content')
        }),
        ('🏷️ 公告设置', {
            'fields': ('notice_type', 'priority', 'status'),
            'description': '💡 优先级数值越大，前端展示越靠前'
        }),
        ('⏰ 定时设置', {
            'fields': ('start_time', 'end_time'),
            'description': '💡 公告仅在生效时间内对玩家可见'
        }),
        ('🔍 系统信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
