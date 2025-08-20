from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import AnonRateThrottle
from rest_framework.pagination import PageNumberPagination

from .models import Comment
from .serializers import CommentSerializer


class CommentThrottle(AnonRateThrottle):
    """评论限流器"""
    rate = "10/min"


class CommentPagination(PageNumberPagination):
    """评论分页器"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentViewSet(ModelViewSet):
    """评论视图集"""
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    throttle_classes = [CommentThrottle]
    http_method_names = ['get', 'post']  # 只允许GET和POST方法
    
    def get_queryset(self):
        """只返回已审核通过的评论"""
        if self.request.user.is_staff:
            # 管理员可以看到所有评论
            return Comment.objects.all().order_by('-datetime')
        # 普通用户只能看到已审核通过的评论
        return Comment.objects.filter(status=Comment.AuditStatus.APPROVED).order_by('-datetime')



