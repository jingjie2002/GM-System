from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    """
    审计日志模型
    
    记录管理员在后台的所有敏感操作，用于:
    1. 合规性审计 - 应对玩家投诉或法律审计
    2. 安全追溯 - 追查内部人员滥用权限
    3. 故障排查 - 回溯操作历史定位问题
    """
    
    # ========== 操作者信息 ==========
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        db_index=True,  # 按管理员过滤优化
        verbose_name='操作管理员'
    )
    
    # ========== 操作内容 ==========
    action = models.CharField(
        max_length=50,
        verbose_name='操作类型',
        help_text='如: 创建、修改、删除、发放邮件、封禁玩家'
    )
    
    app_label = models.CharField(
        max_length=50,
        verbose_name='应用模块',
        help_text='如: players, mails, cdks'
    )
    
    model_name = models.CharField(
        max_length=50,
        verbose_name='模型名称',
        help_text='如: Player, Mail, CDK'
    )
    
    target = models.CharField(
        max_length=200,
        verbose_name='被操作对象',
        help_text='如: 玩家 "小明"'
    )
    
    details = models.TextField(
        blank=True,
        verbose_name='详细改动',
        help_text='如: 金币从 100 变为 1000'
    )
    
    # ========== 操作环境 ==========
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP地址'
    )
    
    # ========== 时间戳 ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='操作时间'
    )
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.admin} {self.action} {self.target}"
