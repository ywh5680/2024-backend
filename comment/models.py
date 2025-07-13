from django.db import models


class comment(models.Model):
    content = models.TextField(verbose_name='评论内容')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, verbose_name='父评论id')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    qq = models.IntegerField(verbose_name='QQ号', null=True)
    email = models.CharField(max_length=20, verbose_name='邮箱', null=True)
    # XXX: parent, qq, email also need to be marked as not required in ./admin
