from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
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
    throttle_classes = [CommentThrottle]

    def get(self, request, page=1):  # 新增：page参数，默认第一页
        """
        调整后：
        /comment/ 返回第一页评论
        /comment/1/ 返回第1页评论
        /comment/2/ 返回第2页评论（每页10条）
        """
        try:
            page = int(page)  # 确保页码为整数
            if page < 1:
                raise ParseError("页码必须大于0")
        except ValueError:
            raise ParseError("页码必须是整数")

        all_comments = Comment.objects.order_by('id')
        paginator = Paginator(all_comments, 10)  # 新增：每页10条数据

        try:
            page_comments = paginator.page(page)
        except EmptyPage:
            """处理页码超出范围的情况"""
            return Response([], status=200)

        result = []
        for comment in page_comments:

            result.append({
                "id": comment.id,
                "content": comment.content,
                "datetime": comment.datetime.isoformat(),  # 标准化时间格式
                "qq": comment.qq,
                "email": comment.email,
                "orid": comment.parent.id if comment.parent else None  # 新增：父评论ID字段
            })

        response_data = {
            "comments": result,
            "has_next": page_comments.has_next(),
            "next_page": page + 1 if page_comments.has_next() else None
        }

        return Response(response_data)

    def post(self, request: Request) -> Response:
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=201)
            except IntegrityError as e:
                return Response({"detail": str(e)}, status=422)

        return Response(serializer.errors, status=400)


class CommentReplyView(APIView):
    throttle_classes = [CommentThrottle]

    def get(self, request: Request, parent_id: int) -> Response:
        parent = get_object_or_404(Comment, id=parent_id)
        replies = Comment.objects.filter(parent=parent).order_by('id')

        result = []
        for comment in replies:

            result.append({
                "id": comment.id,
                "content": comment.content,
                "datetime": comment.datetime.isoformat(),
                "qq": comment.qq,
                "email": comment.email,
                "orid": comment.parent.id if comment.parent else None
            })

        return Response(result)
