
from django.conf import settings
import warnings
from .verify_code_impl import *

_CONFS = (
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "DEFAULT_FROM_EMAIL"
)

email_conf = dict()

for attr in _CONFS:
    email_conf[attr] = getattr(settings, attr, None)
del attr

try:
    from . import _email_conf
    def _load(name):
        res = getattr(_email_conf, name, None)
        if res is not None and name in email_conf:
            warnings.warn(f"settings.{name} is overwritten by {_email_conf}",
                          ImportWarning)
        email_conf[name] = res
    for i in _CONFS:
        _load(i)

except ImportError:
    pass

_ADMINS = getattr(settings, "ADMINS", [])

sender = Sender(
    auth_user=email_conf["EMAIL_HOST_USER"],
    auth_password=email_conf["EMAIL_HOST_PASSWORD"],
    from_email=email_conf["DEFAULT_FROM_EMAIL"],
    admins=_ADMINS)


if not all(i in email_conf for i in ("EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD")):
    # overwrite send_code
    Solution = """
        Solution:
        1) set such an environment variable;
        2) modify settings.EMAIL_HOST_PASSWORD to something other than None
"""
    warnings.warn("NO email conf found, `send_code` will raise Error if called" + Solution,
                  RuntimeWarning)
    def send_code(*_a, **_kw):
        raise OSError(
            """EMAIL_HOST_PASSWORD environment variable is not set,
            which is required to send email.

            """ + Solution
        )
    sender._send_code = sender.send_code #type: ignore
    sender.send_code = send_code
    del send_code

del email_conf
