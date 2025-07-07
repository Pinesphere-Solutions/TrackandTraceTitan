from django.db import models
from django.utils import timezone
from django.db.models import F
from django.core.exceptions import ValidationError
import datetime
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.
class ModelImage(models.Model):
  #give master_image field for mulitple image slection
    master_image = models.ImageField(upload_to='model_images/')
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Master_Image {self.id}"
    
class PolishFinishType(models.Model):
    polish_finish = models.CharField(max_length=255, unique=True, help_text="Type of polish finish")
    polish_internal = models.CharField(
        max_length=255,
        unique=True,
        default="DefaultInternal",
        help_text="Internal name of the Polish Finish"
    )
    date_time = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.polish_finish 
    
class Plating_Color(models.Model):
    #need choices for plating color field -dropdown field
    plating_color = models.CharField(max_length=255, unique=True, help_text="Plating color")
    plating_color_internal = models.CharField(
        max_length=10,
        default="B",  
        help_text="Short internal code used in stock number (e.g., B for Black)", 
    )
    jig_unload_zone_1 = models.BooleanField(default=False, help_text="Indicates if Jig Unload Zone 1 is active")
    jig_unload_zone_2 = models.BooleanField(default=False, help_text="Indicates if Jig Unload Zone 2 is active")
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.plating_color
    
        
class Version(models.Model):
    version_name = models.CharField(max_length=255, unique=True, help_text="Version name")
    version_internal = models.CharField(max_length=255, unique=True,null=True,blank=True, help_text="Version Internal")
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.version_name
    
class TrayType(models.Model):
    tray_type = models.CharField(max_length=255, unique=True, help_text="Type of tray")
    tray_capacity = models.IntegerField(help_text="Number of watches the tray can hold")  
    tray_color = models.CharField(max_length=255, help_text="Color of the tray",blank=True, null=True)  
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.tray_type
    
class Vendor(models.Model):
    vendor_name = models.CharField(max_length=255, unique=True, help_text="Name of the vendor")
    vendor_internal = models.CharField(max_length=255, unique=True, help_text="Internal name of the vendor")
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.vendor_name

class Location(models.Model):
    location_name = models.CharField(max_length=255, unique=True, help_text="Name of the location")
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.location_name
    
class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True, help_text="Name of the location")
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.category_name
    
    
class ModelMaster(models.Model):
    # Assuming this model holds the reference data for dropdowns and auto-fetch fields
    model_no = models.CharField(max_length=100, unique=True)
    polish_finish = models.ForeignKey(PolishFinishType, on_delete=models.SET_NULL, null=True, blank=True)
    ep_bath_type = models.CharField(max_length=100)
    tray_type = models.ForeignKey(TrayType, on_delete=models.SET_NULL, null=True, blank=True)
    tray_capacity = models.IntegerField(null=True, blank=True)
    images = models.ManyToManyField(ModelImage, blank=True)  # Allows multiple images
    vendor_internal = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=100,null=True, blank=True)
    gender = models.CharField(max_length=50,null=True, blank=True)
    wiping_required = models.BooleanField(default=False)
    date_time = models.DateTimeField(default=timezone.now)
 
    def __str__(self):
        return self.model_no
    
class ModelMasterCreation(models.Model):
    
    #unique_id = models.CharField(max_length=100, unique=True,null=True, blank=True) #not in use
    batch_id = models.CharField(max_length=50, unique=True)
    lot_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # <== ADD THIS LINE
    model_stock_no = models.ForeignKey(ModelMaster, related_name='model_stock_no', on_delete=models.CASCADE)
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
    vendor_internal = models.CharField(max_length=100,null=True, blank=True)
    sequence_number = models.IntegerField(default=0)  # Add this field
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)  # Allow null values
    Moved_to_D_Picker = models.BooleanField(default=False, help_text="Moved to D Picker")
    top_tray_qty_verified = models.BooleanField(default=False, help_text="On Hold Picking")
    verified_tray_qty=models.IntegerField(default=0, help_text="Verified Tray Quantity")
    top_tray_qty_modify=models.IntegerField(default=0, help_text="Top Tray Quantity Modified")
    Draft_Saved=models.BooleanField(default=False,help_text="Draft Save")
    dp_pick_remarks=models.CharField(max_length=100,null=True, blank=True)
    category=models.CharField(max_length=100, null=True, blank=True, help_text="Category of the model")
    plating_stk_no=models.CharField(max_length=100, null=True, blank=True, help_text="Plating Stock Number")
    polishing_stk_no=models.CharField(max_length=100,null=True, blank=True)
    holding_reason = models.CharField(max_length=255, null=True, blank=True, help_text="Reason for holding the batch")  
    release_reason= models.CharField(max_length=255, null=True, blank=True, help_text="Reason for releasing the batch")
    hold_lot = models.BooleanField(default=False, help_text="Indicates if the lot is on hold")
    release_lot =models.BooleanField(default=False)
    previous_lot_status = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
    
        if not self.pk:  # Only set the sequence number for new instances
            last_batch = ModelMasterCreation.objects.order_by('-sequence_number').first()
            self.sequence_number = 1 if not last_batch else last_batch.sequence_number + 1
        
        # Fetch related data from ModelMaster
        model_data = self.model_stock_no
        
        
        self.ep_bath_type = model_data.ep_bath_type
        
        # FIXED: Convert tray_type ForeignKey to string
        if model_data.tray_type:
            self.tray_type = model_data.tray_type.tray_type  # Use the actual field value
        else:
            self.tray_type = ""
        
        self.tray_capacity = model_data.tray_capacity

        super().save(*args, **kwargs)
        self.images.set(model_data.images.all())


    def __str__(self):
        return f"{self.model_stock_no} - {self.batch_id}"

        
