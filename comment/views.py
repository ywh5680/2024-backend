from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.throttling import AnonRateThrottle

from .models import Comment
from .serializers import CommentSerializer


class CommentThrottle(AnonRateThrottle):
    """评论限流器"""
    rate = "10/min"


class CommentView(APIView):
    """评论视图"""
    throttle_classes = [CommentThrottle]
    
    def get(self, request: Request, page=1) -> Response:
        """获取评论列表
        
        参数:
            page: 页码，默认为1
        """
        try:
            page = int(page)
            if page < 1:
                raise ParseError("页码必须大于0")
        except ValueError:
            raise ParseError("页码必须是整数")
                
        # 获取所有评论，不再过滤 parent=None
        comments = Comment.objects.all().order_by('-datetime')
        
        # 使用Django的分页器
        paginator = Paginator(comments, 10)  # 每页10条
        
        try:
            page_comments = paginator.page(page)
        except EmptyPage:
            # 如果页码超出范围，返回空列表
            return Response([])
        
        serializer = CommentSerializer(page_comments, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """创建新评论"""
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=201)
            except IntegrityError as e:
                return Response({"detail": str(e)}, status=422)
        
        return Response(serializer.errors, status=400)



