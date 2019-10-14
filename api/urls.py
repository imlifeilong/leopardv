"""leopardv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from django.urls import path
from api import views

urlpatterns = [
    # 验证码接口
    path('verify/', views.verify),

    path('username/', views.get_username),
    # 节点
    path('node/', views.NodeList.as_view()),
    path('node/detail/', views.NodeDetail.as_view()),
    # 工程
    path('project/', views.ProjectList.as_view()),
    path('project/upload/', views.project_upload),
    path('project/mapping/', views.project_mapping),
    # 作业
    path('job/', views.JobList.as_view()),
    path('job/mapping/', views.job_mapping),
    path('job/start/', views.job_start),
    path('job/stop/', views.job_stop),
    path('job/view/', views.job_view),
    path('job/status/', views.job_status),

    # 日志
    path('log/', views.log_view),
]
