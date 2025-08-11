

from datetime import datetime, timezone
from django.db import models
from .email_livecycle import ALIVE_DURATION

EmailFieldInst = models.EmailField(
    max_length=36, unique=True, verbose_name="邮箱")

CODE_HELP_TEXT = "验证码"

class IntegerChoices:
    '''Sequnence:
      - `__iter__` yields tuple[int, str], and starts from `start`'''
    start = 0
    data: 'tuple[str,...]'
    def __init__(self, ls: 'tuple[str,...]', start=None):
        if start is not None: self.start = start
        self.data = ls
    def __iter__(self):
        for (i, s) in enumerate(self.data, start=self.start):
            yield (i, s)
    def __len__(self): return len(self.data)
    def __getitem__(self, i) -> str:
        return self.data[i]
    def index(self, ele): return self.data.index(ele)

genIntegerChoices = IntegerChoices

def _center_as_0_len(sized) -> int:
    le = len(sized)
    (quo, rem) = divmod(le, 2)
    assert rem == 1
    return quo

class EnrollStatus(IntegerChoices):
    def __init__(self, ls):
        start = -_center_as_0_len(ls)
        super().__init__(ls, start)
    def get_index(self, item) -> int:
        return self.index(item) - self.start
    def get_str(self, index: int):
        return self[index-self.start]


class EnrollModel(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "报名信息"
    # the order matters and this is symmetric
    schedules = EnrollStatus((
        "未录取",
        "二面失败",
        "国庆题未完成",
        "一面失败",
        "已报名", # idx: 0
        "一面已到",
        "国庆题已完成",
        "二面已参与",
        "已录取",
    ))
    @classmethod
    def progress_idx(cls, status: str) -> int:
        '''@raises: ValueError'''
        return cls.schedules.get_index(status)
    @classmethod
    def get_status_str(cls, idx: int) -> str:
        return cls.schedules.get_str(idx)
    # the order matters!
    # serializers.EnrollSerializer requires this to have
    #   __getitem__(i: int) -> str
    # and SmallIntegerField requires this to be
    #  Iterable[
    #   tuple[`SmallInt`, str] |
    #   tuple[str, Iterable[tuple[`SmallInt`, str]]]
    #  ]
    # NOTE: the order must match that of .admin.username2department
    departments = genIntegerChoices((
        "程序开发",
        "Web开发",
        "游戏开发",
        "APP开发",
        "UI设计",
        "ios",
    ))
    name = models.CharField(max_length=20, verbose_name="姓名")
    uid = models.PositiveBigIntegerField(unique=True, verbose_name="学号")
    major = models.CharField(max_length=20, verbose_name="年级专业")
    phone = models.PositiveBigIntegerField(unique=True, verbose_name="手机号码")
    # 0..9,223,372,036,854,775,807 (max of int64), bigger than 11 digits
    email = EmailFieldInst
    department = models.SmallIntegerField(choices=departments, verbose_name="意向部门")
    content = models.CharField(null=True, max_length=200, verbose_name="为什么要加入爱特工作室")
    status = models.SmallIntegerField(choices=schedules, default=0, verbose_name="报名状态")

    qq = models.PositiveBigIntegerField(unique=True, null=True, name="qq", verbose_name="QQ号")
    comment = models.CharField(max_length=64, blank=True, verbose_name="备注")
    # XXX: qq, content also need to be marked as not required in ./admin

    def __str__(self):
        return self.name

    STATUS_QUERY_CAND = (
        'email', 'phone', 'qq', 'uid')
    STATUS_QUERY_FUZZY_CAND = ('name',)  # name is not unique
