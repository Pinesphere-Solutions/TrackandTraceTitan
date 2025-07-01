from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(RecoveryMasterCreation)
admin.site.register(RecoveryStockModel)
admin.site.register(RecoveryTrayId)

admin.site.register(Rec_IP_Rejection_Table)
admin.site.register(Rec_IP_Rejected_TrayScan)
admin.site.register(Rec_IP_Accepted_TrayID_Store)
admin.site.register(Rec_IP_Rejection_ReasonStore)

admin.site.register(Rec_Brass_QC_Rejection_Table)
admin.site.register(Rec_Brass_QC_Rejected_TrayScan)
admin.site.register(Rec_Brass_Qc_Accepted_TrayID_Store)
admin.site.register(Rec_Brass_QC_Rejection_ReasonStore)

admin.site.register(Rec_IQF_Rejection_Table)
admin.site.register(Rec_IQF_Rejection_ReasonStore) 
admin.site.register(Rec_IQF_Rejected_TrayScan)
admin.site.register(Rec_IQF_Accepted_TrayScan)