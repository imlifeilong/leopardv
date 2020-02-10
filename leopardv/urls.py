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
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from anything import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),
    path('', TemplateView.as_view(template_name="index.html")),
    path('node/', TemplateView.as_view(template_name="node.html")),
    path('node/<str:nid>', views.node_detail),
    path('project/', TemplateView.as_view(template_name="project.html")),
    path('job/', TemplateView.as_view(template_name="job.html")),
    path('log/', TemplateView.as_view(template_name="log.html")),

    path('api/', include('api.urls')),

]
