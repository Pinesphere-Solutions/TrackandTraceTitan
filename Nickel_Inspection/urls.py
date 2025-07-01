from django.urls import path
from .views import *

urlpatterns = [
    path('Nickel_Inspection/', Nickel_Inspection.as_view(), name='Nickel_Inspection'), 
    path('NI_Completed/', NI_Completed.as_view(), name='NI_Completed'),
    path('NI_Rejected/', NI_Rejected.as_view(), name='NI_Rejected') 
]