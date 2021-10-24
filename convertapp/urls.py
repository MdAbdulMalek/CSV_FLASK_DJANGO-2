from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [

    path('', views.home, name="home"),
    path('upload_client', views.upload_client, name="upload_client"),
    path('upload_sanveo', views.upload_sanveo, name="upload_sanveo"),
    path('upload_dict', views.upload_dict, name="upload_dict"),
    path('apply_dict', views.apply_dict, name="apply_dict"),
    path('processs', views.processs, name="processs"),
    path('download', views.download, name="download"),
    path('download_multiple', views.download_multiple, name="download_multiple"),
    path('download_dict', views.download_dict, name="download_dict")
]