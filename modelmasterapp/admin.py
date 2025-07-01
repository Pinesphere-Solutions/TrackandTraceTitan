from django.contrib import admin
from .models import *
#test

admin.site.register(PolishFinishType)
admin.site.register(TrayType)
admin.site.register(Vendor)
admin.site.register(ModelMaster)
admin.site.register(ModelMasterCreation)
admin.site.register(Version)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(TrayId)
admin.site.register(DraftTrayId)
admin.site.register(ModelImage)
admin.site.register(Plating_Color)
admin.site.register(TotalStockModel)
admin.site.register(DP_TrayIdRescan)

admin.site.register(IP_RejectionGroup)
admin.site.register(IP_Rejection_Table)
admin.site.register(IP_Rejection_ReasonStore)
admin.site.register(IP_Rejected_TrayScan)

admin.site.register(IP_Accepted_TrayScan)
admin.site.register(IP_Accepted_TrayID_Store)

admin.site.register(Brass_QC_Rejection_Table)
admin.site.register(Brass_QC_Rejection_ReasonStore)
admin.site.register(Brass_QC_Rejected_TrayScan)
admin.site.register(Brass_Qc_Accepted_TrayScan)
admin.site.register(Brass_Qc_Accepted_TrayID_Store)


admin.site.register(IQF_Accepted_TrayScan)
admin.site.register(IQF_Accepted_TrayID_Store)
admin.site.register(IQF_Rejection_ReasonStore)
admin.site.register(IQF_Rejected_TrayScan)
admin.site.register(IQF_Rejection_Table)

admin.site.register(Nickle_IP_Rejection_Table)
admin.site.register(Nickle_IP_Rejection_ReasonStore)
admin.site.register(Nickle_IP_Rejected_TrayScan)
admin.site.register(Nickle_IP_Accepted_TrayScan)
admin.site.register(Nickle_IP_Accepted_TrayID_Store)


#jig loading
admin.site.register(JigLoadingMaster)
admin.site.register(JigDetails)
admin.site.register(BathNumbers)


admin.site.register(JigUnload_TrayId)
admin.site.register(JigUnloadAfterTable)

admin.site.register(TrayAutoSaveData)
