from django.db import models


class Notice(models.Model):
    """
    公告模型 - 支持登录公告、跑马灯和系统邮件通知
    
    为什么需要 start_time 和 end_time?
    --------------------------------
    游戏运营中经常需要定时公告，例如:
    - 春节活动公告: 1月10日自动生效，2月10日自动失效
    - 版本更新维护: 凌晨3点开始，5点结束
    
    有了这两个字段，管理员可以提前创建好公告，到时间自动生效/失效，
    无需半夜起来手动上下线公告。
    """
    
    # ========== 公告类型选项 ==========
    class NoticeType(models.TextChoices):
        LOGIN = 'login', '登录公告'      # 玩家登录时弹出
        MARQUEE = 'marquee', '滚动跑马灯'  # 游戏内顶部滚动
        SYSTEM = 'system', '系统邮件通知'  # 发送到玩家邮箱
    
    # ========== 状态选项 ==========
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'           # 仅管理员可见
        PUBLISHED = 'published', '已发布'  # 玩家可见
    
    # ========== 公告内容 ==========
    title = models.CharField(
        max_length=100,
        verbose_name='公告标题'
    )
    
    content = models.TextField(
        verbose_name='公告内容'
    )
    
    # ========== 公告类型 ==========
    notice_type = models.CharField(
        max_length=20,
        choices=NoticeType.choices,
        default=NoticeType.LOGIN,
        verbose_name='公告类型'
    )
    
    # ========== 优先级 (数值越大越靠前) ==========
    priority = models.IntegerField(
        default=0,
        verbose_name='优先级',
        help_text='数值越大，前端展示时越靠前'
    )
    
    # ========== 状态 ==========
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,  # 状态过滤优化
        verbose_name='状态'
    )
    
    # ========== 定时功能 ==========
    start_time = models.DateTimeField(
        db_index=True,  # 时间范围查询优化
        verbose_name='生效时间',
        help_text='公告开始展示的时间'
    )
    
    end_time = models.DateTimeField(
        db_index=True,  # 时间范围查询优化
        verbose_name='失效时间',
        help_text='公告停止展示的时间'
    )
    
    # ========== 时间戳 ==========
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        db_table = 'notices'
        verbose_name = '公告'
        verbose_name_plural = '公告列表'
        ordering = ['-priority', '-created_at']  # 优先级高的在前，同优先级按创建时间倒序
    
    def __str__(self):
        return f"[{self.get_notice_type_display()}] {self.title}"
    
    # ========== 业务方法 ==========
    
    def is_active(self):
        """
        判断公告当前是否生效
        条件: 已发布 + 当前时间在 start_time 和 end_time 之间
        """
        from django.utils import timezone
        now = timezone.now()
        return (
            self.status == self.Status.PUBLISHED and
            self.start_time <= now <= self.end_time
        )
    is_active.boolean = True  # Admin 列表中显示为图标
    is_active.short_description = '当前生效'
