from django.urls import path
from .views import *

urlpatterns = [
    path('', LoginAPIView.as_view(), name='login-api'),
    path('base/', BaseAPIView.as_view(), name='base-api'),
    path('logout/', logout_view, name='logout'),

]