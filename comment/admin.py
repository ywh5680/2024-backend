
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

@admin.display(description="Content")
def clamped_content(obj: models.comment):
    res = clamp_len_with(obj.content, 10)
    return res


@admin.display(description="Time")
def comment_time(obj: models.comment):
    res = (obj.datetime
           .strftime('%m-%d %H:%M %z')  # MM-DD hh:mm[ [+-]HHSS[.ffffff]]
           )
    return res

@admin.display(description="parent")
def parent(obj: models.comment):
    parent = obj.parent
    if parent is None:
        return None
    url = reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
                    args=(parent.id,)
    )
    return format_html("<a href={}>{}</a>", url, parent.id)

@admin.register(models.comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', clamped_content, comment_time, parent]
    list_display_links = [clamped_content]
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for i in 'parent', 'qq', 'email':
            form.base_fields[i].required = False
        return form

