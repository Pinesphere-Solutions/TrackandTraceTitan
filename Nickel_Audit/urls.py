from django.urls import path
from .views import *

urlpatterns = [
    path('NA_Main/', Nickel_Audit__MainTable.as_view(), name='NA_Main_Table'),
    path('NA_Complete/', Nickel_Audit__CompleteTable.as_view(), name='NA_Complete_Table'),
]