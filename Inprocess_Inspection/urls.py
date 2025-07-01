from django.urls import path
from . import views

urlpatterns = [
    path('', views.InprocessInspectionView.as_view(), name='inprocess_inspection_main'),
    path('complete/', views.InprocessInspectionCompleteView.as_view(), name='inprocess_inspection_complete'),

    
]