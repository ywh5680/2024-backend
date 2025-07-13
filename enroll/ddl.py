
import time
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

try:
    from ._ddl_conf import DDL as _DDL
except ImportError:
    import os
    val = os.getenv("DDL")
    if val is not None:
        _DDL = float(val)
    else:
        raise

def over_ddl():
    return time.time() > _DDL

def after_ddl_response(request, args, kwargs):
    return Response(
        dict(detail="server has stoppped", since=_DDL),
        status=499  # XXX: 499 is of non-standard response
    )

def after_ddl_response_for_cls(request, *args, **kwargs):
    return after_ddl_response(request, args, kwargs)

def stop_after_ddl(func_or_cls):
    '''decorator.
    currently only handles POST method
    '''
    if type(func_or_cls) is type \
            and issubclass(func_or_cls, ModelViewSet):
        class SubCls(func_or_cls):
            def create(self, request, *args, **kwargs):
                if over_ddl():
                    self.create = \
                        after_ddl_response_for_cls
                    return after_ddl_response_for_cls(request, *args, **kwargs)
                return super().create(request, *args, **kwargs)
        return SubCls
    else:
        assert callable(func_or_cls)
        class inner:
            def __new__(cls, request, *args, **kwd):
                if over_ddl():
                    cls.__new__ = after_ddl_response #type: ignore
                    return after_ddl_response(request, args, kwd)
                return func_or_cls(request, *args, **kwd)
        return inner


