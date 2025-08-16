from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError, ValidationError
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
    queryset = Comment.objects.all().order_by('-datetime')
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    throttle_classes = [CommentThrottle]
    
    def list(self, request: Request, *args, **kwargs) -> Response:
        """获取评论列表（对应GET请求）- 保持原有接口格式"""
        # 获取页码参数，支持URL路径和查询参数两种方式
        page = kwargs.get('page')  # 从URL路径获取页码
        if page is None:
            page = request.query_params.get('page', 1)  # 从查询参数获取页码
        
        try:
            page = int(page)
            if page < 1:
                raise ParseError("页码必须大于0")
        except ValueError:
            raise ParseError("页码必须是整数")
        
        # 获取所有评论，保持原有逻辑
        comments = Comment.objects.all().order_by('-datetime')
        
        # 使用Django的分页器，保持原有分页逻辑
        paginator = Paginator(comments, 10)  # 每页10条
        
        try:
            page_comments = paginator.page(page)
        except EmptyPage:
            # 如果页码超出范围，返回空列表，保持原有行为
            return Response([])
        
        serializer = CommentSerializer(page_comments, many=True)
        return Response(serializer.data)
    
    def create(self, request: Request, *args, **kwargs) -> Response:
        """创建新评论（对应POST请求）- 保持原有接口格式"""
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=201)
            except IntegrityError as e:
                return Response({"detail": str(e)}, status=422)
        
        return Response(serializer.errors, status=400)



