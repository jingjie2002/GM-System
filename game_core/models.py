from django.db import models


class Project(models.Model):
    # 公司/项目名称
    name = models.CharField(max_length=100, verbose_name="项目名称")
    # 图标上的文字 (如 "XD", "Py")
    logo_text = models.CharField(max_length=5, default="XD")
    # 图标背景色 (存储 CSS 颜色代码，如 #0075ff)
    logo_color = models.CharField(max_length=20, default="#0075ff")
    # 预算
    budget = models.CharField(max_length=50, verbose_name="预算", default="$0")
    # 完成度 (0-100)
    completion = models.IntegerField(default=0, verbose_name="完成度")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "项目管理"
        verbose_name_plural = "项目管理"