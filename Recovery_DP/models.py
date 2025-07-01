from django.db import models
from modelmasterapp.models import *

# Create your models here.

class RecoveryMasterCreation(models.Model):
    
    #unique_id = models.CharField(max_length=100, unique=True,null=True, blank=True) #not in use
    batch_id = models.CharField(max_length=50, unique=True)
    lot_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # <== ADD THIS LINE
    model_stock_no = models.ForeignKey(
        ModelMaster, 
        related_name='recovery_master_creations',  # Unique related_name
        on_delete=models.CASCADE
    )    
    polish_finish = models.CharField(max_length=100)
    ep_bath_type = models.CharField(max_length=100)
    plating_color=models.CharField(max_length=100,null=True,blank=True)
    tray_type = models.CharField(max_length=100)
    tray_capacity = models.IntegerField(null=True, blank=True)
    images = models.ManyToManyField(ModelImage, blank=True)  # Store multiple images
    date_time = models.DateTimeField(default=timezone.now)
    version = models.ForeignKey(Version, on_delete=models.CASCADE, help_text="Version")
    total_batch_quantity = models.IntegerField()  
    initial_batch_quantity = models.IntegerField(default=0) #not in use
    current_batch_quantity = models.IntegerField(default=0)  # not in use
    no_of_trays = models.IntegerField(null=True, blank=True)  # Calculated field
    vendor_internal = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    gender = models.CharField(max_length=50)
    sequence_number = models.IntegerField(default=0)  # Add this field
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)  # Allow null values
    recovery_tray_scan = models.BooleanField(default=False, help_text="Tray scan status")
    Moved_to_R_Picker = models.BooleanField(default=False, help_text="Moved to D Picker")
    R_Draft_Saved=models.BooleanField(default=False,help_text="Draft Save")
    rec_pick_remarks=models.CharField(max_length=100,null=True, blank=True)

    def save(self, *args, **kwargs):
        
        if not self.pk:  # Only set the sequence number for new instances
            last_batch = RecoveryMasterCreation.objects.order_by('-sequence_number').first()
            self.sequence_number = 1 if not last_batch else last_batch.sequence_number + 1
        
        # Fetch related data from ModelMaster
        model_data = self.model_stock_no
        self.polish_finish = model_data.polish_finish
        self.ep_bath_type = model_data.ep_bath_type
        self.tray_type = model_data.tray_type
        self.tray_capacity = model_data.tray_capacity
        self.vendor_internal = model_data.vendor_internal
        self.brand = model_data.brand
        self.gender = model_data.gender



        super().save(*args, **kwargs)
        self.images.set(model_data.images.all())


    def __str__(self):
        return f"{self.model_stock_no} - {self.batch_id}"
    

class RecoveryStockModel(models.Model):
    """
    This model is for saving overall stock in Day Planning operation form.
  
    """
    
    model_stock_no = models.ForeignKey(ModelMaster, on_delete=models.CASCADE, help_text="Model Stock Number")
    version = models.ForeignKey(Version, on_delete=models.CASCADE, help_text="Version")
    total_stock = models.IntegerField(help_text="Total stock quantity")
    polish_finish = models.ForeignKey(PolishFinishType, on_delete=models.SET_NULL, null=True, blank=True, help_text="Polish Finish")
        
    plating_color = models.ForeignKey(Plating_Color, on_delete=models.SET_NULL, null=True, blank=True, help_text="Plating Color")
    location = models.ManyToManyField(Location, blank=True, help_text="Multiple Locations")
    lot_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Lot ID")
    batch_id = models.ForeignKey(RecoveryMasterCreation, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=now, help_text="Timestamp of the record")
    # day planning missing qty in day planning pick table
    recovery_missing_qty = models.IntegerField(default=0, help_text="Missing quantity in day planning")
    recovery_onboard_assigned_qty = models.IntegerField(help_text="Original assigned quantity", default=0)  # New field
      
      # New fields for process tracking
    last_process_date_time = models.DateTimeField(null=True, blank=True, help_text="Last Process Date/Time")
    last_process_module = models.CharField(max_length=255, null=True, blank=True, help_text="Last Process Module")
    next_process_module = models.CharField(max_length=255, null=True, blank=True, help_text="Next Process Module")

    #IP Module accept and rejection
    total_Rec_IP_accpeted_quantity = models.IntegerField(default=0, help_text="Total accepted quantity")
    total_qty_after_rejection_IP = models.IntegerField(default=0, help_text="Total rejected quantity")
    
    #Brass QC Module accept and rejection
    brass_qc_accepted_qty = models.IntegerField(default=0, help_text="Brass QC Accepted Quantity")  # New field
    brass_qc_after_rejection_qty = models.IntegerField(default=0, help_text="Brass QC Rejected Quantity")  # New field
    
    #IQF Module accept and rejection
    iqf_accept_qty_after_accept_ftn = models.IntegerField(default=0, help_text="IQF Accepted Quantity")# New field
    iqf_accepted_qty = models.IntegerField(default=0, help_text="IQF Accepted Quantity")  # New field
    iqf_after_rejection_qty = models.IntegerField(default=0, help_text="IQF Rejected Quantity")  # New field
    
    #IP Verification and tray_scan
    tray_scan_status = models.BooleanField(default=False, help_text="Tray scan status")
    recovery_ip_person_qty_verified = models.BooleanField(default=False, help_text="IP Person Quantity Verified")  # New field
    accepted_recovery_Ip_stock = models.BooleanField(default=False, help_text="Accepted IP Stock")  # New field
    few_cases_accepted_Ip_stock = models.BooleanField(default=False, help_text="Few Accepted IP Stock")  # New field
    rejected_ip_stock = models.BooleanField(default=False, help_text="Rejected IP Stock")  # New field
    wiping_status = models.BooleanField(default=False, help_text="Wiping Status")  # New field
   
    rejected_tray_scan_status=models.BooleanField(default=False)
    accepted_tray_scan_status=models.BooleanField(default=False)
    
    #Brass QC Module accept and rejection
    brass_qc_accptance=models.BooleanField(default=False)
    brass_qc_few_cases_accptance=models.BooleanField(default=False)
    brass_qc_rejection=models.BooleanField(default=False)
    brass_rejection_tray_scan_status=models.BooleanField(default=False)
    brass_accepted_tray_scan_status=models.BooleanField(default=False)
    
    #IQF Module accept and rejection
    iqf_acceptance=models.BooleanField(default=False)
    iqf_few_cases_acceptance=models.BooleanField(default=False)
    iqf_rejection=models.BooleanField(default=False)
    iqf_rejection_tray_scan_status=models.BooleanField(default=False)
    iqf_accepted_tray_scan_status=models.BooleanField(default=False)
    
    #Module is IQF - Acceptance - Send to Brass QC 
    send_brass_qc=models.BooleanField(default=False, help_text="Send to Brass QC")
    
    # Override the save method to calculate recovery_onboard_assigned_qty
    
        
    def __str__(self):
        return f"{self.model_stock_no.model_no} - {self.version.version_name} - {self.lot_id}"
    