class TrayId(models.Model):
    """
    TrayId Model
    Represents a tray identifier in the Titan Track and Traceability system.
    """
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True, help_text="Tray ID")
    tray_quantity = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    batch_id = models.ForeignKey(ModelMasterCreation, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    top_tray = models.BooleanField(default=False)
    ip_top_tray = models.BooleanField(default=False)
    ip_top_tray_qty= models.IntegerField(default=0, help_text="IP Top Tray Quantity")

    delink_tray = models.BooleanField(default=False, help_text="Is tray delinked")
    delink_tray_qty = models.CharField(max_length=50, null=True, blank=True, help_text="Delinked quantity")
    
    IP_tray_verified= models.BooleanField(default=False, help_text="Is tray verified in IP")
    
    rejected_tray= models.BooleanField(default=False, help_text="Is tray rejected")
    new_tray=models.BooleanField(default=True, help_text="Is tray new")
    
    # Tray configuration fields (filled by admin)
    tray_type = models.CharField(max_length=50, null=True, blank=True, help_text="Type of tray (Jumbo, Normal, etc.) - filled by admin")
    tray_capacity = models.IntegerField(null=True, blank=True, help_text="Capacity of this specific tray - filled by admin")
    
    # NEW FIELD: Scanned status tracking
    scanned = models.BooleanField(default=False, help_text="Indicates if the tray has been scanned/used")

    def __str__(self):
        return f"{self.tray_id} - {self.lot_id} - {self.tray_quantity}"

    @property
    def is_available_for_scanning(self):
        """
        Check if tray is available for scanning
        Available if: not scanned OR delinked (can be reused)
        """
        return not self.scanned or self.delink_tray

    @property
    def status_display(self):
        """Get human-readable status"""
        if self.delink_tray:
            return "Delinked (Reusable)"
        elif self.scanned:
            return "Already Scanned"
        elif self.batch_id:
            return "In Use"
        else:
            return "Available"

    class Meta:
        verbose_name = "Tray ID"
        verbose_name_plural = "Tray IDs"



class IP_TrayVerificationStatus(models.Model):
    lot_id = models.CharField(max_length=100)
    tray_position = models.IntegerField()  # 1, 2, 3, etc.
    tray_id = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=10, choices=[('pass', 'Pass'), ('fail', 'Fail')], null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['lot_id', 'tray_position']
        
    def __str__(self):
        return f"Lot {self.lot_id} - Position {self.tray_position} - {self.verification_status}"        
        
class DraftTrayId(models.Model):
    """
    TrayId Model
    Represents a tray identifier in the Titan Track and Traceability system.
    """
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, blank=True, help_text="Tray ID")
    tray_quantity = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    batch_id = models.ForeignKey(ModelMasterCreation, on_delete=models.CASCADE, blank=True, null=True)
    position = models.IntegerField(
        help_text="Position/slot number in the tray scan grid",
        null=True,
        blank=True,
        default=None
    )    
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # ✅ NEW: Add delink fields
    delink_tray = models.BooleanField(default=False, help_text="Is tray delinked")
    delink_tray_qty = models.CharField(max_length=50, null=True, blank=True, help_text="Delinked quantity")
    
    class Meta:
        unique_together = ('batch_id', 'position')
        constraints = [
            models.UniqueConstraint(
                fields=['batch_id', 'tray_id'],
                condition=models.Q(tray_id__gt=''),
                name='unique_non_empty_tray_id_per_batch'
            )
        ]
    
    def __str__(self):
        return f"{self.tray_id or 'Empty'} - Position {self.position} - {self.tray_quantity}"  


