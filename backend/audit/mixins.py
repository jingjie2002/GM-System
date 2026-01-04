"""
审计日志 Mixin (修复版)
兼容 Django Admin 和 DRF API
"""
from .models import AuditLog

def get_client_ip(request):
    """获取客户端 IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class AuditLogMixin:
    """
    审计日志混入类
    继承此类后，Admin 操作和 API 操作都会自动记录日志
    """

    # ==========================================
    # 📝 1. 核心记录逻辑 (通用)
    # ==========================================
    def _record_log(self, request, obj, action, details):
        """写入数据库的统一方法"""
        try:
            # 安全检查：如果用户未登录(如 AllowAny 接口)，admin 设为 None
            # request.user 可能是 AnonymousUser，is_authenticated 是方法或属性
            user = request.user if request.user and request.user.is_authenticated else None

            AuditLog.objects.create(
                admin=user,
                action=action,
                app_label=obj._meta.app_label,
                model_name=obj._meta.model_name,
                target=str(obj),
                details=details,
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            # 打印错误但不中断业务流，防止日志系统搞挂主业务
            print(f"❌ 审计日志记录失败: {e}")

    # ==========================================
    # 🔌 2. 适配 DRF API (Vue 前端调用)
    # ==========================================
    def perform_create(self, serializer):
        """API: 创建"""
        instance = serializer.save()
        # ViewSet 中 request 对象在 self.request
        self._record_log(self.request, instance, '创建', '通过 API 创建')

    def perform_update(self, serializer):
        """API: 修改"""
        instance = serializer.save()
        self._record_log(self.request, instance, '修改', '通过 API 修改')

    def perform_destroy(self, instance):
        """API: 删除"""
        self._record_log(self.request, instance, '删除', '通过 API 删除')
        instance.delete()

    # ==========================================
    # 🕵️ 3. 适配 Django Admin 后台
    # ==========================================
    def save_model(self, request, obj, form, change):
        """Admin: 保存/修改"""
        super().save_model(request, obj, form, change)

        if change:
            action = '修改'
            changed_fields = form.changed_data
            details = f"修改字段: {', '.join(changed_fields)}" if changed_fields else "无字段变更"
        else:
            action = '创建'
            details = "后台新建记录"

        self._record_log(request, obj, action, details)

    def delete_model(self, request, obj):
        """Admin: 删除"""
        self._record_log(request, obj, '删除', "后台删除记录")
        super().delete_model(request, obj)