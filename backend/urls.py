"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from comment.views import CommentView, CommentReplyView
from enroll.views import EnrollViewSet, send, get_status, query_ddl
from django.conf import settings
from django.conf.urls.static import static

# 导入自定义管理站点配置
import backend.admin

router = DefaultRouter()
router.register('enroll', EnrollViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/comment/', CommentView.as_view()),
    path('api/send_code/', send),
    path('api/get_status/', get_status),
    path('api/query_ddl/', query_ddl),
    path('api/comment/<int:parent_id>/', CommentReplyView.as_view()),
]

# 添加静态文件的URL路由
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
