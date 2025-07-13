

from html import escape as html_escape
from string import Template
import smtplib  # for error handle
from pathlib import Path
from django.core.mail import send_mail
from .email_livecycle import ALIVE_MINUTES


# use Template over `{}`-format to prevent getting
# confused with JS's block syntax.
MSG = Template("欢迎报名爱特工作室，你的验证码是：$code\n  有效期：$alive_minutes 分钟")
def slurp(fn):
    f = open(fn, encoding="utf-8")
    res = f.read()
    return res

H_MSG = Template(
    slurp(
        Path(__file__).with_name("verify_code.html")
    ))

def substitute(t, code):
    return t.substitute(code=code, alive_minutes=ALIVE_MINUTES)

def mapping_to_html_table(d):
    html_table = """<table border="1"><tbody>"""
    for (key, value) in d.items():
        html_table += f'''
<tr><th>{html_escape(str(key))}</th>
    <th>{html_escape(str(value))}</th></tr>'''
    return html_table + "</tbody></table>"

class Sender:
    def __init__(self, auth_user=None, auth_password=None, from_email=None,
                admins: 'list[tuple[str, str]]' = []):
        self.auth_user = auth_user
        self.auth_password = auth_password
        self.from_email = from_email
        self.admins = admins  # do not modify this list
    def send_mail(self, subject: str, msg: str, emails: list, html_message=None):
        return send_mail(
                subject, msg,
                self.from_email, # None means using the value of DEFAULT_FROM_EMAIL setting
                emails,
                html_message=html_message,
                auth_user=self.auth_user,
                auth_password=self.auth_password
            )
    def send_enrollee_info(self, data):
        return self.send_mail(
            "Enrollee for itstudio: " + data["name"],
            str(data),
            self.admins,
            mapping_to_html_table(data)
        )
    def send_code(self, code, emails) -> 'None|str':
        """returns None is not error (successful).
        If error occurs, returns error message (str).
        """
        num_sent = 0
        err_msg = "success"
        try:
            num_sent = self.send_mail(
                '报名验证', substitute(MSG, code=code),
                emails,
                html_message=substitute(H_MSG, code=code)
            )
        except smtplib.SMTPServerDisconnected:
            err_msg = "SMTP server disconnected"
        except smtplib.SMTPResponseException as e:
            err_msg = e.smtp_error
            if type(err_msg) is bytes:
                err_msg = err_msg.decode()
        except smtplib.SMTPException as e:
            err_msg = "error"
        if num_sent != 0:
            return None
        assert type(err_msg) is str  # just comfort type cheking
        return err_msg
