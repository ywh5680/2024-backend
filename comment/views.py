from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.throttling import AnonRateThrottle
from rest_framework.decorators import throttle_classes

from .models import Comment
from .serializers import CommentSerializer


class CommentThrottle(AnonRateThrottle):
    """评论限流器"""
    rate = "10/min"


class CommentView(APIView):
    """评论视图"""
    throttle_classes = [CommentThrottle]
    
    def get(self, request: Request) -> Response:
        """获取评论列表"""
        def parse_int(sth, default_if_omit):
            p = request.query_params.get(sth)
            if p is None: 
                return default_if_omit
            try: 
                return int(p)
            except ValueError:
                raise ParseError(f"{sth} 不是有效的整数")
                
        limit = parse_int("limit", 20)
        start = parse_int("start", 0)
        
        comments = Comment.objects.filter(parent=None).order_by('-datetime')[start:start+limit]
        serializer = CommentSerializer(comments, many=True)
        
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """创建新评论"""
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=201)
            except IntegrityError as e:
                return Response({"detail": str(e)}, status=422)
        
        return Response(serializer.errors, status=400)


class CommentReplyView(APIView):
    """评论回复视图"""
    throttle_classes = [CommentThrottle]
    
    def get(self, request: Request, parent_id: int) -> Response:
        """获取特定评论的回复"""
        # 检查父评论是否存在
        parent = Comment.objects.filter(id=parent_id).first()
        if not parent:
            raise ValidationError(f"ID为{parent_id}的评论不存在")
            
        replies = Comment.objects.filter(parent_id=parent_id).order_by('datetime')
        serializer = CommentSerializer(replies, many=True)
        
        return Response(serializer.data)
