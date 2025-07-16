
from django.urls import reverse
from django.utils.html import format_html

from django.contrib import admin
from . import models


def clamp_len_with(s: str, max_len_without_suffix: int,
                   suffix: str = "...") -> str:
    le = len(s)
    add_suffix = le > max_len_without_suffix
    s = s.replace('\n', ' ')
    if add_suffix:
        res = s[:max_len_without_suffix] + suffix
    else:
        res = s
    return res

@admin.display(description="评论内容")
def clamped_content(obj: models.comment):
    res = clamp_len_with(obj.content, 30)
    return res


@admin.display(description="评论时间")
def comment_time(obj: models.comment):
    res = (obj.datetime
           .strftime('%Y-%m-%d %H:%M')
           )
    return res

@admin.display(description="父评论")
def parent(obj: models.comment):
    parent = obj.parent
    if parent is None:
        return format_html('<span style="color: gray;">无</span>')
    url = reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
                    args=(parent.id,)
    )
    return format_html('<a href="{}" title="查看父评论">#{}</a>', url, parent.id)

@admin.display(description="联系方式")
def contact_info(obj: models.comment):
    if obj.qq and obj.email:
        return format_html('QQ: {} / 邮箱: {}', obj.qq, obj.email)
    elif obj.qq:
        return format_html('QQ: {}', obj.qq)
    elif obj.email:
        return format_html('邮箱: {}', obj.email)
    else:
        return format_html('<span style="color: red;">无联系方式</span>')

@admin.register(models.comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', clamped_content, comment_time, parent, contact_info, 'has_children']
    list_display_links = ['id', clamped_content]
    list_filter = ['datetime']
    search_fields = ['content', 'email', 'qq']
    date_hierarchy = 'datetime'
    readonly_fields = ['datetime']
    
    fieldsets = (
        ('评论内容', {
            'fields': ('content',)
        }),
        ('评论关系', {
            'fields': ('parent',)
        }),
        ('联系方式', {
            'fields': ('qq', 'email')
        }),
        ('时间信息', {
            'fields': ('datetime',),
            'classes': ('collapse',),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for i in 'parent', 'qq', 'email':
            form.base_fields[i].required = False
        return form
    
    def has_children(self, obj):
        children_count = models.comment.objects.filter(parent=obj).count()
        if children_count > 0:
            return format_html('<span style="color: green;">有 ({}) 条回复</span>', children_count)
        return format_html('<span style="color: gray;">无回复</span>')
    has_children.short_description = '回复数'
    
    actions = ['delete_with_children']
    
    def delete_with_children(self, request, queryset):
        for obj in queryset:
            # 删除所有子评论
            models.comment.objects.filter(parent=obj).delete()
        # 删除选中的评论
        queryset.delete()
    delete_with_children.short_description = '删除评论及其所有回复'