class TotalStockModel(models.Model):
    """
    This model is for saving overall stock in Day Planning operation form.
  
    """
    batch_id = models.ForeignKey(ModelMasterCreation, on_delete=models.CASCADE, null=True, blank=True)

    model_stock_no = models.ForeignKey(ModelMaster, on_delete=models.CASCADE, help_text="Model Stock Number")
    version = models.ForeignKey(Version, on_delete=models.CASCADE, help_text="Version")
    total_stock = models.IntegerField(help_text="Total stock quantity")
    polish_finish = models.ForeignKey(PolishFinishType, on_delete=models.SET_NULL, null=True, blank=True, help_text="Polish Finish")

    plating_color = models.ForeignKey(Plating_Color, on_delete=models.SET_NULL, null=True, blank=True, help_text="Plating Color")
    location = models.ManyToManyField(Location, blank=True, help_text="Multiple Locations")
    lot_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Lot ID")
    created_at = models.DateTimeField(default=now, help_text="Timestamp of the record")
    brass_saved_time = models.DateTimeField(default=now)
    # day planning missing qty in day planning pick table
    dp_missing_qty = models.IntegerField(default=0, help_text="Missing quantity in day planning")
    dp_physical_qty = models.IntegerField(help_text="Original physical quantity", default=0)  # New field
    dp_physical_qty_edited = models.BooleanField(default=False, help_text="Qunatity Edited in IP")

    brass_missing_qty= models.IntegerField(default=0, help_text="Missing quantity in Brass QC")
    brass_physical_qty= models.IntegerField(help_text="Original physical quantity in Brass QC", default=0)  # New field
    brass_physical_qty_edited = models.BooleanField(default=False, help_text="Qunatity Edited in Brass")

    iqf_missing_qty = models.IntegerField(default=0, help_text="Missing quantity in IQF")
    iqf_physical_qty = models.IntegerField(help_text="Original physical quantity in IQF", default=0)  # New field
    iqf_physical_qty_edited= models.BooleanField(default=False, help_text="Qunatity Edited in IQF")
    
    jig_physical_qty = models.IntegerField(help_text="Original physical quantity in JIG", default=0)  # New field
    jig_physical_qty_edited = models.BooleanField(default=False, help_text="Qunatity Edited in JIG")    
    
    # New fields for process tracking
    last_process_date_time = models.DateTimeField(null=True, blank=True, help_text="Last Process Date/Time")
    last_process_module = models.CharField(max_length=255, null=True, blank=True, help_text="Last Process Module")
    next_process_module = models.CharField(max_length=255, null=True, blank=True, help_text="Next Process Module")

    #IP Module accept and rejection
    total_IP_accpeted_quantity = models.IntegerField(default=0, help_text="Total accepted quantity")
    total_qty_after_rejection_IP = models.IntegerField(default=0, help_text="Total rejected quantity")
    
    #Brass QC Module accept and rejection
    brass_qc_accepted_qty = models.IntegerField(default=0, help_text="Brass QC Accepted Quantity")  # New field
    brass_qc_after_rejection_qty = models.IntegerField(default=0, help_text="Brass QC Rejected Quantity")  # New field
    
    #IQF Module accept and rejection
    iqf_accept_qty_after_accept_ftn = models.IntegerField(default=0, help_text="IQF Accepted Quantity")  # New field
    iqf_accepted_qty = models.IntegerField(default=0, help_text="IQF Accepted Quantity")  # New field
    iqf_after_rejection_qty = models.IntegerField(default=0, help_text="IQF Rejected Quantity")  # New field
    
    #IP Verification and tray_scan
    tray_scan_status = models.BooleanField(default=False, help_text="Tray scan status")
    ip_person_qty_verified = models.BooleanField(default=False, help_text="IP Person Quantity Verified")  # New field
    accepted_Ip_stock = models.BooleanField(default=False, help_text="Accepted IP Stock")  # New fiel
    few_cases_accepted_Ip_stock = models.BooleanField(default=False, help_text="Few Accepted IP Stock")  # New field
    rejected_ip_stock = models.BooleanField(default=False, help_text="Rejected IP Stock")  # New field
    wiping_status = models.BooleanField(default=False, help_text="Wiping Status")  # New field
    IP_pick_remarks=models.CharField(max_length=100, null=True, blank=True, help_text="IP Pick Remarks")
    Bq_pick_remarks= models.CharField(max_length=100, null=True, blank=True, help_text="BQ Pick Remarks")  # New field
    IQF_pick_remarks= models.CharField(max_length=100, null=True, blank=True, help_text="IQF Pick Remarks")  # New field
    jig_pick_remarks= models.CharField(max_length=100, null=True, blank=True, help_text="JIG Pick Remarks")  # New field
    brass_qc_accepted_qty_verified= models.BooleanField(default=False, help_text="Brass QC Accepted Quantity Verified")  # New field
    
    rejected_tray_scan_status=models.BooleanField(default=False)
    accepted_tray_scan_status=models.BooleanField(default=False)
    ip_onhold_picking =models.BooleanField(default=False)
    
    #Brass QC Module accept and rejection
    brass_qc_accptance=models.BooleanField(default=False)
    brass_qc_few_cases_accptance=models.BooleanField(default=False)
    brass_qc_rejection=models.BooleanField(default=False)
    brass_rejection_tray_scan_status=models.BooleanField(default=False)
    brass_accepted_tray_scan_status=models.BooleanField(default=False)
    brass_onhold_picking=models.BooleanField(default=False, help_text="Brass QC On Hold Picking")
    
    #IQF Module accept and rejection
    iqf_accepted_qty_verified=models.BooleanField(default=False, help_text="IQF Accepted Quantity Verified")  # New field
    iqf_acceptance=models.BooleanField(default=False)
    iqf_few_cases_acceptance=models.BooleanField(default=False)
    iqf_rejection=models.BooleanField(default=False)
    iqf_rejection_tray_scan_status=models.BooleanField(default=False)
    iqf_accepted_tray_scan_status=models.BooleanField(default=False)
    iqf_onhold_picking=models.BooleanField(default=False, help_text="IQF On Hold Picking")
    
    #Module is IQF - Acceptance - Send to Brass QC 
    send_brass_qc=models.BooleanField(default=False, help_text="Send to Brass QC")
    
    # New fields for Jig status
    jig_full_cases = models.BooleanField(default=False, help_text="Indicates if jig is loaded with full cases")
    jig_full_cases_qty=models.IntegerField(default=0, help_text="JIG Full Quantity")
    jig_remining_cases = models.BooleanField(default=False, help_text="Indicates if jig has remaining cases")
    jig_remaining_cases_qty=models.IntegerField(default=0, help_text="JIG Remaining Quantity")
   
        
    ip_holding_reason = models.CharField(max_length=255, null=True, blank=True, help_text="IP Reason for holding the batch")  
    ip_release_reason= models.CharField(max_length=255, null=True, blank=True, help_text="IP Reason for releasing the batch")
    ip_hold_lot = models.BooleanField(default=False, help_text="Indicates if the lot is on hold n IP")
    ip_release_lot =models.BooleanField(default=False)
    
    ip_top_tray_qty_verified = models.BooleanField(default=False, help_text="IP-On Hold Picking")
    ip_verified_tray_qty=models.IntegerField(default=0, help_text="IP-Verified Tray Quantity")
    ip_top_tray_qty_modify=models.IntegerField(default=0, help_text="IP-Top Tray Quantity Modified")
    
    def __str__(self):
        return f"{self.model_stock_no.model_no} - {self.version.version_name} - {self.lot_id}"

    def delete(self, *args, **kwargs):
        if self.lot_id:
            # Delete related records with the same lot_id
            TrayId.objects.filter(lot_id=self.lot_id).delete()
            DraftTrayId.objects.filter(lot_id=self.lot_id).delete()
            DP_TrayIdRescan.objects.filter(lot_id=self.lot_id).delete()
            IP_Rejection_ReasonStore.objects.filter(lot_id=self.lot_id).delete()
            Brass_QC_Rejection_ReasonStore.objects.filter(lot_id=self.lot_id).delete()
            IQF_Rejection_ReasonStore.objects.filter(lot_id=self.lot_id).delete()
            IP_Rejected_TrayScan.objects.filter(lot_id=self.lot_id).delete()
            Brass_QC_Rejected_TrayScan.objects.filter(lot_id=self.lot_id).delete()
            IQF_Rejected_TrayScan.objects.filter(lot_id=self.lot_id).delete()
            IP_Accepted_TrayScan.objects.filter(lot_id=self.lot_id).delete()
            Brass_Qc_Accepted_TrayScan.objects.filter(lot_id=self.lot_id).delete()
            IQF_Accepted_TrayScan.objects.filter(lot_id=self.lot_id).delete()
            IP_Accepted_TrayID_Store.objects.filter(lot_id=self.lot_id).delete()
            Brass_Qc_Accepted_TrayID_Store.objects.filter(lot_id=self.lot_id).delete()
            IQF_Accepted_TrayID_Store.objects.filter(lot_id=self.lot_id).delete()
            JigDetails.objects.filter(lot_id=self.lot_id).delete()
        
        super().delete(*args, **kwargs)



