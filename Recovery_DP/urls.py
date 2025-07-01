from django.urls import path
from .views import *

urlpatterns = [
    path('rec_bulk_upload/', REC_DPBulkUploadView.as_view(), name='rec_bulk_upload'),
    path('rec_bulk_upload/preview/', REC_DPBulkUploadPreviewView.as_view(), name='rec_bulk_upload_review'),
    path('rec_dp_pick_table/', REC_PickTableAPIView.as_view(), name='rec_dp_pick_table'),
    path('rec_tray_scan/', Rec_TrayIdScanAPIView.as_view(), name='rec_tray_scan_api'),
    path('rec_tray_id_list/', Rec_TrayIdListAPIView.as_view(), name='rec_tray_id_list'),
    path('rec_tray_id_unique_check/', Rec_TrayIdUniqueCheckAPIView.as_view(), name='rec_tray_id_unique_check'),
    path('rec_draft_tray/', Rec_DraftTrayIdAPIView.as_view(), name='rec_draft_tray'),
    path('draft_tray_id_list/', Rec_DraftTrayIdListAPIView.as_view(), name='draft_tray_id_list'),
    path('rec_delete_batch/', Rec_DeleteBatchAPIView.as_view(), name='rec_delete_batch'),
    path('rec_update_batch_quantity/', Rec_UpdateBatchQuantityAPIView.as_view(), name='rec_update_batch_quantity'),
    path('rec_save_dp_pick_remark/', Rec_SaveDPPickRemarkAPIView.as_view(), name='rec_save_dp_pick_remark'),
    path('rec_completed_table/', Rec_DPCompletedTableView.as_view(), name='rec_completed_table'),  # <-- Add this

]