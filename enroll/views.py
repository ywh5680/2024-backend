
import random

from django.core.exceptions import ValidationError
from django.conf import settings
if settings.DEBUG:
    def log(*a): print(*a) #type: ignore
else:
    def log(*_): pass
from .models import VerifyCodeModel, EnrollModel
from .email_livecycle import ALIVE_MINUTES
from .serializers import EnrollSerializer
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response

from .verify_code import sender
from .ddl import stop_after_ddl, over_ddl

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

# XXX: if using stop_after_ddl as the top decorator, it just response
# `Forbidden (CSRF cookie not set.)` all time, donno why :(
@api_view(['POST'])
@throttle_classes([SendCodeThrottle])
@stop_after_ddl
def send(request: Request) -> Response:
    email = request.data.get('email', None) #type: ignore
    if email is None:
        return err_response("email is required but missing", status=422)
    log(email)
    obj = VerifyCodeModel.objects.filter(email=email).first()
    code = gen_code()
    def create_new():
        nonlocal obj
        try:
            obj = VerifyCodeModel.objects.create(email=email, code=format_code(code))
        except ValidationError:
            return err_response("邮箱格式错误", status=422)

    if obj is not None:
        if obj.try_remove_if_unalive():
            res = create_new()
            if res is not None:
                return res
        obj.code = code
    else:
        res = create_new()
        if res is not None:
            return res
    assert obj is not None
    obj.save()

    log(code)

    err_msg = sender.send_code(code, [email])
    if err_msg is None:
        return Response(data=dict(alive_minutes=ALIVE_MINUTES),
                        status=200)
    else:
        return err_response(err_msg , status=500)

@stop_after_ddl
class EnrollViewSet(ModelViewSet):
    queryset = EnrollModel.objects.all()
    serializer_class = EnrollSerializer
    def create(self, request: Request, *args, **kwargs):
       sender.send_enrollee_info(request.data)
       return super().create(request, *args, **kwargs)

@api_view(['POST'])
@throttle_classes([GetStatusThrottle])
def get_status(request: Request) -> Response:
    try:
        # we know (isinstance(request.data, dict))
        tup = EnrollModel.get_status(request.data) #type:ignore
    except KeyError as e:
        return err_response(str(e), status=400)
    except EnrollModel.DoesNotExist as e:
        return err_response(str(e), status=404)
    except EnrollModel.MultipleObjectsReturned as e:
        return err_response(str(e), status=406) # or maybe 300
    else:
        (idx, progress) = tup
        return Response(
            dict(idx=idx, progress=progress),
        )