class RecoveryTrayId(models.Model):
    """
    RecoveryTrayId Model
    Represents a tray identifier in the Titan Track and Traceability system.
   
    """
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True, help_text="Tray ID")
    tray_quantity = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    batch_id = models.ForeignKey(RecoveryMasterCreation, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id} - {self.tray_quantity}"

class Rec_DraftTrayId(models.Model):
    """
    TrayId Model
    Represents a tray identifier in the Titan Track and Traceability system.
   
    """
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True, help_text="Tray ID")
    tray_quantity = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    batch_id = models.ForeignKey(RecoveryMasterCreation, on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
 
 
    def __str__(self):
        return f"{self.tray_id} - {self.tray_quantity}"
    
class Rec_IP_Rejection_Table(models.Model):
    rejection_reason = models.TextField(help_text="Reason for rejection")
    rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def __str__(self):
        return f"{self.rejection_reason} - {self.rejection_count}"
    
class Rec_IP_Rejection_ReasonStore(models.Model):
    rejection_reason = models.ManyToManyField(Rec_IP_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.total_rejection_quantity} - {self.lot_id}"

#give rejected trayscans - fields are lot_id , rejected_tray_quantity , rejected_reson(forign key from RejectionTable), user
class Rec_IP_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    rejection_reason = models.ForeignKey(Rec_IP_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rejection_reason} - {self.rejected_tray_quantity} - {self.lot_id}"

#give accepted tray scan in input screening - fields are lot_id , tray_id , user
class Rec_IP_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"

#give accpeted tray scan - fields are lot_id , accepted_tray_quantity , user    
class Rec_IP_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.accepted_tray_quantity} - {self.lot_id}"

class Rec_Brass_QC_Rejection_Table(models.Model):
    brass_rejection_reason = models.TextField(help_text="Reason for rejection")
    brass_rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def __str__(self):
        return f"{self.brass_rejection_reason} - {self.brass_rejection_count}"

class Rec_Brass_QC_Rejection_ReasonStore(models.Model):
    brass_rejection_reason = models.ManyToManyField(Rec_Brass_QC_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brass_total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    brass_batch_rejection=models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, help_text="Timestamp of the record")
    
    def __str__(self):
        return f"{self.user} - {self.brass_total_rejection_quantity} - {self.lot_id}"

    
class Rec_Brass_QC_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    brass_rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    brass_rejection_reason = models.ForeignKey(Rec_Brass_QC_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    batch_id = models.ForeignKey(RecoveryMasterCreation, on_delete=models.CASCADE,null=True,blank=True)  # ✅ Add this line

    def __str__(self):
        return f"{self.brass_rejection_reason} - {self.brass_rejected_tray_quantity} - {self.lot_id}"

class Rec_Brass_Qc_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    brass_accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.brass_accepted_tray_quantity} - {self.lot_id}"

class Rec_Brass_Qc_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}" 
    
class Rec_IQF_Rejection_Table(models.Model):
    iqf_rejection_reason = models.TextField(help_text="Reason for rejection")
    iqf_rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def __str__(self):
        return f"{self.iqf_rejection_reason} - {self.iqf_rejection_count}"
    
class Rec_IQF_Rejection_ReasonStore(models.Model):
    iqf_rejection_reason = models.ManyToManyField(Rec_IQF_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    iqf_total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    iqf_batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.iqf_total_rejection_quantity} - {self.lot_id}"

class Rec_IQF_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    iqf_rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    iqf_rejection_reason = models.ForeignKey(Rec_IQF_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.iqf_rejection_reason} - {self.iqf_rejected_tray_quantity} - {self.lot_id}" 
    
class Rec_IQF_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    iqf_accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.iqf_accepted_tray_quantity} - {self.lot_id}"
    
class Rec_IQF_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"