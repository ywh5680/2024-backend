
def add_logo_to_admin():
    """
    通过自定义CSS和admin.site属性来添加Logo到管理界面
    无需创建模板文件
    """
    from django.contrib import admin
    from django.utils.safestring import mark_safe
    from django.conf import settings
    
    # 构建静态文件URL
    logo_url = f"{settings.STATIC_URL}admin/img/itstudio_logo.svg"
    
    # 设置管理站点标题，在标题前添加图片标签
    admin.site.site_header = mark_safe(f'<img src="{logo_url}" height="30px" style="vertical-align: middle; margin-right: 10px;">爱特工作室管理系统')
    # admin.site.site_title = mark_safe(f'<img src="{logo_url}" height="20px" style="vertical-align: middle; margin-right: 5px;">爱特工作室')
    admin.site.index_title = '管理面板'
    
    # 添加自定义CSS
    class AdminLogoMedia:
        css = {
            'all': ('admin/css/logo.css',)
        }
    
    # 将自定义CSS应用到AdminSite
    admin.site.Media = AdminLogoMedia 