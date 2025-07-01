from django.urls import path
from .views import *

urlpatterns = [
    path('Jig_Unloading_MainTable/', Jig_Unloading_MainTable.as_view(), name='Jig_Unloading_MainTable'),
    path('JigUnloading_Completedtable/', JigUnloading_Completedtable.as_view(), name='JigUnloading_Completedtable'),
    

    
]