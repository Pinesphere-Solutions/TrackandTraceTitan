from django.urls import path
from .views import *

urlpatterns = [
    path('index/',IndexView.as_view(),name="index"),
    path('dp_modelmaster/', DP_ModelmasterView.as_view(), name='dp_modelmaster'),
    path('dp_visualaid/', Visual_AidView.as_view(), name='dp_visualaid'),
    path('view_master/',DP_ViewmasterView.as_view(), name='view_master'),
    
    # Main Model Master Page
    
    # Polish Finish APIs
    path('polish-finish/', PolishFinishAPIView.as_view(), name='polish-finish-api'),
    path('polish-finish/<int:pk>/', PolishFinishAPIView.as_view(), name='polish-finish-detail-api'),
    
    # Plating Color APIs
    path('plating-color/', PlatingColorAPIView.as_view(), name='plating-color-api'),
    path('plating-color/<int:pk>/', PlatingColorAPIView.as_view(), name='plating-color-detail-api'),
    
    # Tray Type APIs
    path('tray-type/', TrayTypeAPIView.as_view(), name='tray-type-api'),
    path('tray-type/<int:pk>/', TrayTypeAPIView.as_view(), name='tray-type-detail-api'),
    
    
    # Model Image APIs
    path('model-image/', ModelImageAPIView.as_view(), name='model-image-api'),
    path('model-image/<int:pk>/', ModelImageAPIView.as_view(), name='model-image-detail-api'),
    
    # Model Master APIs
    path('model-master/', ModelMasterAPIView.as_view(), name='model-master-api'),
    path('model-master/<int:pk>/', ModelMasterAPIView.as_view(), name='model-master-detail-api'),
    
    # Dropdown Data API
    path('dropdown-data/', ModelMasterDropdownDataAPIView.as_view(), name='dropdown-data-api'),
    
    # Location APIs
    path('location/', LocationAPIView.as_view(), name='location-api'),
    path('location/<int:pk>/', LocationAPIView.as_view(), name='location-detail-api'),

    # TrayId APIs
    path('tray-id/', TrayIdAPIView.as_view(), name='tray-id-api'),
    path('tray-id/<int:pk>/', TrayIdAPIView.as_view(), name='tray-id-detail-api'),
 
    # Category APIs
    path('category/', CategoryAPIView.as_view(), name='category-api'),
    path('category/<int:pk>/', CategoryAPIView.as_view(), name='category-detail-api'),

    # IP Rejection APIs
    path('ip-rejection/', IPRejectionAPIView.as_view(), name='ip-rejection-api'),
    path('ip-rejection/<int:pk>/', IPRejectionAPIView.as_view(), name='ip-rejection-detail-api'),

]



