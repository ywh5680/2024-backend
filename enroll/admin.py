
from django.contrib import admin
from django.utils.html import format_html
from . import models, export

@admin.register(models.VerifyCodeModel)
class VerifyCodeAdmin(admin.ModelAdmin):
    list_display = "email", "send_time", "is_alive_display"
    readonly_fields = ("send_time",)
    search_fields = ("email",)
    
    def is_alive_display(self, obj):
        is_alive = obj.is_alive()
        if is_alive:
            return format_html('<span style="color: green;">有效</span>')
        return format_html('<span style="color: red;">已过期</span>')
    is_alive_display.short_description = "验证码状态"


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
    list_display = ("name", "email", "major", "qq", "status", "comment", "department_display")
    list_editable = ("status", "comment")
    list_filter = ("department", "status")
    search_fields = ("name", "email", "uid", "phone", "qq")
    search_help_text = '搜索姓名、邮箱、学号、手机号或QQ'
    list_per_page = 20
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'uid', 'major', 'phone', 'email', 'qq')
        }),
        ('申请信息', {
            'fields': ('department', 'content')
        }),
        ('状态', {
            'fields': ('status', 'comment')
        }),
    )
    
    actions = ['mark_as_accepted', 'mark_as_rejected', 'mark_as_interview1_passed', 'mark_as_interview2_passed']
    
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

    @admin.display(description="意向部门")
    def department_display(self, obj):
        """
        一个健壮的、用于显示部门中文名称的方法。
        """
        # 从模型中获取 departments 元组，这部分是正确的
        departments = models.EnrollModel.departments

        # 检查 obj.department 是否是一个有效的整数，并且在索引范围内
        if isinstance(obj.department, int) and 0 <= obj.department < len(departments):
            # 如果是有效的，就安全地返回值
            return departments[obj.department]
        else:
            # 如果不是有效的（比如是 None, 负数, 或者超出范围的大数）
            # 就返回一个带警告标志的、友好的提示信息
            # format_html 用于防止XSS攻击，并正确渲染HTML
            return format_html('<span style="color: orange;">⚠️ 未知或无效</span>')
    
    def status_color(self, obj):
        status_str = models.EnrollModel.get_status_str(obj.status)
        colors = {
            "未录取": "red",
            "二面失败": "orange",
            "国庆题未完成": "orange",
            "一面失败": "orange",
            "已报名": "blue",
            "一面已到": "blue",
            "国庆题已完成": "blue",
            "二面已参与": "blue",
            "已录取": "green",
        }
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(status_str, "black"), 
                          status_str)
    status_color.short_description = "状态显示"
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(status=8)  # 已录取
    mark_as_accepted.short_description = "标记为已录取"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status=-4)  # 未录取
    mark_as_rejected.short_description = "标记为未录取"
    
    def mark_as_interview1_passed(self, request, queryset):
        queryset.update(status=5)  # 一面已到
    mark_as_interview1_passed.short_description = "标记为一面已到"
    
    def mark_as_interview2_passed(self, request, queryset):
        queryset.update(status=7)  # 二面已参与
    mark_as_interview2_passed.short_description = "标记为二面已参与"
    
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }


# 将导出CSV的操作标题改为中文
export.export_csv.short_description = "导出为CSV"
admin.site.add_action(export.export_csv)
