
from django.conf import settings
import warnings
from .verify_code_impl import *

_CONFS = (
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "DEFAULT_FROM_EMAIL"
)

email_conf = dict()

# Get email configuration from settings
for attr in _CONFS:
    email_conf[attr] = getattr(settings, attr, None)
del attr

_ADMINS = getattr(settings, "ADMINS", [])

sender = Sender(
    auth_user=email_conf["EMAIL_HOST_USER"],
    auth_password=email_conf["EMAIL_HOST_PASSWORD"],
    from_email=email_conf["DEFAULT_FROM_EMAIL"],
    admins=_ADMINS)


if not all(i in email_conf and email_conf[i] is not None for i in ("EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD")):
    # overwrite send_code
    Solution = """
        Solution:
        1) Check your email_config.json file is correctly configured
        2) Make sure the file is in the project root directory
"""
    warnings.warn("Email configuration is missing or incomplete, `send_code` will raise Error if called" + Solution,
                  RuntimeWarning)
    def send_code(*_a, **_kw):
        raise OSError(
            """Email configuration is missing or incomplete.

            """ + Solution
        )
    sender._send_code = sender.send_code #type: ignore
    sender.send_code = send_code
    del send_code

del email_conf
