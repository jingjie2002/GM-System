from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    玩家模型的 Admin 后台配置
    """
    
    # =====================================
    # 📋 列表页配置
    # =====================================
    
    # 列表中显示的字段（从左到右）
    list_display = [
        'nickname',     # 昵称
        'level',        # 等级
        'gold',         # 金币
        'diamond',      # 钻石
        'status',       # 账号状态
        'created_at',   # 注册时间
    ]
    
    # 可以点击进入详情的字段
    list_display_links = ['nickname']
    
    # 右侧筛选栏
    list_filter = [
        'status',       # 按状态筛选
        'level',        # 按等级筛选
        'created_at',   # 按注册时间筛选
    ]
    
    # 搜索框可搜索的字段
    search_fields = [
        'nickname',     # 按昵称搜索
        'id',           # 按玩家ID搜索
    ]
    
    # 默认排序（-表示倒序）
    ordering = ['-created_at']
    
    # 每页显示数量
    list_per_page = 20
    
    # =====================================
    # 📝 详情页配置
    # =====================================
    
    # 只读字段（不可编辑）
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    # 字段分组布局
    fieldsets = [
        ('基本信息', {
            'fields': ['id', 'nickname']
        }),
        ('游戏数据', {
            'fields': ['level', 'gold', 'diamond']
        }),
        ('账号状态', {
            'fields': ['status']
        }),
        ('时间信息', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']  # 默认折叠
        }),
    ]
