
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ParseError
from .models import *
from .serializers import commentSerializer


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
        comments = comment.objects.filter(parent=None).order_by('-id')[start:start+limit]
        serializer = commentSerializer(comments, many=True).data
        for i in serializer:
            sub_comment = comment.objects.filter(parent=i['id'])
            i['children'] = commentSerializer(sub_comment, many=True).data
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
                comment.objects.create(content=content, parent=parent, qq=qq, email=email)
            except IntegrityError as e:
                return Response(dict(detail=str(e)), status=422)
            else:
                return Response({}, status=200)
        if parent_id is None:
            return create_return(None)
        parent = comment.objects.filter(id=parent_id).first()
        if parent is not None:
            return create_return(parent)
        else:
            return Response(dict(detail='parent不存在'), status=404)
