from django.db import models


class Comment(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = '评论'
        
    class AuditStatus(models.IntegerChoices):
        PENDING = 0, '待审核'
        APPROVED = 1, '已通过'
        REJECTED = 2, '已拒绝'
        
    content = models.TextField(verbose_name='评论内容')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, verbose_name='父评论id')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    qq = models.IntegerField(verbose_name='QQ号', null=True)
    email = models.CharField(max_length=50, verbose_name='邮箱', null=True)
    status = models.IntegerField(
        choices=AuditStatus.choices,
        default=AuditStatus.PENDING,
        verbose_name='审核状态'
    )
