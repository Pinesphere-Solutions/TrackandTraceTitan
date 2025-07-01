from django.urls import path
from .views import *

urlpatterns = [
    path('iqf_picktable/', IQFPickTableView.as_view(), name='iqf_picktable'),
    path('iqf_save_ip_checkbox/', IQFSaveIPCheckboxView.as_view(), name='iqf_save_ip_checkbox'),
    path('iqf_save_ip_pick_remark/', IQFSaveIPPickRemarkAPIView.as_view(), name='iqf_save_ip_pick_remark'),
    path('iqf_update_batch_quantity/', IQFUpdateBatchQuantityAPIView.as_view(), name='iqf_update_batch_quantity'),
    path('iqf_delete_batch/', IQFDeleteBatchAPIView.as_view(), name='iqf_delete_batch'),
    path('iqf_accepted_form/', IQF_Accepted_form.as_view(), name='iqf_accepted_form'),
    path('iqf_batch_rejection/', IQFBatchRejectionAPIView.as_view(), name='iqf_batch_rejection'),
    path('iqf_tray_rejection/', IQFTrayRejectionAPIView.as_view(), name='iqf_tray_rejection'),
    path('iqf_reject_check_tray_id/', iqf_reject_check_tray_id, name='iqf_reject_check_tray_id'),
    path('iqf_get_accepted_tray_scan_data/', iqf_get_accepted_tray_scan_data, name='iqf_get_accepted_tray_scan_data'),
    path('iqf_view_tray_list/', iqf_view_tray_list, name='iqf_view_tray_list'),
    path('iqf_save_accepted_tray_scan/', iqf_save_accepted_tray_scan, name='iqf_save_accepted_tray_scan'),
    path('iqf_check_tray_id/', iqf_check_tray_id, name='iqf_check_tray_id'),
    path('iqf_get_rejected_tray_scan_data/', iqf_get_rejected_tray_scan_data, name='iqf_get_rejected_tray_scan_data'),
    path('iqf_tray_validate/', IQFTrayValidateAPIView.as_view(), name='iqf_tray_validate'),
    path('iqf_completed_table/', IQFCompletedTableView.as_view(), name='iqf_completed_table'),
    path('iqf_rejection_table/', IQFRejectTableView.as_view(), name='iqf_rejection_table'),
    path('iqf_get_rejection_details/',iqf_get_rejection_details,name="iqf_get_rejection_details"),
]