class DP_TrayIdRescan(models.Model):
    """
    Stores tray ID rescans during the day planning process.
    """
    tray_id = models.CharField(max_length=100, unique=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_count = models.PositiveIntegerField(default=1)  # Count how many times scanned

    class Meta:
        unique_together = ('tray_id', 'lot_id')  # Ensure each tray_id and lot_id combination is unique

    def __str__(self):
        return f"{self.tray_id} - {self.lot_id} (Scanned: {self.scan_count})"

class IP_RejectionGroup(models.Model):
    group_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.group_name

class IP_Rejection_Table(models.Model):
    rejection_reason_id = models.CharField(max_length=10, null=True, blank=True, editable=False)
    rejection_reason = models.TextField(help_text="Reason for rejection")
    rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def save(self, *args, **kwargs):
        if not self.rejection_reason_id:
            last = IP_Rejection_Table.objects.order_by('-rejection_reason_id').first()
            if last and last.rejection_reason_id.startswith('R'):
                last_num = int(last.rejection_reason_id[1:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.rejection_reason_id = f"R{new_num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rejection_reason} - {self.rejection_count}"
   
# Add this to your models.py

class IP_Rejection_Draft(models.Model):
    """
    Model to store draft rejection data that can be edited later
    """
    lot_id = models.CharField(max_length=50, unique=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    draft_data = models.JSONField(help_text="JSON data containing rejection details")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['lot_id', 'user']
    
    def __str__(self):
        return f"Draft: {self.lot_id} - {self.user.username}"
     
class Brass_QC_Rejection_Table(models.Model):
    group = models.ForeignKey(IP_RejectionGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='brass_qc_rejection_reasons')
    rejection_reason_id = models.CharField(max_length=10, null=True, blank=True, editable=False)
    rejection_reason = models.TextField(help_text="Reason for rejection")
    rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def save(self, *args, **kwargs):
        if not self.rejection_reason_id:
            last = Brass_QC_Rejection_Table.objects.order_by('-rejection_reason_id').first()
            if last and last.rejection_reason_id.startswith('R'):
                last_num = int(last.rejection_reason_id[1:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.rejection_reason_id = f"R{new_num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rejection_reason} - {self.rejection_count}"
 
class IQF_Rejection_Table(models.Model):
    group = models.ForeignKey(IP_RejectionGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='iqf_rejection_reasons')
    rejection_reason_id = models.CharField(max_length=10, null=True, blank=True, editable=False)
    rejection_reason = models.TextField(help_text="Reason for rejection")
    rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def save(self, *args, **kwargs):
        if not self.rejection_reason_id:
            last = IQF_Rejection_Table.objects.order_by('-rejection_reason_id').first()
            if last and last.rejection_reason_id.startswith('R'):
                last_num = int(last.rejection_reason_id[1:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.rejection_reason_id = f"R{new_num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rejection_reason} - {self.rejection_count}"
    
#rejection reasons stored tabel , fields ared rejection resoon multiple slection from RejectionTable an dlot_id , user, Total_rejection_qunatity
class IP_Rejection_ReasonStore(models.Model):
    rejection_reason = models.ManyToManyField(IP_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.total_rejection_quantity} - {self.lot_id}"
    
    
    
class Brass_QC_Rejection_ReasonStore(models.Model):
    rejection_reason = models.ManyToManyField(Brass_QC_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    batch_rejection=models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, help_text="Timestamp of the record")
    
    def __str__(self):
        return f"{self.user} - {self.total_rejection_quantity} - {self.lot_id}"

class IQF_Rejection_ReasonStore(models.Model):
    rejection_reason = models.ManyToManyField(IQF_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.total_rejection_quantity} - {self.lot_id}"
    
#give rejected trayscans - fields are lot_id , rejected_tray_quantity , rejected_reson(forign key from RejectionTable), user
class IP_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    rejected_tray_id= models.CharField(max_length=100, null=True, blank=True, help_text="Rejected Tray ID")
    rejection_reason = models.ForeignKey(IP_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rejection_reason} - {self.rejected_tray_quantity} - {self.lot_id}"

class Brass_QC_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    rejected_tray_id= models.CharField(max_length=100, null=True, blank=True, help_text="Rejected Tray ID")
    rejection_reason = models.ForeignKey(Brass_QC_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rejection_reason} - {self.rejected_tray_quantity} - {self.lot_id}"
    
class IQF_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    rejected_tray_id= models.CharField(max_length=100, null=True, blank=True, help_text="Rejected Tray ID")
    rejection_reason = models.ForeignKey(IQF_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rejection_reason} - {self.rejected_tray_quantity} - {self.lot_id}"
    
#give accpeted tray scan - fields are lot_id , accepted_tray_quantity , user    
class IP_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.accepted_tray_quantity} - {self.lot_id}"

class Brass_Qc_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.accepted_tray_quantity} - {self.lot_id}"
    
class IQF_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.accepted_tray_quantity} - {self.lot_id}"
    
class IP_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    top_tray_id = models.CharField(max_length=100, unique=True)  # renamed from tray_id
    top_tray_qty = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")  # renamed from tray_qty
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=False, help_text="Draft Save")
    is_save = models.BooleanField(default=False, help_text="Save")
    # NEW FIELDS
    delink_tray_id = models.CharField(max_length=100, null=True, blank=True, help_text="Delink Tray ID")
    delink_tray_qty = models.IntegerField(null=True, blank=True, help_text="Delink Tray Quantity")

    def __str__(self):
        return f"{self.top_tray_id} - {self.lot_id}"
    
class Brass_Qc_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    tray_qty = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=False, help_text="Draft Save")
    is_save= models.BooleanField(default=False, help_text="Save")
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"

class IQF_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    tray_qty = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=False, help_text="Draft Save")
    is_save= models.BooleanField(default=False, help_text="Save")
    
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"
    

#jig Loading master
class JigLoadingMaster(models.Model):
    model_stock_no = models.ForeignKey(ModelMaster, on_delete=models.CASCADE, help_text="Model Stock Number")
    jig_type=models.CharField(max_length=100, help_text="Jig Type")
    jig_capacity=models.IntegerField(help_text="Jig Capacity")
    forging_info=models.CharField(max_length=100, help_text="Forging Info")
    
    def __str__(self):
        return f"{self.model_stock_no} - {self.jig_type} - {self.jig_capacity}"

class BathNumbers(models.Model):
    bath_number=models.CharField(max_length=100)

class JigDetails(models.Model):
    JIG_POSITION_CHOICES = [
        ('Top', 'Top'),
        ('Middle', 'Middle'),
        ('Bottom', 'Bottom'),
    ]
    jig_qr_id = models.CharField(max_length=100)
    faulty_slots = models.IntegerField(default=0)
    jig_type = models.CharField(max_length=50)  # New field
    jig_capacity = models.IntegerField()        # New field
    bath_tub = models.CharField(max_length=100, help_text="Bath Tub",blank=True, null=True)
    plating_color = models.CharField(max_length=50)
    empty_slots = models.IntegerField(default=0)
    ep_bath_type = models.CharField(max_length=50)
    total_cases_loaded = models.IntegerField()
        #JIG Loading Module - Remaining cases
    jig_cases_remaining_count=models.IntegerField(default=0,blank=True,null=True)

    forging = models.CharField(max_length=100)
    no_of_model_cases = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    no_of_cycle=models.IntegerField(default=1)
    lot_id = models.CharField(max_length=100)
    new_lot_ids = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    electroplating_only = models.BooleanField(default=False)
    lot_id_quantities = JSONField(blank=True, null=True)
    draft_save = models.BooleanField(default=False, help_text="Draft Save")
    delink_tray_data = models.JSONField(default=list, blank=True, null=True)  # Add this field
    date_time = models.DateTimeField(default=timezone.now)
    bath_numbers = models.ForeignKey(
            BathNumbers,
            on_delete=models.SET_NULL,  
            null=True,                  
            blank=True,
            help_text="Related Bath Numbers"
        )   
    
    jig_position = models.CharField(
        max_length=10,
        choices=JIG_POSITION_CHOICES,
        default='Top',
        help_text="Jig position: Top, Middle, or Bottom"
    )
    remarks = models.CharField(
        max_length=50,
        blank=True,
        help_text="Remarks (max 50 words)"
    )
    pick_remarks=models.CharField(
        max_length=50,
        blank=True,
        help_text="Remarks (max 50 words)"
    )
     
    jig_unload_draft = models.BooleanField(default=False)
    combined_lot_ids = ArrayField(models.CharField(max_length=50), blank=True, default=list)  # Correct ArrayField
    
    def __str__(self):
        return f"{self.jig_qr_id} - {self.lot_id} - {self.no_of_cycle}"
    

class JigUnload_TrayId(models.Model):
    tray_id = models.CharField(max_length=100, help_text="Tray ID")
    tray_qty = models.IntegerField(help_text="Quantity in the tray")
    lot_id = models.CharField(max_length=100, help_text="Lot ID")
    draft_save=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.tray_id} - {self.tray_qty} - {self.lot_id}"
    
from django.utils import timezone

class JigUnloadAfterTable(models.Model):
    combine_lot_ids = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="List of combined lot IDs"
    )
    lot_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Auto-generated unique lot ID"
    )
    total_case_qty = models.IntegerField(help_text="Total case quantity")

    def save(self, *args, **kwargs):
        if not self.lot_id:
            # Format: UNLOTYYYYMMDDHHMMSSNNN (N = sequence for the day)
            now = timezone.now()
            date_str = now.strftime("%Y%m%d%H%M%S")
            # Count how many records created today to get sequence
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = JigUnloadAfterTable.objects.filter(
                created_at__gte=today_start
            ).count() + 1
            self.lot_id = f"UNLOT{date_str}{today_count:03d}"
        super().save(*args, **kwargs)

    # Add a created_at field to support daily sequence
    created_at = models.DateTimeField(default=timezone.now)
    selected_user= models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who created the lot", null=True, blank=True)
    unload_accepted = models.BooleanField(default=False, help_text="Indicates if the unload was accepted")
    accepted_qty=models.IntegerField(default=0, help_text="Accepted quantity during unload")
    nickle_ip_few_cases_acceptance=models.BooleanField(default=False)
    nickle_ip_rejection_tray_scan_status=models.BooleanField(default=False)
    nickle_ip_accepted_tray_scan_status=models.BooleanField(default=False)
    nickle_ip_onhold_picking=models.BooleanField(default=False, help_text="Nickle On Hold Picking")
    nickle_ip_top_tray_qty_verified = models.BooleanField(default=False, help_text="Nickle-On Hold Picking")
    nickle_ip_verified_tray_qty=models.IntegerField(default=0, help_text="Nickle-Verified Tray Quantity")
    nickle_ip_top_tray_qty_modify=models.IntegerField(default=0)
    
    unload_audit_accepted = models.BooleanField(default=False, help_text="Indicates if the unload was accepted")
    audit_accepted_qty=models.IntegerField(default=0, help_text="Accepted quantity during unload")
    nickle_audit_few_cases_acceptance=models.BooleanField(default=False)
    nickle_audit_rejection_tray_scan_status=models.BooleanField(default=False)
    nickle_audit_accepted_tray_scan_status=models.BooleanField(default=False)
    nickle_audit_onhold_picking=models.BooleanField(default=False, help_text="Nickle On Hold Picking")
    nickle_audit_top_tray_qty_verified = models.BooleanField(default=False, help_text="Nickle-On Hold Picking")
    nickle_audit_verified_tray_qty=models.IntegerField(default=0, help_text="Nickle-Verified Tray Quantity")
    nickle_audit_top_tray_qty_modify=models.IntegerField(default=0)
    
    last_process_module = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Last Process Module"
    )
    next_process_module = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Next Process Module"
    )
    
    rejected_nickle_ip_stock = models.BooleanField(default=False, help_text="Rejected Nickle IP Stock")  # New field
    rejected_audit_nickle_ip_stock = models.BooleanField(default=False, help_text="Rejected Nickle Audit Stock")  # New field
    audit_check = models.BooleanField(default=False, help_text="Audit Check")  # New field
    send_to_nickel_ip=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.lot_id} - {self.total_case_qty}"


