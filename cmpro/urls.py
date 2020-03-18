from django.contrib import admin
from django.urls import path
from django.urls import re_path
from django.urls import include
from cmpro import views

urlpatterns = [
    re_path(r'^addstock/(\d+)$', views.add_stock),                  # 增加库存
    re_path(r'^reducestock/(\d+)$', views.reduce_stock),            # 减少库存
    re_path(r'^remove/(\d+)$', views.remove_commodity),             # 删除商品
    path('search/', views.search_commodity),                        # 搜索商品
    path('addcomm/', views.add_commodity),                          # 新增商品
    path('bulkload/', views.bulk_load),                             # 批量新增商品
    path('download/', views.download),                              # 下载批量导入模板
]