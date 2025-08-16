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



