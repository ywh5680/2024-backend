
from django.contrib import admin
from . import models, export

@admin.register(models.VerifyCodeModel)
class VerifyCodeAdmin(admin.ModelAdmin):
    list_display = "email", "send_time"
    # send_time is marked as `auto_now=True`, so not editable
    #list_editable = "send_time",


# NOTE: the order must match that of .EnrollModel.departments
username2department = (
    'py',
    'web',
    'game',
    'app',
    'ui',
    'ios'
)
def uname2departmentIdx(name):
    return username2department.index(name)

@admin.register(models.EnrollModel)
class EnrollAdmin(admin.ModelAdmin):
    list_display = "name", "email", "major", "qq", "status", "comment", "department"
    list_editable = "status", "comment"
    list_filter = "department",
    search_fields = 'name',
    search_help_text = 'Search for name'
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for i in 'qq', 'content':
            form.base_fields[i].required = False
        return form

    def get_queryset(self, request):
        # 获取当前登录的用户
        user = request.user
        # 如果用户是超级用户，则返回所有记录
        if user.is_superuser:
            return super().get_queryset(request)
        # 否则，只返回该用户名等于用户名称的记录
        return super().get_queryset(request).filter(department=
                                                    uname2departmentIdx(user.username)
        )


admin.site.add_action(export.export_csv)
