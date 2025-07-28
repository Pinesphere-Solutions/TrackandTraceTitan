from django.urls import path

from DayPlanning import views
from .views import *

urlpatterns = [
    path('brass_picktable/', BrassPickTableView.as_view(), name='BrassPickTableView'),
    path('brass_completed/', BrassCompletedView.as_view(), name='BrassCompletedView'),
    path('brass_save_hold_unhold_reason/', BrassSaveHoldUnholdReasonAPIView.as_view(), name='brass_save_hold_unhold_reason'),

    path('brass_save_ip_checkbox/', BrassSaveIPCheckboxView.as_view(), name='brass_save_ip_checkbox'),
    path('brass_save_ip_pick_remark/', BrassSaveIPPickRemarkAPIView.as_view(), name='brass_save_ip_pick_remark'),
    path('brass_delete_batch/', BQDeleteBatchAPIView.as_view(), name='brass_delete_batch'),
    path('brass_accepted_form/', BQ_Accepted_form.as_view(), name='brass_accepted_form'),
    
    path('brass_batch_rejection/', BQBatchRejectionAPIView.as_view(), name='brass_batch_rejection'),
    path('brass_tray_rejection/', BQTrayRejectionAPIView.as_view(), name='brass_tray_rejection'),
    path('brass_reject_check_tray_id/', brass_reject_check_tray_id, name='brass_reject_check_tray_id'),
    path('brass_get_accepted_tray_scan_data/', brass_get_accepted_tray_scan_data, name='brass_get_accepted_tray_scan_data'),
    path('brass_view_tray_list/', brass_view_tray_list, name='brass_view_tray_list'),
    path('brass_save_accepted_tray_scan/', brass_save_accepted_tray_scan, name='brass_save_accepted_tray_scan'),
    path('brass_check_tray_id/', brass_check_tray_id, name='brass_check_tray_id'),
    path('brass_get_rejected_tray_scan_data/', brass_get_rejected_tray_scan_data, name='brass_get_rejected_tray_scan_data'),
    path('brass_tray_validate/', BrassTrayValidateAPIView.as_view(), name='brass_tray_validate'),
    path('brass_save_single_top_tray_scan/', brass_save_single_top_tray_scan, name='brass_save_single_top_tray_scan'),
    path('brass_reject_check_tray_id_simple/', brass_reject_check_tray_id_simple, name='brass_reject_check_tray_id_simple'),
    
    path('brass_get_delink_tray_data/', brass_get_delink_tray_data, name='brass_get_delink_tray_data'),
    path('brass_delink_check_tray_id/', brass_delink_check_tray_id, name='brass_delink_check_tray_id'),
    
    path('brass_CompleteTable_tray_id_list/', BrassTrayIdList_Complete_APIView.as_view(), name='brass_CompleteTable_tray_id_list'),
    path('brass_complete_tray_validate/', BrassTrayValidate_Complete_APIView.as_view(), name='brass_complete_tray_validate'),

    # Draft functionality endpoints
    path('brass_batch_rejection_draft/', BrassBatchRejectionDraftAPIView.as_view(), name='brass_batch_rejection_draft'),
    path('brass_tray_rejection_draft/', BrassTrayRejectionDraftAPIView.as_view(), name='brass_tray_rejection_draft'),
    path('brass_get_draft_data/', brass_get_draft_data, name='brass_get_draft_data'),
    path('brass_clear_draft/', BrassClearDraftAPIView.as_view(), name='brass_clear_draft'),
    path('brass_get_all_drafts/', brass_get_all_drafts, name='brass_get_all_drafts'),

    # ✅ NEW: Top Tray Scan Draft endpoints
    path('brass_top_tray_scan_draft/', BrassTopTrayScanDraftAPIView.as_view(), name='brass_top_tray_scan_draft'),
    path('brass_get_top_tray_draft/', brass_get_top_tray_draft, name='brass_get_top_tray_draft'),
    path('brass_clear_top_tray_draft/', BrassClearTopTrayDraftAPIView.as_view(), name='brass_clear_top_tray_draft'),
    
]