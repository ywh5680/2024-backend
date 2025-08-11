
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError
from .models import Comment
from .serializers import CommentSerializer


class CommentView(APIView):
    def get(self, request: Request) -> Response:
        def parse_int(sth, default_if_omit):
            p = request.query_params.get(sth) # str|None
            if p is None: res = default_if_omit
            else:
                try: res = int(p)
                except ValueError:
                    raise ParseError(sth + " is not an integer") # def: code=400
            return res
        limit = parse_int("limit", 20)
        start = parse_int("start", 0)
        comments = Comment.objects.filter(parent=None).order_by('-id')[start:start+limit]
        serializer = CommentSerializer(comments, many=True).data
        for i in serializer:
            sub_comment_ids = list(Comment.objects.filter(parent=i['id']).values_list('id', flat=True))
            i['children'] = sub_comment_ids
        return Response(serializer)

    def post(self, request: Request) -> Response:
        content = request.data.get("content") #type: ignore
        parent_id = request.data.get("parent") #type: ignore
        qq = request.data.get("qq")
        email = request.data.get("email")
        if qq is None and email is None:
            return Response(dict(detail="at least one of qq or email shall be given"), status=400)
        def create_return(parent):
            try:
                Comment.objects.create(content=content, parent=parent, qq=qq, email=email)
            except IntegrityError as e:
                return Response(dict(detail=str(e)), status=422)
            else:
                return Response({}, status=200)
        if parent_id is None:
            return create_return(None)
        parent = Comment.objects.filter(id=parent_id).first()
        if parent is not None:
            return create_return(parent)
        else:
            return Response(dict(detail='parent不存在'), status=404)


class CommentReplyView(APIView):
    def get(self, request, parent_id):
        replies = Comment.objects.filter(parent_id=parent_id).order_by('datetime')
        data = CommentSerializer(replies, many=True).data
        for i in data:
            sub_comment_ids = list(Comment.objects.filter(parent=i['id']).values_list('id', flat=True))
            i['children'] = sub_comment_ids
        return Response(data)
