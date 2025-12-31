from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    审计日志管理界面
    
    只读界面，用于查看操作记录
    """
    
    list_display = [
        'created_at',     # 操作时间
        'admin',          # 操作者
        'action',         # 操作类型
        'app_label',      # 应用模块
        'model_name',     # 模型名称
        'target',         # 被操作对象
        'ip_address',     # IP地址
    ]
    
    list_filter = ['action', 'app_label', 'admin', 'created_at']
    search_fields = ['target', 'details', 'admin__username']
    readonly_fields = ['admin', 'action', 'app_label', 'model_name', 'target', 'details', 'ip_address', 'created_at']
    
    # 按时间倒序显示
    ordering = ['-created_at']
    
    # 禁止添加和修改（审计日志只能查看）
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # 只有超级管理员可以删除审计日志
        return request.user.is_superuser
