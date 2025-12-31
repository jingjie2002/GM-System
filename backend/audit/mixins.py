"""
审计日志 Mixin

使用方法:
在 ModelAdmin 中继承 AuditLogMixin，自动记录管理员操作

示例:
    from audit.mixins import AuditLogMixin

    class PlayerAdmin(AuditLogMixin, admin.ModelAdmin):
        ...
"""

from .models import AuditLog


def get_client_ip(request):
    """
    从请求中获取客户端 IP 地址
    
    优先从 X-Forwarded-For 获取（用于反向代理场景）
    否则从 REMOTE_ADDR 获取
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuditLogMixin:
    """
    审计日志 Mixin
    
    在 ModelAdmin 中继承此类，会自动记录:
    - 创建操作
    - 修改操作
    - 删除操作
    
    原理:
    重写 save_model 和 delete_model 方法，在执行原操作后写入审计日志
    """
    
    def save_model(self, request, obj, form, change):
        """
        重写保存方法，自动记录审计日志
        
        Args:
            request: HTTP 请求对象
            obj: 被保存的模型实例
            form: 表单对象
            change: True=修改, False=创建
        """
        # 1. 先调用原始保存逻辑
        super().save_model(request, obj, form, change)
        
        # 2. 构建操作详情
        if change:
            action = '修改'
            # 获取修改的字段
            changed_fields = form.changed_data
            if changed_fields:
                details = f"修改字段: {', '.join(changed_fields)}"
            else:
                details = "无字段变更"
        else:
            action = '创建'
            details = "新建记录"
        
        # 3. 写入审计日志
        AuditLog.objects.create(
            admin=request.user,
            action=action,
            app_label=obj._meta.app_label,
            model_name=obj._meta.model_name,
            target=str(obj),
            details=details,
            ip_address=get_client_ip(request)
        )
    
    def delete_model(self, request, obj):
        """
        重写删除方法，自动记录审计日志
        """
        # 先记录日志（删除后 obj 就没了）
        AuditLog.objects.create(
            admin=request.user,
            action='删除',
            app_label=obj._meta.app_label,
            model_name=obj._meta.model_name,
            target=str(obj),
            details="删除记录",
            ip_address=get_client_ip(request)
        )
        
        # 再执行删除
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """
        重写批量删除方法，自动记录审计日志
        """
        # 先记录每个被删除的对象
        for obj in queryset:
            AuditLog.objects.create(
                admin=request.user,
                action='批量删除',
                app_label=obj._meta.app_label,
                model_name=obj._meta.model_name,
                target=str(obj),
                details="批量删除记录",
                ip_address=get_client_ip(request)
            )
        
        # 再执行删除
        super().delete_queryset(request, queryset)
