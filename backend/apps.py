from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        """
        在Django应用程序完全加载后调用
        这是应用自定义管理界面设置的正确位置
        """
        # 导入自定义管理站点配置
        from admin_customization import add_logo_to_admin
        
        # 应用自定义设置
        add_logo_to_admin() 