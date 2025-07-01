from django.urls import path
from . import views

urlpatterns = [
    path('spider_pick_table/', views.spider_pick_table, name='spider_pick_table'),
]