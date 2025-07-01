from django.urls import path
from .views import *

urlpatterns = [
    path('brass_picktable/', BrassPickTableView.as_view(), name='BrassPickTableView'),
    path('brass_completed/', BrassCompletedView.as_view(), name='BrassCompletedView'),
    path('iqf_picktable/', IqfPickTableView.as_view(), name='IqfPickTableView'),
    path('iqf_completed/', IqfCompletedTableView.as_view(), name='IqfCompletedTableView'),
    path('iqp_rejecttable/', IqpRejectTableView.as_view(), name='IqpRejectTableView'),


    path('R_brass_picktable/', R_BrassPickTableView.as_view(), name='R_BrassPickTableView'),
    path('R_brass_completed/', R_BrassCompletedView.as_view(), name='R_BrassCompletedView'),
    path('R_iqf_picktable/', R_IqfPickTableView.as_view(), name='R_IqfPickTableView'),
    path('R_iqf_completed/', R_IqfCompletedTableView.as_view(), name='R_IqfCompletedTableView'),
    path('R_iqp_rejecttable/', R_IqpRejectTableView.as_view(), name='R_IqpRejectTableView'),
]