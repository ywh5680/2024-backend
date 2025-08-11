
import random

from django.conf import settings
if settings.DEBUG:
    def log(*a): print(*a) #type: ignore
else:
    def log(*_): pass
from .models import EnrollModel
from .email_livecycle import ALIVE_MINUTES
from .serializers import EnrollSerializer
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q

from .verify_code import sender
from .ddl import stop_after_ddl, over_ddl
from django.core.cache import cache

@api_view(['GET'])
def query_ddl(_: Request) -> Response:
    status = 200
    if over_ddl():
        status = 499
    return Response({}, status=status)


def gen_code() -> int:
    code = random.randint(1000, 9999)
    return code


def format_code(i: int) -> str:
    return '%04d' % i


def err_response(msg: str, status = 400):
    return Response(
        data=dict(detail=msg),
        status=status
    )

class SendCodeThrottle(AnonRateThrottle):
    rate = "6/min"

class GetStatusThrottle(AnonRateThrottle):
    rate = "1/sec"

@api_view(['POST'])
@throttle_classes([SendCodeThrottle])
@stop_after_ddl
def send(request: Request) -> Response:
    email = request.data.get('email', None)
    if email is None:
        raise ValidationError("email is required but missing")
    
    key = f"verify_code_{email}"

    if cache.get(key) is not None:
        # 发过了验证码，还没有过期
        return Response(data=dict(alive_minutes=ALIVE_MINUTES),
                        status=200)
    else:
        code = gen_code()
        cache.set(key, code, timeout=ALIVE_MINUTES * 60)
        # 发验证码
        sender.send_code(code, [email])
        return Response(data=dict(alive_minutes=ALIVE_MINUTES),
                        status=200)

@stop_after_ddl
class EnrollViewSet(ModelViewSet):
    queryset = EnrollModel.objects.all()
    serializer_class = EnrollSerializer

@api_view(['POST'])
@throttle_classes([GetStatusThrottle])
def get_status(request: Request) -> Response:
    keyword = request.data.get('keyword', None)

    filters = Q()
    if keyword is not None:
        filters |= Q(email=keyword) | Q(phone=keyword) | Q(qq=keyword) | Q(uid=keyword)

    enrollments = EnrollModel.objects.filter(filters).first()

    if not enrollments:
        raise ValidationError("没有找到符合条件的报名信息")

    return Response(
        dict(idx=enrollments.status, progress=enrollments.get_status_display()),
    )
