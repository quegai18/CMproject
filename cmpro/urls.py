from django.contrib import admin
from django.urls import path
from django.urls import re_path
from django.urls import include
from cmpro import views

urlpatterns = [
    re_path(r'^addstock/(\d+)$', views.add_stock),
    re_path(r'^reducestock/(\d+)$', views.reduce_stock),
    re_path(r'^remove/(\d+)$', views.remove_commodity),
    path('search/', views.search_commodity),
    path('addcomm/', views.add_commodity),
    path('bulkload/', views.bulk_load),
    path('download/', views.download),
]