class Nickle_IP_Rejection_Table(models.Model):
    group = models.ForeignKey(IP_RejectionGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='nickle_rejection_reasons')
    rejection_reason_id = models.CharField(max_length=10, null=True, blank=True, editable=False)
    rejection_reason = models.TextField(help_text="Reason for rejection")
    rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def save(self, *args, **kwargs):
        if not self.rejection_reason_id:
            last = Nickle_IP_Rejection_Table.objects.order_by('-rejection_reason_id').first()
            if last and last.rejection_reason_id.startswith('R'):
                last_num = int(last.rejection_reason_id[1:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.rejection_reason_id = f"R{new_num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rejection_reason} - {self.rejection_count}"

#rejection reasons stored tabel , fields ared rejection resoon multiple slection from RejectionTable an dlot_id , user, Total_rejection_qunatity
class Nickle_IP_Rejection_ReasonStore(models.Model):
    rejection_reason = models.ManyToManyField(Nickle_IP_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.total_rejection_quantity} - {self.lot_id}"
    
#give rejected trayscans - fields are lot_id , rejected_tray_quantity , rejected_reson(forign key from RejectionTable), user
class Nickle_IP_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    rejected_tray_id= models.CharField(max_length=100, null=True, blank=True, help_text="Rejected Tray ID")
    rejection_reason = models.ForeignKey(Nickle_IP_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rejection_reason} - {self.rejected_tray_quantity} - {self.lot_id}"

class Nickle_IP_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.accepted_tray_quantity} - {self.lot_id}"
    
class Nickle_IP_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    tray_qty = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=False, help_text="Draft Save")
    is_save= models.BooleanField(default=False, help_text="Save")
     
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"
    
