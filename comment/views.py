from django.db import IntegrityError
from django.shortcuts import get_object_or_404

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
    
    def get(self, request: Request) -> Response:
        """获取评论列表"""
        try:
            limit = int(request.query_params.get("limit", 20))
            start = int(request.query_params.get("start", 0))
        except ValueError:
            raise ParseError("limit和start参数必须是整数")
                
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
        # 使用get_object_or_404简化代码
        parent = get_object_or_404(Comment, id=parent_id)
        replies = Comment.objects.filter(parent=parent).order_by('datetime')
        serializer = CommentSerializer(replies, many=True)
        
        return Response(serializer.data)
