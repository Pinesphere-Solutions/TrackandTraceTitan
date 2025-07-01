from django.urls import path, include
from .views import (
    RecoveryView,
    Recovery_BulkUpload,
    Recovery_DPPickTableView,
    Recovery_DPCompletedTableView,
)

urlpatterns = [
    path('', RecoveryView.as_view(), name='recovery_home'),
    path('completed-table/', Recovery_DPCompletedTableView.as_view(), name='recovery_dp_completed_table'),
    path('BulkUpload/', Recovery_BulkUpload.as_view(), name="recovery_BulkUpload"),
    path('pick-table/', Recovery_DPPickTableView.as_view(), name='recovery_dp_pick_table'),
    
]