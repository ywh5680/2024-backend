
from django.contrib import admin
from django.utils.html import format_html
from . import models, export

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
    list_display = ("name", "uid", "phone", "email", "major", "qq", "status", "comment", "department_display")
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
    
    actions = ['mark_as_accepted', 'mark_as_rejected', 'mark_as_interview1_passed', 'mark_as_interview2_passed', 'export_csv', 'export_excel']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for i in 'qq', 'content':
            form.base_fields[i].required = False
        return form

    def get_queryset(self, request):
        # 获取当前登录的用户
        user = request.user
        # 如果用户是管理员，则返回所有记录
        if user.is_staff:
            return super().get_queryset(request)
        # 否则，只返回该用户名等于用户名称的记录
        return super().get_queryset(request).filter(department=
                                                    uname2departmentIdx(user.username)
        )

    @admin.display(description="意向部门")
    def department_display(self, obj):
        departments = models.EnrollModel.departments

        if isinstance(obj.department, int) and 0 <= obj.department < len(departments):
            return departments[obj.department]
        else:
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
    status_color.short_description = "报名状态"
    
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

    # 添加导出方法
    export_csv = export.export_csv
    export_excel = export.export_excel
    
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }

# 将导出的操作标题改为中文
export.export_csv.short_description = "导出为CSV"
export.export_excel.short_description = "导出为Excel"