class Nickle_Audit_Rejection_Table(models.Model):
    group = models.ForeignKey(IP_RejectionGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='nickle_audit_rejection_reasons')
    rejection_reason_id = models.CharField(max_length=10, null=True, blank=True, editable=False)
    rejection_reason = models.TextField(help_text="Reason for rejection")
    rejection_count = models.PositiveIntegerField(help_text="Count of rejected items")

    def save(self, *args, **kwargs):
        if not self.rejection_reason_id:
            last = Nickle_Audit_Rejection_Table.objects.order_by('-rejection_reason_id').first()
            if last and last.rejection_reason_id.startswith('R'):
                last_num = int(last.rejection_reason_id[1:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.rejection_reason_id = f"R{new_num:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rejection_reason} - {self.rejection_count}"

#rejection reasons stored tabel , fields ared rejection resoon multiple slection from RejectionTable an dlot_id , user, Total_rejection_qunatity
class Nickle_Audit_Rejection_ReasonStore(models.Model):
    rejection_reason = models.ManyToManyField(Nickle_Audit_Rejection_Table, blank=True)
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_rejection_quantity = models.PositiveIntegerField(help_text="Total Rejection Quantity")
    batch_rejection=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.total_rejection_quantity} - {self.lot_id}"
    
#give rejected trayscans - fields are lot_id , rejected_tray_quantity , rejected_reson(forign key from RejectionTable), user
class Nickle_Audit_Rejected_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    rejected_tray_quantity = models.CharField(help_text="Rejected Tray Quantity")
    rejected_tray_id= models.CharField(max_length=100, null=True, blank=True, help_text="Rejected Tray ID")
    rejection_reason = models.ForeignKey(Nickle_Audit_Rejection_Table, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.rejection_reason} - {self.rejected_tray_quantity} - {self.lot_id}"

class Nickle_Audit_Accepted_TrayScan(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    accepted_tray_quantity = models.CharField(help_text="Accepted Tray Quantity")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.accepted_tray_quantity} - {self.lot_id}"
    
class Nickle_Audit_Accepted_TrayID_Store(models.Model):
    lot_id = models.CharField(max_length=50, null=True, blank=True, help_text="Lot ID")
    tray_id = models.CharField(max_length=100, unique=True)
    tray_qty = models.IntegerField(null=True, blank=True, help_text="Quantity in the tray")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=False, help_text="Draft Save")
    is_save= models.BooleanField(default=False, help_text="Save")
     
    def __str__(self):
        return f"{self.tray_id} - {self.lot_id}"
    
    
    
class TrayAutoSaveData(models.Model):
    """
    Model to store auto-save data for tray scan modal
    Supports cross-browser and user-specific auto-save
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tray_autosave')
    batch_id = models.CharField(max_length=100, db_index=True)
    auto_save_data = models.JSONField()  # Stores the complete tray data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'batch_id']  # One auto-save per user per batch
        db_table = 'tray_auto_save_data'
        indexes = [
            models.Index(fields=['user', 'batch_id']),
            models.Index(fields=['updated_at']),
        ]
    
    def is_expired(self, hours=24):
        """Check if auto-save data is older than specified hours"""
        from datetime import timedelta
        return timezone.now() - self.updated_at > timedelta(hours=hours)
    
    def __str__(self):
        return f"AutoSave: {self.user.username} - {self.batch_id}"
    




@receiver(post_delete, sender=ModelMasterCreation)
def delete_related_trayids(sender, instance, **kwargs):
    TrayId.objects.filter(batch_id=instance).delete()
    DraftTrayId.objects.filter(batch_id=instance).delete()
    
from django.db import models
from django.contrib.auth.models import User


# User Management Models

# ✅ Dept master (Place Department first)
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

# ✅ User Role Master - (Then Role)
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

# ✅ Then UserProfile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    custom_user_id = models.CharField(max_length=10, unique=True, blank=True)

    department = models.CharField(max_length=100)  # <-- store as string
    role = models.CharField(max_length=100)  # <-- store as string

    manager = models.CharField(max_length=100, blank=True, null=True)
    employment_status = models.CharField(
        max_length=20,
        choices=[('On-role', 'On-role'), ('Off-role', 'Off-role')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.custom_user_id}"

