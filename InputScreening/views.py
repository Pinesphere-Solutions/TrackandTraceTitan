from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render
from django.db.models import OuterRef, Subquery, Exists, F
from django.core.paginator import Paginator
from django.templatetags.static import static
import math
from modelmasterapp.models import *
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import traceback
from rest_framework import status
from django.http import JsonResponse
import json
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_GET
from math import ceil
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone



class IS_PickTable(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_PickTable.html'
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user
        
        # Check if user is in Admin group
        is_admin = user.groups.filter(name='Admin').exists() if user.is_authenticated else False


        # ✅ UPDATED: Remove group-related code and simplify rejection reasons
        ip_rejection_reasons = IP_Rejection_Table.objects.all()
       
        
        # Add the subquery for dp_physical_qty_edited
        dp_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty_edited')[:1]
        
       
        accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_Ip_stock')[:1]
        
        accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_tray_scan_status')[:1]
        
        rejected_ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('rejected_ip_stock')[:1]
        
        few_cases_accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('few_cases_accepted_Ip_stock')[:1]
        
        ip_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_onhold_picking')[:1]
        
        
        # Only include ModelMasterCreation with a related TotalStockModel with tray_scan_status=True
        tray_scan_exists = Exists(
            TotalStockModel.objects.filter(
                batch_id=OuterRef('pk'),
                tray_scan_status=True
            )
        )
        


        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0,
            
        ).annotate(
            last_process_module=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('last_process_module')[:1]
            ),
            next_process_module=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('next_process_module')[:1]
            ),
            wiping_required=F('model_stock_no__wiping_required'),
            stock_lot_id=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('lot_id')[:1]
            ),

            ip_person_qty_verified=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('ip_person_qty_verified')[:1]
            ),
            dp_physical_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('dp_physical_qty')[:1]
            ),
            dp_physical_qty_edited=dp_physical_qty_edited_subquery,
            accepted_Ip_stock=accepted_Ip_stock_subquery,
            accepted_tray_scan_status=accepted_tray_scan_status_subquery,
            rejected_ip_stock=rejected_ip_stock_subquery,
            few_cases_accepted_Ip_stock=few_cases_accepted_Ip_stock_subquery,
            ip_onhold_picking=ip_onhold_picking_subquery,
            tray_scan_exists=tray_scan_exists,

            IP_pick_remarks=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('IP_pick_remarks')[:1]
            ),
            created_at=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('created_at')[:1]
            ),
            total_ip_accepted_quantity=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('total_IP_accpeted_quantity')[:1]
            ),
            ip_hold_lot=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('ip_hold_lot')[:1]
            ),
            ip_holding_reason=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('ip_holding_reason')[:1]
            ),
            ip_release_lot=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('ip_release_lot')[:1]
            ),
            ip_release_reason=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('ip_release_reason')[:1]
            ),

                    

           
        ).filter(
            (Q(accepted_Ip_stock=False) | Q(accepted_Ip_stock__isnull=True)) &
            (Q(rejected_ip_stock=False) | Q(rejected_ip_stock__isnull=True)) &
            (Q(accepted_tray_scan_status=False) | Q(accepted_tray_scan_status__isnull=True)),
            tray_scan_exists=True
        ).order_by('-created_at')

        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(page_number)

        master_data = list(page_obj.object_list.values(
            'batch_id',
            'date_time',
            'model_stock_no__model_no',
            'plating_color',
            'polish_finish',
            'version__version_name',
            'vendor_internal',
            'location__location_name',
            'no_of_trays',
            'tray_type',
            'total_batch_quantity',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'wiping_required',
            'stock_lot_id',
            'ip_person_qty_verified',
            'dp_physical_qty',
            'dp_physical_qty_edited',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'IP_pick_remarks',
            'rejected_ip_stock',
            'ip_onhold_picking',
            'created_at',
            'plating_stk_no',
            'polishing_stk_no',
            'category',
            'version__version_internal',
            'total_ip_accepted_quantity',
            'ip_hold_lot',
            'ip_holding_reason',
            'ip_release_lot',
            'ip_release_reason',
        ))

        for data in master_data:
            total_batch_quantity = data.get('total_batch_quantity', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(total_batch_quantity / tray_capacity)
            else:
                data['no_of_trays'] = 0
                
            # Get the ModelMasterCreation instance
            mmc = ModelMasterCreation.objects.filter(batch_id=data['batch_id']).first()
            images = []
            if mmc:
                # Get images from related ModelMaster (model_stock_no)
                model_master = mmc.model_stock_no
                for img in model_master.images.all():
                    if img.master_image:
                        images.append(img.master_image.url)
            # If no images, add a placeholder
            if not images:
                images = [static('assets/images/imagePlaceholder.png')]
            data['model_images'] = images
            
            # Simplified accepted quantity logic
            total_ip_accepted_quantity = data.get('total_ip_accepted_quantity')
            lot_id = data.get('stock_lot_id')

            if total_ip_accepted_quantity and total_ip_accepted_quantity > 0:
                # Use stored accepted quantity if available
                data['display_accepted_qty'] = total_ip_accepted_quantity
            else:
                # Calculate from total_stock - total_rejection_qty (ignoring dp_missing_qty)
                total_rejection_qty = 0
                rejection_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
                if rejection_store and rejection_store.total_rejection_quantity:
                    total_rejection_qty = rejection_store.total_rejection_quantity

                total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
                
                if total_stock_obj and total_rejection_qty > 0:
                    # Calculate: total_stock - rejection_qty
                    data['display_accepted_qty'] = max(total_stock_obj.total_stock - total_rejection_qty, 0)
                    print(f"Calculated accepted qty for {lot_id}: {total_stock_obj.total_stock} - {total_rejection_qty} = {data['display_accepted_qty']}")
                else:
                    # No rejections or no stock data = 0 accepted
                    data['display_accepted_qty'] = 0
            
            # --- Add available_qty for each row ---
            lot_id = data.get('stock_lot_id')
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock_obj:
                # Priority: dp_physical_qty > total_stock
                available_qty = 0
                if hasattr(total_stock_obj, 'dp_physical_qty') and total_stock_obj.dp_physical_qty and total_stock_obj.dp_physical_qty > 0:
                    available_qty = total_stock_obj.dp_physical_qty
                    print(f"✅ Using dp_physical_qty: {available_qty} for lot {lot_id}")
                elif hasattr(total_stock_obj, 'total_stock') and total_stock_obj.total_stock and total_stock_obj.total_stock > 0:
                    available_qty = total_stock_obj.total_stock
                    print(f"⚠️ Using total_stock: {available_qty} for lot {lot_id}")
                
                data['available_qty'] = available_qty
            else:
                data['available_qty'] = 0
                # Get rejection quantity from IP_Rejection_ReasonStore only
            if lot_id:
                try:
                    rejection_qty = 0
                    rejection_record = IP_Rejection_ReasonStore.objects.filter(
                        lot_id=lot_id
                    ).first()
                    
                    if rejection_record and rejection_record.total_rejection_quantity:
                        rejection_qty = rejection_record.total_rejection_quantity
                        print(f"Found rejection for {lot_id}: {rejection_record.total_rejection_quantity}")
                    
                    # Set rejection quantity (only from IP_Rejection_ReasonStore)
                    data['ip_rejection_total_qty'] = rejection_qty
                    print(f"Set rejection qty for {lot_id}: {rejection_qty}")
                                
                except Exception as e:
                    print(f"Error getting rejection for {lot_id}: {str(e)}")
                    data['ip_rejection_total_qty'] = 0
            else:
                data['ip_rejection_total_qty'] = 0
                print(f"No lot_id for batch {data.get('batch_id')}")

        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'ip_rejection_reasons':ip_rejection_reasons,
            'is_admin': is_admin,

        }
        return Response(context, template_name=self.template_name)



# CORRECTED CALCULATION - No Double Counting

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class IPSaveTrayDraftAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            edited_tray_qty = data.get('edited_tray_qty')

            print(f"[IPSaveTrayDraftAPIView] ========== DEBUGGING edited_tray_qty ==========")
            print(f"[IPSaveTrayDraftAPIView] Raw request data: {data}")
            
            if not lot_id:
                return JsonResponse({'success': False, 'error': 'lot_id is required'}, status=400)
            
            try:
                total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            except TotalStockModel.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Stock record not found'}, status=404)

            # Handle edited_tray_qty (keep tracking for audit purposes)
            if edited_tray_qty not in [None, "", "null", "undefined"]:
                try:
                    if isinstance(edited_tray_qty, str):
                        edited_tray_qty = edited_tray_qty.strip()
                        if edited_tray_qty == "":
                            edited_tray_qty = None
                    
                    if edited_tray_qty is not None:
                        edited_tray_qty = int(edited_tray_qty)
                        print(f"[IPSaveTrayDraftAPIView] Converted edited_tray_qty to int: {edited_tray_qty}")
                        
                        # Find and update the top tray
                        top_tray = TrayId.objects.filter(lot_id=lot_id, top_tray=True).first()
                        if top_tray:
                            prev_qty = top_tray.tray_quantity or 0
                            
                            # Store original quantity for audit (but don't use in calculation)
                            if total_stock.original_tray_qty is None:
                                total_stock.original_tray_qty = prev_qty
                                print(f"[IPSaveTrayDraftAPIView] 📌 Storing original tray qty: {prev_qty}")
                            
                            # Update the tray quantity
                            top_tray.tray_quantity = edited_tray_qty
                            top_tray.save(update_fields=['tray_quantity'])
                            
                            # Calculate edit difference for audit tracking
                            edit_difference = total_stock.original_tray_qty - edited_tray_qty
                            total_stock.cumulative_edit_difference = edit_difference
                            
                            print(f"✅ [IPSaveTrayDraftAPIView] Updated top tray {top_tray.tray_id} qty from {prev_qty} to {edited_tray_qty}")
                            print(f"📊 [IPSaveTrayDraftAPIView] Edit tracking: original({total_stock.original_tray_qty}) - new({edited_tray_qty}) = {edit_difference}")
                        else:
                            print("⚠️ [IPSaveTrayDraftAPIView] Top tray not found for lot:", lot_id)
                            
                except (ValueError, TypeError) as e:
                    print(f"❌ [IPSaveTrayDraftAPIView] Error converting edited_tray_qty: {e}")
                    return JsonResponse({"success": False, "error": f"Edited tray qty must be an integer: {e}"}, status=400)

            # 🔥 CORRECTED CALCULATION: Simple total stock accounting
            # Calculate current verified quantity
            verified_qty = TrayId.objects.filter(
                lot_id=lot_id,
                IP_tray_verified=True
            ).aggregate(total=models.Sum('tray_quantity'))['total'] or 0

            # 🔥 KEY FIX: Use simple subtraction, no double counting
            final_missing_qty = total_stock.total_stock - verified_qty
            
            print(f"✅ [IPSaveTrayDraftAPIView] CORRECTED Calculation:")
            print(f"   - Total stock: {total_stock.total_stock}")
            print(f"   - Verified qty: {verified_qty}")
            print(f"   - Missing qty: {total_stock.total_stock} - {verified_qty} = {final_missing_qty}")
            print(f"   - Edit difference (audit only): {total_stock.cumulative_edit_difference}")

            # Save the corrected values
            total_stock.ip_onhold_picking = True
            total_stock.dp_physical_qty = verified_qty
            total_stock.dp_physical_qty_edited = True

            total_stock.save(update_fields=[
                'ip_onhold_picking', 
                'dp_physical_qty', 
                'dp_physical_qty_edited',
                'cumulative_edit_difference',
                'original_tray_qty'
            ])
            
            print(f"✅ [IPSaveTrayDraftAPIView] Final saved values:")
            print(f"   - dp_physical_qty: {verified_qty} ✅")
            
            return JsonResponse({
                'success': True, 
                'message': 'Tray scan saved with corrected calculation.',
                'lot_id': lot_id,
                'missing_qty': final_missing_qty,
                'physical_qty': verified_qty
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'}, status=500)

class SaveIPCheckboxView(APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            lot_id = data.get("lot_id")
            edited_tray_qty = data.get("edited_tray_qty")

            print(f"[SaveIPCheckboxView] ========== DEBUGGING edited_tray_qty ==========")
            print(f"[SaveIPCheckboxView] Raw request.data: {data}")
            print(f"[SaveIPCheckboxView] lot_id: {lot_id}")
            print(f"[SaveIPCheckboxView] edited_tray_qty received: {edited_tray_qty}")

            if not lot_id:
                return Response({"success": False, "error": "Lot ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            total_stock.ip_person_qty_verified = True

            # Handle edited_tray_qty - Update the top tray first
            if edited_tray_qty not in [None, "", "null", "undefined"]:
                try:
                    if isinstance(edited_tray_qty, str):
                        edited_tray_qty = edited_tray_qty.strip()
                        if edited_tray_qty == "":
                            edited_tray_qty = None
                    
                    if edited_tray_qty is not None:
                        edited_tray_qty = int(edited_tray_qty)
                        print(f"[SaveIPCheckboxView] Converted edited_tray_qty to int: {edited_tray_qty}")
                        
                        # Find and update the top tray for this lot
                        top_tray = TrayId.objects.filter(lot_id=lot_id, top_tray=True).first()
                        if top_tray:
                            prev_qty = top_tray.tray_quantity or 0
                            top_tray.tray_quantity = edited_tray_qty
                            top_tray.save(update_fields=['tray_quantity'])
                            print(f"✅ [SaveIPCheckboxView] Updated top tray {top_tray.tray_id} qty from {prev_qty} to {edited_tray_qty}")
                        else:
                            print("⚠️ [SaveIPCheckboxView] Top tray not found for lot:", lot_id)
                            
                except (ValueError, TypeError) as e:
                    print(f"❌ [SaveIPCheckboxView] Error converting edited_tray_qty: {e}")
                    return JsonResponse({"success": False, "error": f"Edited tray qty must be an integer: {e}"}, status=400)

            # 🔥 CORRECTED DELINK LOGIC: Check ALL trays with same lot_id for zero quantity
            print(f"\n🔗 [SaveIPCheckboxView] ========== DELINK CONCEPT ==========")
            
            # Find ALL trays with same lot_id that have zero quantity
            zero_qty_trays = TrayId.objects.filter(
                lot_id=lot_id,
                tray_quantity=0
            )
            
            delinked_trays_info = []
            
            if zero_qty_trays.exists():
                print(f"[SaveIPCheckboxView] Found {zero_qty_trays.count()} trays with zero quantity for lot {lot_id}")
                
                for tray in zero_qty_trays:
                    # Store tray info before delinking
                    tray_info = {
                        'tray_id': tray.tray_id,
                        'prev_lot_id': tray.lot_id,
                        'prev_batch_id': tray.batch_id,
                        'prev_scanned': tray.scanned,
                        'prev_IP_tray_verified': tray.IP_tray_verified,
                        'prev_ip_top_tray': tray.ip_top_tray,
                        'prev_top_tray': tray.top_tray,
                        'prev_delink_tray': tray.delink_tray
                    }
                    
                    # Apply delink logic
                    tray.lot_id = None              # Empty
                    tray.batch_id = None            # Empty  
                    tray.scanned = False
                    tray.IP_tray_verified = False
                    tray.ip_top_tray = False
                    tray.top_tray = False
                    tray.delink_tray = True
                    # tray_quantity already 0
                    
                    tray.save(update_fields=[
                        'lot_id', 'batch_id', 'scanned', 'IP_tray_verified', 
                        'ip_top_tray', 'top_tray', 'delink_tray'
                    ])
                    
                    delinked_trays_info.append(tray_info)
                    
                    print(f"✅ [SaveIPCheckboxView] DELINKED tray {tray.tray_id}:")
                    print(f"   - lot_id: {tray_info['prev_lot_id']} → None")
                    print(f"   - batch_id: {tray_info['prev_batch_id']} → None")
                    print(f"   - scanned: {tray_info['prev_scanned']} → False")
                    print(f"   - IP_tray_verified: {tray_info['prev_IP_tray_verified']} → False")
                    print(f"   - ip_top_tray: {tray_info['prev_ip_top_tray']} → False")
                    print(f"   - top_tray: {tray_info['prev_top_tray']} → False")
                    print(f"   - delink_tray: {tray_info['prev_delink_tray']} → True")
                    
                print(f"✅ [SaveIPCheckboxView] Total delinked trays: {len(delinked_trays_info)}")
            else:
                print(f"[SaveIPCheckboxView] No trays with zero quantity found for lot {lot_id}")
                
            print(f"🔗 [SaveIPCheckboxView] ========== DELINK CONCEPT COMPLETE ==========\n")

            # Calculate final quantities using simple total stock accounting
            verified_qty = TrayId.objects.filter(
                lot_id=lot_id,
                IP_tray_verified=True
            ).aggregate(total=models.Sum('tray_quantity'))['total'] or 0

            # Simple calculation - no double counting
            final_missing_qty = total_stock.total_stock - verified_qty

            total_stock.dp_physical_qty = verified_qty
            total_stock.ip_verification_timestamp = timezone.now()
            total_stock.ip_verification_method = "tray_scan_auto"

            total_stock.save()
            
            print(f"✅ [SaveIPCheckboxView] Final saved values:")
            print(f"   - dp_physical_qty: {verified_qty}")
            
            # 🔥 REJECTION LOGIC: Handle unverified trays after saving (EXCLUDE DELINKED TRAYS)
            print(f"\n🚫 [SaveIPCheckboxView] ========== REJECTION LOGIC ==========")
            
            # Find all unverified trays for this lot_id that are NOT delinked and have quantity > 0
            unverified_trays = TrayId.objects.filter(
                lot_id=lot_id,
                IP_tray_verified=False,
                delink_tray=False,  # 🔥 EXCLUDE delinked trays
                tray_quantity__gt=0  # 🔥 EXCLUDE trays with zero quantity
            )
            
            print(f"[SaveIPCheckboxView] Checking for unverified trays (excluding delinked/zero qty)...")
            print(f"[SaveIPCheckboxView] Found {unverified_trays.count()} unverified trays for rejection")
            
            if unverified_trays.exists():
                # Calculate total rejection quantity
                total_rejection_qty = 0
                rejected_tray_ids = []
                
                # Mark each unverified tray as rejected and calculate total qty
                for tray in unverified_trays:
                    # Mark as rejected
                    tray.rejected_tray = True
                    tray.save(update_fields=['rejected_tray'])
                    
                    # Add to rejection tracking
                    tray_qty = tray.tray_quantity or 0
                    total_rejection_qty += tray_qty
                    rejected_tray_ids.append(tray.tray_id)
                    
                    print(f"   - Marked tray {tray.tray_id} as rejected (qty: {tray_qty}, verified: {tray.IP_tray_verified})")
                
                print(f"✅ [SaveIPCheckboxView] Total rejection quantity: {total_rejection_qty}")
                print(f"✅ [SaveIPCheckboxView] Rejected tray IDs: {rejected_tray_ids}")
                
                # 🔥 Log what was excluded from rejection
                delinked_trays = TrayId.objects.filter(lot_id=lot_id, delink_tray=True)
                if delinked_trays.exists():
                    print(f"ℹ️ [SaveIPCheckboxView] Excluded from rejection (delinked): {list(delinked_trays.values_list('tray_id', flat=True))}")
                    
                zero_qty_trays = TrayId.objects.filter(lot_id=lot_id, tray_quantity=0, IP_tray_verified=False, delink_tray=False)
                if zero_qty_trays.exists():
                    print(f"ℹ️ [SaveIPCheckboxView] Excluded from rejection (zero qty): {list(zero_qty_trays.values_list('tray_id', flat=True))}")
                
                # 🔥 CREATE REJECTION RECORD in IP_Rejection_ReasonStore
                if total_rejection_qty > 0:
                    try:
                        print(f"[SaveIPCheckboxView] Creating/updating rejection record...")
                        print(f"[SaveIPCheckboxView] Current user: {request.user}")
                        print(f"[SaveIPCheckboxView] Lot ID: {lot_id}")
                        print(f"[SaveIPCheckboxView] Total rejection qty: {total_rejection_qty}")
                        
                        # Check if rejection record already exists for this lot_id
                        existing_rejection = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
                        
                        if existing_rejection:
                            # Update existing record
                            existing_rejection.total_rejection_quantity = total_rejection_qty
                            existing_rejection.user = request.user  # Update user as well
                            existing_rejection.save(update_fields=['total_rejection_quantity', 'user'])
                            print(f"✅ [SaveIPCheckboxView] Updated existing rejection record for lot {lot_id}")
                            print(f"   - ID: {existing_rejection.id}")
                            print(f"   - total_rejection_quantity: {existing_rejection.total_rejection_quantity}")
                            print(f"   - user: {existing_rejection.user}")
                        else:
                            # Create new rejection record
                            rejection_record = IP_Rejection_ReasonStore.objects.create(
                                lot_id=lot_id,
                                total_rejection_quantity=total_rejection_qty,
                                user=request.user,  # 🔥 FIX: Add required user field
                                batch_rejection=False  # Default value
                            )
                            print(f"✅ [SaveIPCheckboxView] Created new rejection record for lot {lot_id}:")
                            print(f"   - ID: {rejection_record.id}")
                            print(f"   - lot_id: {rejection_record.lot_id}")
                            print(f"   - total_rejection_quantity: {rejection_record.total_rejection_quantity}")
                            print(f"   - user: {rejection_record.user}")
                            print(f"   - batch_rejection: {rejection_record.batch_rejection}")
                            
                        # Verify the record was saved
                        saved_record = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
                        if saved_record:
                            print(f"✅ [SaveIPCheckboxView] Verification: Record exists in database with ID {saved_record.id}")
                        else:
                            print(f"❌ [SaveIPCheckboxView] ERROR: Record not found in database after creation!")
                            
                    except Exception as e:
                        print(f"❌ [SaveIPCheckboxView] Error creating rejection record: {e}")
                        import traceback
                        traceback.print_exc()
                        # Continue processing, don't fail the entire request
                        return JsonResponse({"success": False, "error": f"Error creating rejection record: {str(e)}"}, status=500)
                else:
                    print(f"[SaveIPCheckboxView] No rejection quantity to record (total_rejection_qty = {total_rejection_qty})")
                        
            else:
                print(f"[SaveIPCheckboxView] No unverified trays found - no rejections to process")
            
            print(f"🚫 [SaveIPCheckboxView] ========== REJECTION LOGIC COMPLETE ==========\n")
            
            # Prepare response with additional info
            response_data = {
                "success": True,
                "dp_physical_qty": verified_qty
            }
            
            # Add delink info if trays were delinked
            if delinked_trays_info:
                response_data["delinked_trays"] = {
                    "delinked_tray_count": len(delinked_trays_info),
                    "delinked_tray_ids": [info['tray_id'] for info in delinked_trays_info]
                }
            
            # Add rejection info if trays were rejected
            if 'total_rejection_qty' in locals() and total_rejection_qty > 0:
                response_data["rejections"] = {
                    "rejected_tray_count": len(rejected_tray_ids) if 'rejected_tray_ids' in locals() else 0,
                    "total_rejection_qty": total_rejection_qty,
                    "rejected_tray_ids": rejected_tray_ids if 'rejected_tray_ids' in locals() else []
                }
            
            return Response(response_data)

        except TotalStockModel.DoesNotExist:
            return Response({"success": False, "error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()   
            return Response({"success": False, "error": "Unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class SaveIPPickRemarkAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            remark = data.get('remark', '').strip()
            if not batch_id:
                return JsonResponse({'success': False, 'error': 'Missing batch_id'}, status=400)
            mmc = ModelMasterCreation.objects.filter(batch_id=batch_id).first()
            if not mmc:
                return JsonResponse({'success': False, 'error': 'Batch not found'}, status=404)
            batch_obj = TotalStockModel.objects.filter(batch_id=mmc).first()  
            if not batch_obj:
                return JsonResponse({'success': False, 'error': 'TotalStockModel not found'}, status=404)
            batch_obj.IP_pick_remarks = remark
            batch_obj.save(update_fields=['IP_pick_remarks'])
            return JsonResponse({'success': True, 'message': 'Remark saved'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class IPUpdateBatchQuantityAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            new_quantity = data.get('dp_physical_qty')
            if not batch_id or new_quantity is None:
                return JsonResponse({'success': False, 'error': 'Missing batch_id or quantity'}, status=400)
            # Find the TotalStockModel for this batch
            stock_obj = TotalStockModel.objects.filter(batch_id__batch_id=batch_id).first()
            if not stock_obj:
                return JsonResponse({'success': False, 'error': 'Stock not found for this batch'}, status=404)
            stock_obj.dp_physical_qty = new_quantity
            stock_obj.dp_physical_qty_edited = True  # <-- Set the flag here
            stock_obj.save(update_fields=['dp_physical_qty', 'dp_physical_qty_edited'])
            return JsonResponse({'success': True, 'message': 'Quantity updated'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class IPDeleteBatchAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            stock_lot_id = data.get('stock_lot_id')
            if not stock_lot_id:
                return JsonResponse({'success': False, 'error': 'Missing stock_lot_id'}, status=400)
            obj = TotalStockModel.objects.filter(lot_id=stock_lot_id).first()
            if not obj:
                return JsonResponse({'success': False, 'error': 'Stock lot not found'}, status=404)
            obj.delete()
            return JsonResponse({'success': True, 'message': 'Stock lot deleted'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class IS_Accepted_form(APIView):

    def post(self, request, format=None):
        data = request.data
        lot_id = data.get("stock_lot_id")
        try:
            total_stock_data = TotalStockModel.objects.get(lot_id=lot_id)
            
            if total_stock_data.accepted_Ip_stock:
                total_stock_data.accepted_Ip_stock = False
                total_stock_data.few_cases_accepted_Ip_stock =False
                total_stock_data.rejected_ip_stock =False
                
            total_stock_data.accepted_Ip_stock = True
    
            # Use dp_physical_qty if set and > 0, else use total_stock
            physical_qty = total_stock_data.dp_physical_qty
            if not physical_qty or physical_qty == 0:
                physical_qty = total_stock_data.total_stock
    
            total_stock_data.total_IP_accpeted_quantity = physical_qty
    
            # Update process modules
            total_stock_data.next_process_module = "Brass QC"
            total_stock_data.last_process_module = "Input screening"
            total_stock_data.last_process_date_time = timezone.now()
            

            
            total_stock_data.save()
            return Response({"success": True})
        
        except TotalStockModel.DoesNotExist:
            return Response(
                {"success": False, "error": "Stock not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BatchRejectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            lot_id = data.get('lot_id')  # <-- get lot_id from POST
            total_qty = data.get('total_qty', 0)

            # Get ModelMasterCreation by batch_id string
            mmc = ModelMasterCreation.objects.filter(batch_id=batch_id).first()
            if not mmc:
                return Response({'success': False, 'error': 'Batch not found'}, status=404)

            # Get TotalStockModel using lot_id (not batch_id)
            total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not total_stock:
                return Response({'success': False, 'error': 'TotalStockModel not found'}, status=404)

            # Get dp_physical_qty if set and > 0, else use total_stock
            qty = total_stock.dp_physical_qty 

            # Set rejected_ip_stock = True

            total_stock.rejected_ip_stock = True
            total_stock.last_process_module = "Input screening"
            total_stock.next_process_module = "Brass QC"
            total_stock.ip_onhold_picking = False
            
            # Set last_process_date_time to now
            total_stock.last_process_date_time = timezone.now()

            total_stock.save(update_fields=[
                'rejected_ip_stock',
                'ip_onhold_picking',
                'last_process_module',
                'next_process_module',
                'last_process_date_time'
            ])
            
            # Create IP_Rejection_ReasonStore entry
            IP_Rejection_ReasonStore.objects.create(
                lot_id=lot_id,
                user=request.user,
                total_rejection_quantity=qty,
                batch_rejection=True
            )
            
            # ✅ Mark all trays for this lot as rejected
            TrayId.objects.filter(lot_id=lot_id).update(rejected_tray=True)


            return Response({'success': True, 'message': 'Batch rejection saved.'})

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)



# ✅ UPDATED: TrayRejectionAPIView to handle multiple tray IDs per rejection reason
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TrayRejectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_actual_tray_distribution(self, lot_id, tray_capacity):
        """
        Get actual tray quantities for the lot.
        Returns list like [4, 12, 12, 12] representing actual tray quantities.
        """
        try:
            # Option 1: Get from TrayId model if it stores individual tray quantities
            tray_records = TrayId.objects.filter(lot_id=lot_id).order_by('created_at')
            if tray_records.exists():
                tray_quantities = []
                for tray in tray_records:
                    if hasattr(tray, 'tray_quantity') and tray.tray_quantity:
                        tray_quantities.append(tray.tray_quantity)
                    else:
                        tray_quantities.append(tray_capacity)  # fallback to standard capacity
                
                if tray_quantities:
                    print(f"✅ Found actual tray distribution from TrayId: {tray_quantities}")
                    return tray_quantities
        except Exception as e:
            print(f"Could not get tray distribution from TrayId: {e}")
        
        # Option 2: Get from TotalStockModel if it has tray distribution info
        try:
            total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock:
                # Check if there's a field storing tray distribution
                if hasattr(total_stock, 'tray_qty_list') and total_stock.tray_qty_list:
                    try:
                        import json
                        tray_quantities = json.loads(total_stock.tray_qty_list)
                        if isinstance(tray_quantities, list) and len(tray_quantities) > 0:
                            print(f"✅ Found actual tray distribution from TotalStockModel: {tray_quantities}")
                            return tray_quantities
                    except:
                        pass
                
                # Calculate from total quantity and number of trays
                if hasattr(total_stock, 'total_stock') and hasattr(total_stock, 'no_of_trays'):
                    total_qty = total_stock.total_stock
                    num_trays = total_stock.no_of_trays
                    
                    if total_qty and num_trays and tray_capacity:
                        # Calculate distribution: remainder first, then full capacity trays
                        full_trays = total_qty // tray_capacity
                        remainder = total_qty % tray_capacity
                        
                        distribution = []
                        if remainder > 0:
                            distribution.append(remainder)  # Top tray with remainder
                        
                        for i in range(full_trays):
                            distribution.append(tray_capacity)  # Full capacity trays
                        
                        # Ensure we don't exceed the actual number of trays
                        if len(distribution) > num_trays:
                            distribution = distribution[:num_trays]
                        elif len(distribution) < num_trays:
                            # Add more trays with standard capacity if needed
                            while len(distribution) < num_trays:
                                distribution.append(tray_capacity)
                        
                        print(f"✅ Calculated tray distribution: total_qty={total_qty}, num_trays={num_trays}, capacity={tray_capacity}")
                        print(f"   Result: {distribution}")
                        return distribution
        except Exception as e:
            print(f"Could not calculate tray distribution: {e}")
        
        # Fallback: assume all trays have standard capacity
        print(f"⚠️ Using fallback: all trays with capacity {tray_capacity}")
        return [tray_capacity] * 4  # Default to 4 trays

    def calculate_trays_with_quantity_from_distribution(self, rejection_qty, tray_distribution):
        """
        Calculate which trays get any quantity (complete OR partial) based on actual tray distribution.
        Returns: (trays_with_quantity, needs_tray_scanning)
        """
        trays_with_quantity = []
        remaining_qty = rejection_qty
        
        print(f"Calculating trays with quantity for rejection qty: {rejection_qty}")
        print(f"Actual tray distribution: {tray_distribution}")
        
        # Go through trays in order (top tray first)
        for i, tray_capacity in enumerate(tray_distribution):
            if remaining_qty <= 0:
                break
                
            qty_for_this_tray = min(remaining_qty, tray_capacity)
            
            # ✅ NEW: Include ANY tray that gets some quantity (complete OR partial)
            trays_with_quantity.append({
                'tray_index': i,
                'tray_capacity': tray_capacity,
                'tray_qty': qty_for_this_tray,
                'is_top_tray': i == 0,
                'is_complete': qty_for_this_tray == tray_capacity,
                'is_partial': qty_for_this_tray < tray_capacity
            })
            
            remaining_qty -= qty_for_this_tray
            
            status = "Complete" if qty_for_this_tray == tray_capacity else "Partial"
            print(f"  Tray {i + 1}: {qty_for_this_tray}/{tray_capacity} qty ({status})")
        
        # ✅ CORRECTED: Only skip tray scanning for partial top tray ONLY
        needs_tray_scanning = not (
            len(trays_with_quantity) == 1 and 
            trays_with_quantity[0]['is_top_tray'] and 
            trays_with_quantity[0]['is_partial']
        )
        
        print(f"  Needs tray scanning: {needs_tray_scanning}")
        return trays_with_quantity, needs_tray_scanning

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            batch_id = data.get('batch_id')
            tray_scans = data.get('tray_scans', [])  # List of {tray_id, tray_qty, reason_id}
            rejection_data = data.get('rejection_data', [])  # List of {reason_id, qty}

            print(f"✅ [TrayRejectionAPIView] Received data:")
            print(f"   - lot_id: {lot_id}")
            print(f"   - batch_id: {batch_id}")
            print(f"   - rejection_data: {rejection_data}")
            print(f"   - tray_scans: {tray_scans}")

            # Find the SHORTAGE reason by name (case-insensitive)
            shortage_reason_obj = IP_Rejection_Table.objects.filter(rejection_reason__iexact='SHORTAGE').first()
            shortage_reason_id = shortage_reason_obj.rejection_reason_id if shortage_reason_obj else None

            print(f"✅ Found SHORTAGE reason: {shortage_reason_obj} with ID: {shortage_reason_id}")

            # Calculate SHORTAGE quantity
            shortage_qty = 0
            for item in rejection_data:
                if item.get('reason_id') == shortage_reason_id:
                    shortage_qty += int(item.get('qty', 0))

            # Validate input
            if not lot_id or (not tray_scans and not any(
                item.get('reason_id') == shortage_reason_id and int(item.get('qty', 0)) > 0
                for item in rejection_data
            )):
                return Response({'success': False, 'error': 'Missing lot_id or tray_scans'}, status=400)

            # Get the TotalStockModel for this lot_id
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not total_stock_obj:
                return Response({'success': False, 'error': 'TotalStockModel not found'}, status=404)

            # Use dp_physical_qty if set and > 0, else use total_stock
            available_qty = total_stock_obj.dp_physical_qty 

            # Calculate total quantity only from NON-SHORTAGE rejections for validation
            total_non_shortage_qty = 0
            for item in rejection_data:
                if item.get('reason_id') != shortage_reason_id:
                    total_non_shortage_qty += int(item.get('qty', 0))

            # Check if non-shortage quantity exceeds available quantity
            if total_non_shortage_qty > available_qty:
                return Response({
                    'success': False,
                    'error': f'Total non-shortage rejection quantity ({total_non_shortage_qty}) exceeds available quantity ({available_qty}).'
                }, status=400)

            # ✅ NEW: Get dynamic tray capacity from TotalStockModel
            tray_capacity = None

            # Try to get tray capacity from different sources (adjust based on your model structure)
            if hasattr(total_stock_obj, 'tray_capacity') and total_stock_obj.tray_capacity:
                tray_capacity = total_stock_obj.tray_capacity
                print(f"✅ Found tray capacity from TotalStockModel: {tray_capacity}")
            elif hasattr(total_stock_obj, 'model_no') and total_stock_obj.model_no:
                # Get from ModelMasterCreation if available
                try:
                    model_master = ModelMasterCreation.objects.filter(model_no=total_stock_obj.model_no).first()
                    if model_master and hasattr(model_master, 'tray_capacity'):
                        tray_capacity = model_master.tray_capacity
                        print(f"✅ Found tray capacity from ModelMasterCreation: {tray_capacity}")
                except Exception as e:
                    print(f"Could not get tray capacity from ModelMasterCreation: {e}")

            # If still no tray capacity found, try to get from existing TrayId records for this lot
            if not tray_capacity:
                try:
                    sample_tray = TrayId.objects.filter(lot_id=lot_id).first()
                    if sample_tray and hasattr(sample_tray, 'tray_capacity'):
                        tray_capacity = sample_tray.tray_capacity
                        print(f"✅ Found tray capacity from TrayId: {tray_capacity}")
                except Exception as e:
                    print(f"Could not get tray capacity from TrayId: {e}")

            # Try to get from batch_id model if available
            if not tray_capacity and hasattr(total_stock_obj, 'batch_id') and total_stock_obj.batch_id:
                try:
                    batch_obj = total_stock_obj.batch_id
                    if hasattr(batch_obj, 'tray_capacity') and batch_obj.tray_capacity:
                        tray_capacity = batch_obj.tray_capacity
                        print(f"✅ Found tray capacity from Batch: {tray_capacity}")
                except Exception as e:
                    print(f"Could not get tray capacity from Batch: {e}")

            # Default fallback if no tray capacity found anywhere
            if not tray_capacity:
                tray_capacity = 10  # Conservative default
                print(f"⚠️ Warning: Could not determine tray capacity for lot {lot_id}, using default: {tray_capacity}")
            else:
                print(f"✅ Using tray capacity for lot {lot_id}: {tray_capacity}")

            # ✅ NEW: Get actual tray distribution for this lot
            tray_distribution = self.get_actual_tray_distribution(lot_id, tray_capacity)

            # ✅ UPDATED: Validate tray_scans data structure with actual tray distribution
            print(f"✅ [TrayRejectionAPIView] Validating {len(tray_scans)} tray scans...")
            
            # Group tray scans by reason_id for validation
            tray_scans_by_reason = {}
            for scan in tray_scans:
                reason_id = scan.get('reason_id')
                if reason_id not in tray_scans_by_reason:
                    tray_scans_by_reason[reason_id] = []
                tray_scans_by_reason[reason_id].append(scan)

            # ✅ CORRECTED: Validate that tray scan quantities match ALL trays with quantity
            for rejection in rejection_data:
                reason_id = rejection.get('reason_id')
                rejection_qty = int(rejection.get('qty', 0))
                
                if reason_id == shortage_reason_id:
                    continue  # Skip SHORTAGE validation
                
                # ✅ NEW: Calculate trays that get any quantity using ACTUAL tray distribution
                trays_with_quantity, needs_tray_scanning = self.calculate_trays_with_quantity_from_distribution(
                    rejection_qty, tray_distribution
                )
                
                print(f"✅ Rejection analysis for reason {reason_id}:")
                print(f"   - Total rejection qty: {rejection_qty}")
                print(f"   - Tray distribution: {tray_distribution}")
                print(f"   - Trays with quantity: {len(trays_with_quantity)}")
                print(f"   - Needs tray scanning: {needs_tray_scanning}")
                print(f"   - Trays info: {trays_with_quantity}")
                
                if needs_tray_scanning:
                    # Calculate expected total from all trays with quantity
                    expected_total_qty = sum(tray['tray_qty'] for tray in trays_with_quantity)
                    
                    if reason_id in tray_scans_by_reason:
                        tray_total = sum(int(scan.get('tray_qty', 0)) for scan in tray_scans_by_reason[reason_id])
                        
                        # ✅ UPDATED: Validate against total quantity from ALL trays with quantity
                        if tray_total != expected_total_qty:
                            trays_desc = ", ".join([
                                f"Tray {t['tray_index'] + 1}({t['tray_qty']}/{t['tray_capacity']} qty)" + 
                                (" - Top" if t['is_top_tray'] else "") +
                                (" - Complete" if t['is_complete'] else " - Partial")
                                for t in trays_with_quantity
                            ])
                            
                            return Response({
                                'success': False,
                                'error': f'Tray scan total ({tray_total}) does not match expected total quantity ({expected_total_qty}) for reason {reason_id}. Expected trays: {trays_desc}'
                            }, status=400)
                            
                        print(f"✅ Validated reason {reason_id}: {tray_total} tray scans = {expected_total_qty} expected")
                        
                        # ✅ NEW: Validate individual tray quantities match expected
                        expected_tray_count = len(trays_with_quantity)
                        actual_tray_count = len(tray_scans_by_reason[reason_id])
                        
                        if actual_tray_count != expected_tray_count:
                            return Response({
                                'success': False,
                                'error': f'Expected {expected_tray_count} tray scans for reason {reason_id}, but received {actual_tray_count}'
                            }, status=400)
                            
                    else:
                        # Expected tray scans but none provided
                        trays_desc = ", ".join([
                            f"Tray {t['tray_index'] + 1}({t['tray_qty']}/{t['tray_capacity']} qty)" + 
                            (" - Top" if t['is_top_tray'] else "") +
                            (" - Complete" if t['is_complete'] else " - Partial")
                            for t in trays_with_quantity
                        ])
                        return Response({
                            'success': False,
                            'error': f'Expected {len(trays_with_quantity)} tray scan(s) for reason {reason_id}: {trays_desc}, but no tray scans provided'
                        }, status=400)
                else:
                    # No tray scanning needed - this is partial top tray only
                    print(f"✅ Reason {reason_id}: Partial top tray only ({rejection_qty}), no tray scanning required")
                    
                    # ✅ UPDATED: Allow optional tray scans but validate them if provided
                    if reason_id in tray_scans_by_reason:
                        # If tray scans are provided, validate they match the expected quantity
                        tray_total = sum(int(scan.get('tray_qty', 0)) for scan in tray_scans_by_reason[reason_id])
                        expected_total_qty = sum(tray['tray_qty'] for tray in trays_with_quantity)
                        
                        if tray_total != expected_total_qty:
                            return Response({
                                'success': False,
                                'error': f'Tray scan total ({tray_total}) does not match expected quantity ({expected_total_qty}) for reason {reason_id}'
                            }, status=400)
                        
                        print(f"✅ Optional tray scans provided and validated for reason {reason_id}: {tray_total} = {expected_total_qty}")
                    else:
                        print(f"✅ No tray scans provided for partial top tray rejection {reason_id} - this is acceptable")

            # Handle SHORTAGE rejections (without tray_id)
            for item in rejection_data:
                if item.get('reason_id') == shortage_reason_id:
                    qty = int(item.get('qty', 0))
                    if qty > 0:
                        try:
                            reason_obj = IP_Rejection_Table.objects.get(rejection_reason_id=shortage_reason_id)
                            IP_Rejected_TrayScan.objects.create(
                                lot_id=lot_id,
                                rejected_tray_quantity=qty,
                                rejection_reason=reason_obj,
                                user=request.user,
                                rejected_tray_id=''  # Empty tray_id for SHORTAGE
                            )
                            print(f"✅ Created SHORTAGE rejection: qty={qty}, no tray_id")
                        except IP_Rejection_Table.DoesNotExist:
                            print(f"Warning: SHORTAGE reason {shortage_reason_id} not found")
                            continue

            # ✅ UPDATED: Handle NON-SHORTAGE rejections using tray_scans data
            for scan in tray_scans:
                tray_id = scan.get('tray_id')
                tray_qty = int(scan.get('tray_qty', 0))
                reason_id = scan.get('reason_id')
                
                # Only update if this is a new tray (new_tray=True)
                tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
                if tray_obj and getattr(tray_obj, 'new_tray', False):
                    tray_obj.lot_id = lot_id  # Assign to selected lot_id if not already
                    tray_obj.rejected_tray = True
                    tray_obj.top_tray = False
                    tray_obj.tray_quantity = tray_qty  # <-- Save the tray quantity

                    tray_obj.save(update_fields=['lot_id', 'rejected_tray', 'top_tray',  'scanned','tray_quantity'])
                
                if tray_qty > 0 and reason_id and tray_id:
                    try:
                        reason_obj = IP_Rejection_Table.objects.get(rejection_reason_id=reason_id)
                        
                        # Mark tray as rejected
                        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
                        if tray_obj:
                            tray_obj.rejected_tray = True
                            tray_obj.save(update_fields=['rejected_tray'])
                        
                        # Create rejection scan record
                        IP_Rejected_TrayScan.objects.create(
                            lot_id=lot_id,
                            rejected_tray_quantity=tray_qty,
                            rejection_reason=reason_obj,
                            user=request.user,
                            rejected_tray_id=tray_id
                        )
                        print(f"✅ Created {reason_obj.rejection_reason} rejection: qty={tray_qty}, tray_id={tray_id}")
                        
                    except IP_Rejection_Table.DoesNotExist:
                        print(f"Warning: Rejection reason {reason_id} not found")
                        continue

            # ✅ UPDATED: Handle any remaining partial quantities
            # This handles cases where rejection_data total > tray_scans total
            for item in rejection_data:
                reason_id = item.get('reason_id')
                total_rejection_qty = int(item.get('qty', 0))
                
                if reason_id == shortage_reason_id:
                    continue  # Already handled above
                
                # Calculate how much was covered by tray scans
                tray_scan_qty = 0
                if reason_id in tray_scans_by_reason:
                    tray_scan_qty = sum(int(scan.get('tray_qty', 0)) for scan in tray_scans_by_reason[reason_id])
                
                # For the corrected logic, tray_scan_qty should equal total_rejection_qty for non-shortage
                # But if there's any discrepancy, handle it gracefully
                if tray_scan_qty < total_rejection_qty:
                    remaining_qty = total_rejection_qty - tray_scan_qty
                    print(f"⚠️ Warning: Remaining quantity {remaining_qty} for reason {reason_id} not covered by tray scans")
                    
                    # This shouldn't happen with the corrected logic, but handle it anyway
                    try:
                        reason_obj = IP_Rejection_Table.objects.get(rejection_reason_id=reason_id)
                        
                        # Create rejection record for remaining quantity (without tray_id)
                        IP_Rejected_TrayScan.objects.create(
                            lot_id=lot_id,
                            rejected_tray_quantity=remaining_qty,
                            rejection_reason=reason_obj,
                            user=request.user,
                            rejected_tray_id='',  # Empty tray_id for uncovered quantity
                        )
                        print(f"✅ Created uncovered {reason_obj.rejection_reason} rejection: qty={remaining_qty}, no tray_id")
                        
                    except IP_Rejection_Table.DoesNotExist:
                        print(f"Warning: Rejection reason {reason_id} not found")
                        continue

            # Group rejections by reason_id for IP_Rejection_ReasonStore (from rejection_data)
            reason_groups = {}
            total_rejection_qty = 0

            for item in rejection_data:
                reason_id = item.get('reason_id')
                qty = int(item.get('qty', 0))
                if reason_id and qty > 0:
                    if reason_id not in reason_groups:
                        reason_groups[reason_id] = 0
                    reason_groups[reason_id] += qty
                    total_rejection_qty += qty

            # Save to IP_Rejection_ReasonStore (grouped by reason)
            if reason_groups:
                reason_ids = list(reason_groups.keys())
                reasons = IP_Rejection_Table.objects.filter(rejection_reason_id__in=reason_ids)
                reason_store = IP_Rejection_ReasonStore.objects.create(
                    lot_id=lot_id,
                    user=request.user,
                    total_rejection_quantity=total_rejection_qty,
                    batch_rejection=False
                )
                reason_store.rejection_reason.set(reasons)

            # Update TotalStockModel with correct calculations
            total_stock_obj.ip_onhold_picking = True
            total_stock_obj.few_cases_accepted_Ip_stock = True

            # Only reduce physical qty by NON-SHORTAGE rejections
            total_stock_obj.dp_physical_qty = available_qty - total_non_shortage_qty

            # Set last_process_date_time to now
            total_stock_obj.last_process_date_time = timezone.now()
            total_stock_obj.save(update_fields=[
                'few_cases_accepted_Ip_stock',
                'ip_onhold_picking',
                'dp_physical_qty',
                'last_process_date_time'
            ])

            # Return updated quantities for frontend
            response_data = {
                'success': True, 
                'message': 'Tray rejections saved successfully.',
                'lot_qty': total_stock_obj.batch_id.total_batch_quantity if total_stock_obj.batch_id else total_stock_obj.total_stock,
                'physical_qty': total_stock_obj.dp_physical_qty,
                'total_rejection_qty': total_rejection_qty,
                'shortage_qty': shortage_qty,
                'non_shortage_qty': total_non_shortage_qty,
                'tray_scans_processed': len(tray_scans),
                'tray_capacity_used': tray_capacity,
                'tray_distribution_used': tray_distribution,
                'logic_version': 'corrected_all_trays_with_quantity'
            }

            print(f"✅ Response data: {response_data}")
            return Response(response_data)

        except Exception as e:
            print(f"Error in TrayRejectionAPIView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)
        
# ==========================================
# SIMPLIFIED TRAY VALIDATION - SINGLE VIEW
@require_GET
def reject_check_tray_id_simple(request):
    """
    Enhanced tray validation: Check if existing tray rejection can accommodate remaining pieces
    """
    tray_id = request.GET.get('tray_id', '')
    current_lot_id = request.GET.get('lot_id', '')
    rejection_qty = int(request.GET.get('rejection_qty', 0))
    
    # ✅ NEW: Get current session allocations from frontend
    current_session_allocations_str = request.GET.get('current_session_allocations', '[]')
    
    print(f"[Simple Validation] tray_id: {tray_id}, lot_id: {current_lot_id}, qty: {rejection_qty}")
    print(f"[Simple Validation] Current session allocations: {current_session_allocations_str}")

    try:
        # Parse current session allocations
        import json
        try:
            current_session_allocations = json.loads(current_session_allocations_str)
        except:
            current_session_allocations = []
        
        # Get tray object
        from modelmasterapp.models import TrayId
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        
        if not tray_obj:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Tray ID not found',
                'status_message': 'Not Found'
            })

        # Basic validations
        if not getattr(tray_obj, 'IP_tray_verified', False):
            if not getattr(tray_obj, 'new_tray', False):
                return JsonResponse({
                    'exists': False,
                    'valid_for_rejection': False,
                    'error': 'Tray not verified',
                    'status_message': 'Not Verified'
                })

        # Check if already rejected
        if tray_obj.rejected_tray:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Already rejected',
                'status_message': 'Already Rejected'
            })

        # Get tray properties
        is_new_tray = getattr(tray_obj, 'new_tray', False)
        
        # ✅ NEW TRAY: Always allow (any quantity)
        if is_new_tray:
            return JsonResponse({
                'exists': True,
                'valid_for_rejection': True,
                'status_message': 'New Tray Available',
                'validation_type': 'new_tray'
            })

        # ✅ EXISTING TRAY: Check lot assignment
        if tray_obj.lot_id:
            if str(tray_obj.lot_id).strip() != str(current_lot_id).strip():
                return JsonResponse({
                    'exists': False,
                    'valid_for_rejection': False,
                    'error': 'Different lot',
                    'status_message': 'Different Lot'
                })
        else:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Invalid tray state',
                'status_message': 'Invalid State'
            })

        # ✅ ENHANCED: Apply current session allocations to get updated available quantities
        available_tray_quantities, actual_free_space = get_available_quantities_with_session_allocations(
            current_lot_id, current_session_allocations
        )

        original_capacities = get_tray_capacities_for_lot(current_lot_id)
        total_current_qty = sum(available_tray_quantities)
        
        print(f"[Simple Validation] Available tray quantities (with session): {available_tray_quantities}")
        print(f"[Simple Validation] Total current qty: {total_current_qty}")
        print(f"[Simple Validation] ACTUAL free space: {actual_free_space}")
        print(f"[Simple Validation] Rejection qty: {rejection_qty}")

        # Check if rejection is possible with existing trays
        if rejection_qty <= total_current_qty:
            # ✅ ENHANCED: Check if specific tray can be used for rejection
            can_use_existing_tray = False
            valid_tray_info = []
            
            for i, tray_qty in enumerate(available_tray_quantities):
                if tray_qty >= rejection_qty:
                    # This tray has enough quantity
                    remaining_after_rejection = tray_qty - rejection_qty
                    
                    # Calculate free space in OTHER trays
                    free_space_in_other_trays = 0
                    for j, other_qty in enumerate(available_tray_quantities):
                        if i != j and j < len(original_capacities):
                            capacity = original_capacities[j] if j < len(original_capacities) else 12
                            free_space_in_other_trays += max(0, capacity - other_qty)
                    
                    print(f"[Simple Validation] Tray {i+1}: qty={tray_qty}, remaining_after={remaining_after_rejection}, free_space_in_others={free_space_in_other_trays}")
                    
                    if remaining_after_rejection <= free_space_in_other_trays:
                        can_use_existing_tray = True
                        valid_tray_info.append(f"Tray{i+1}({tray_qty})")
                        
            if can_use_existing_tray:
                return JsonResponse({
                    'exists': True,
                    'valid_for_rejection': True,
                    'status_message': f'Available (can rearrange)',
                    'validation_type': 'existing_rearrangeable',
                    'available_quantities': available_tray_quantities,
                    'total_current': total_current_qty,
                    'actual_free_space': actual_free_space,
                    'valid_trays': valid_tray_info
                })
            else:
                # No existing tray can accommodate the remaining pieces
                return JsonResponse({
                    'exists': False,
                    'valid_for_rejection': False,
                    'error': 'Insufficient free space for rearrangement',
                    'status_message': f'Need NEW tray (insufficient rearrange space)',
                    'validation_type': 'existing_no_space',
                    'available_quantities': available_tray_quantities,
                    'actual_free_space': actual_free_space
                })
        else:
            # Rejection quantity exceeds total available
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Insufficient total quantity',
                'status_message': f'Need NEW tray (have {total_current_qty}, need {rejection_qty})',
                'validation_type': 'existing_insufficient',
                'available_quantities': available_tray_quantities,
                'total_current': total_current_qty
            })

    except Exception as e:
        print(f"[Simple Validation] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'exists': False,
            'valid_for_rejection': False,
            'error': 'System error',
            'status_message': 'System Error'
        })


def get_available_quantities_with_session_allocations(lot_id, current_session_allocations):
    """
    Calculate available tray quantities and ACTUAL free space
    """
    try:
        # Get original distribution and track free space separately
        original_distribution = get_original_tray_distribution(lot_id)
        original_capacities = get_tray_capacities_for_lot(lot_id)
        
        available_quantities = original_distribution.copy()
        new_tray_usage_count = 0  # Track NEW tray usage for free space calculation
        
        print(f"[Session Validation] Starting with: {available_quantities}")
        
        # First, apply saved rejections
        from modelmasterapp.models import IP_Rejected_TrayScan
        saved_rejections = IP_Rejected_TrayScan.objects.filter(lot_id=lot_id).order_by('id')
        
        for rejection in saved_rejections:
            rejected_qty = rejection.rejected_tray_quantity or 0
            tray_id = rejection.rejected_tray_id
            
            if rejected_qty <= 0:
                continue
                
            if tray_id and is_new_tray_by_id(tray_id):
                # NEW tray creates actual free space
                new_tray_usage_count += 1
                available_quantities = reduce_quantities_optimally(available_quantities, rejected_qty, is_new_tray=True)
                print(f"[Session Validation] NEW tray saved rejection: freed up {rejected_qty} space")
            else:
                # EXISTING tray just consumes available quantities
                available_quantities = reduce_quantities_optimally(available_quantities, rejected_qty, is_new_tray=False)
                print(f"[Session Validation] EXISTING tray saved rejection: removed tray")
        
        # Then, apply current session allocations
        for allocation in current_session_allocations:
            try:
                reason_text = allocation.get('reason_text', '')
                qty = int(allocation.get('qty', 0))
                tray_ids = allocation.get('tray_ids', [])
                
                if qty <= 0 or reason_text.upper() == 'SHORTAGE':
                    continue
                
                # ✅ FIXED: Check if NEW tray was used by looking at tray_ids
                is_new_tray_used = False
                if tray_ids:
                    for tray_id in tray_ids:
                        if tray_id and is_new_tray_by_id(tray_id):
                            is_new_tray_used = True
                            break
                
                if is_new_tray_used:
                    new_tray_usage_count += 1
                    available_quantities = reduce_quantities_optimally(available_quantities, qty, is_new_tray=True)
                    print(f"[Session Validation] NEW tray session: freed up {qty} space using tray {tray_ids}")
                else:
                    available_quantities = reduce_quantities_optimally(available_quantities, qty, is_new_tray=False)
                    print(f"[Session Validation] EXISTING tray session: removed tray")
            except Exception as e:
                print(f"[Session Validation] Error processing allocation: {e}")
                continue
        
        # ✅ FIXED: Calculate ACTUAL current free space
        actual_free_space = 0
        if len(available_quantities) <= len(original_capacities):
            for i, qty in enumerate(available_quantities):
                if i < len(original_capacities):
                    capacity = original_capacities[i]
                    actual_free_space += max(0, capacity - qty)
        
        # Calculate totals
        total_available = sum(available_quantities)
        total_capacity = sum(original_capacities[:len(available_quantities)])  # Only count current trays
        
        print(f"[Session Validation] FINAL:")
        print(f"  Available quantities: {available_quantities}")
        print(f"  Total available: {total_available}")
        print(f"  Total capacity of current trays: {total_capacity}")
        print(f"  ACTUAL free space in current trays: {actual_free_space}")
        print(f"  NEW tray usage count: {new_tray_usage_count}")
        
        return available_quantities, actual_free_space
        
    except Exception as e:
        print(f"[Session Validation] Error: {e}")
        return get_original_tray_distribution(lot_id), 0

def reduce_quantities_optimally(available_quantities, qty_to_reduce, is_new_tray=True):
    quantities = available_quantities.copy()
    remaining = qty_to_reduce

    if is_new_tray:
        # ✅ FIXED: NEW tray usage should FREE UP space from existing trays
        # This simulates moving pieces from existing trays to the new tray
        print(f"[reduce_quantities_optimally] NEW tray: freeing up {qty_to_reduce} space")
        
        # Free up space from smallest trays first (to create empty trays)
        sorted_indices = sorted(range(len(quantities)), key=lambda i: quantities[i])
        for i in sorted_indices:
            if remaining <= 0:
                break
            current_qty = quantities[i]
            if current_qty >= remaining:
                quantities[i] = current_qty - remaining
                print(f"  Freed {remaining} from tray {i}, new qty: {quantities[i]}")
                remaining = 0
            elif current_qty > 0:
                remaining -= current_qty
                print(f"  Freed entire tray {i}: {current_qty}")
                quantities[i] = 0
        
        return quantities
    else:
        # EXISTING tray: consume rejection quantity AND remove one tray entirely
        total_available = sum(quantities)
        if total_available < qty_to_reduce:
            return quantities  # Not enough quantity available
        
        print(f"[reduce_quantities_optimally] EXISTING tray: consuming {qty_to_reduce} and removing one tray")
        
        # Step 1: First try to find exact match (if a tray has exactly the rejection qty)
        for i, qty in enumerate(quantities):
            if qty == qty_to_reduce:
                result = quantities.copy()
                del result[i]  # Remove the exact match tray
                print(f"  Found exact match tray {i}, removed it")
                return result
        
        # Step 2: If no exact match, consume qty_to_reduce from available quantities
        temp_quantities = quantities.copy()
        remaining_to_consume = qty_to_reduce
        
        # Consume from trays in order
        for i in range(len(temp_quantities)):
            if remaining_to_consume <= 0:
                break
            current_qty = temp_quantities[i]
            consume_from_this_tray = min(remaining_to_consume, current_qty)
            temp_quantities[i] -= consume_from_this_tray
            remaining_to_consume -= consume_from_this_tray
            print(f"  Consumed {consume_from_this_tray} from tray {i}")
        
        # Step 3: Remove one tray entirely (prefer empty ones first, then smallest)
        # Remove empty tray first (if any)
        for i in range(len(temp_quantities)):
            if temp_quantities[i] == 0:
                del temp_quantities[i]
                print(f"  Removed empty tray {i}")
                return temp_quantities
        
        # If no empty tray, remove the smallest quantity tray
        if temp_quantities:
            min_qty = min(temp_quantities)
            for i in range(len(temp_quantities)):
                if temp_quantities[i] == min_qty:
                    del temp_quantities[i]
                    print(f"  Removed smallest tray {i} with qty {min_qty}")
                    return temp_quantities
        
        return temp_quantities

# ==========================================
# KEY HELPER FUNCTION
# ==========================================

def get_available_tray_quantities_for_lot(lot_id):
    """
    Get list of available tray quantities after considering previous rejections
    """
    try:
        # Get original tray distribution
        original_distribution = get_original_tray_distribution(lot_id)
        original_capacities = get_tray_capacities_for_lot(lot_id)  # Track original capacities
        
        print(f"[Available Quantities] Original distribution: {original_distribution}")
        print(f"[Available Quantities] Original capacities: {original_capacities}")
        
        # Get all previous rejections
        from modelmasterapp.models import IP_Rejected_TrayScan
        rejections = IP_Rejected_TrayScan.objects.filter(lot_id=lot_id).order_by('id')
        
        available_quantities = original_distribution.copy()
        
        for rejection in rejections:
            rejected_qty = rejection.rejected_tray_quantity or 0
            tray_id = rejection.rejected_tray_id
            
            if rejected_qty <= 0:
                continue
            
            print(f"[Available Quantities] Processing rejection: {rejected_qty} qty, tray: {tray_id}")
            
            # Check if NEW tray was used
            if tray_id and is_new_tray_by_id(tray_id):
                print(f"[Available Quantities] NEW tray used: {tray_id}, qty: {rejected_qty}")
                print(f"[Available Quantities] NEW tray usage FREES UP existing tray content")
                
                remaining_to_free = rejected_qty
                
                # ✅ FIXED: Use index-based approach without sorting to preserve order
                for i in range(len(available_quantities)):
                    if remaining_to_free <= 0:
                        break
                        
                    current_tray_qty = available_quantities[i]
                    
                    if current_tray_qty >= remaining_to_free:
                        # This tray can provide all remaining quantity
                        available_quantities[i] = current_tray_qty - remaining_to_free
                        print(f"[Available Quantities] Freed {remaining_to_free} from tray {i}, new qty: {available_quantities[i]}")
                        remaining_to_free = 0
                    elif current_tray_qty > 0:
                        # Free entire tray content
                        remaining_to_free -= current_tray_qty
                        print(f"[Available Quantities] Freed entire tray {i}: {current_tray_qty}")
                        available_quantities[i] = 0
                
                continue
            
            # EXISTING tray was used - reduce existing tray quantities
            remaining_to_consume = rejected_qty
            
            # ✅ FIXED: Use index-based approach to preserve positions
            for i in range(len(available_quantities)):
                if remaining_to_consume <= 0:
                    break
                    
                current_tray_qty = available_quantities[i]
                
                if current_tray_qty >= remaining_to_consume:
                    # This tray can handle the remaining quantity
                    available_quantities[i] = current_tray_qty - remaining_to_consume
                    print(f"[Available Quantities] Consumed {remaining_to_consume} from tray {i}, remaining: {available_quantities[i]}")
                    remaining_to_consume = 0
                elif current_tray_qty > 0:
                    # Consume entire tray and continue
                    remaining_to_consume -= current_tray_qty
                    print(f"[Available Quantities] Consumed entire tray {i}: {current_tray_qty}")
                    available_quantities[i] = 0
        
        # ✅ FIXED: Don't remove zeros - they represent freed capacity!
        # Just ensure non-negative values
        available_quantities = [max(0, qty) for qty in available_quantities]
        
        print(f"[Available Quantities] FINAL available quantities: {available_quantities}")
        return available_quantities
        
    except Exception as e:
        print(f"[Available Quantities] Error: {e}")
        return []

def get_original_tray_distribution(lot_id):
    """
    Get original tray quantity distribution for the lot
    Returns list like [6, 12, 12] representing individual tray capacities
    """
    try:
        print(f"[Original Distribution] Getting distribution for lot_id: {lot_id}")
        
        # Get TrayId records for this lot
        from modelmasterapp.models import TrayId
        tray_objects = TrayId.objects.filter(lot_id=lot_id).exclude(
            rejected_tray=True
        ).order_by('date')
        
        print(f"[Original Distribution] Found {tray_objects.count()} tray objects")
        
        if tray_objects.exists():
            # Use actual tray quantities from database
            quantities = []
            for tray in tray_objects:
                tray_qty = getattr(tray, 'tray_quantity', None)
                print(f"[Original Distribution] Tray {tray.tray_id}: quantity = {tray_qty}")
                if tray_qty and tray_qty > 0:
                    quantities.append(tray_qty)
            
            if quantities:
                print(f"[Original Distribution] From TrayId objects: {quantities}")
                return quantities
        
        # Fallback: Calculate from total quantity and standard capacity
        from modelmasterapp.models import TotalStockModel
        total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if not total_stock:
            print(f"[Original Distribution] No TotalStockModel found for lot_id: {lot_id}")
            return []
        
        total_qty = get_total_quantity_for_lot(total_stock)
        tray_capacity = get_tray_capacity_for_lot(lot_id)  # ✅ Pass lot_id instead of total_stock
        
        print(f"[Original Distribution] Fallback calculation - total_qty: {total_qty}, tray_capacity: {tray_capacity}")
        
        if not total_qty or not tray_capacity:
            return []
        
        # Calculate distribution: remainder first, then full trays
        remainder = total_qty % tray_capacity
        full_trays = total_qty // tray_capacity
        
        distribution = []
        if remainder > 0:
            distribution.append(remainder)
        
        for _ in range(full_trays):
            distribution.append(tray_capacity)
        
        print(f"[Original Distribution] Calculated: {distribution} (total: {total_qty}, capacity: {tray_capacity})")
        return distribution
        
    except Exception as e:
        print(f"[Original Distribution] Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def is_new_tray_by_id(tray_id):
    """
    Check if a tray ID represents a NEW tray.
    Returns True if TrayId.new_tray is True or lot_id is None/empty.
    """
    if not tray_id:
        return False

    try:
        from modelmasterapp.models import TrayId
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()

        if tray_obj:
            # Use only the DB fields for logic
            return getattr(tray_obj, 'new_tray', False) or not tray_obj.lot_id

        # If tray not found, treat as not new
        return False

    except Exception as e:
        print(f"[is_new_tray_by_id] Error: {e}")
        return False

def get_total_quantity_for_lot(total_stock):
    """Get total quantity for a lot"""
    try:
        print(f"[get_total_quantity_for_lot] Processing total_stock object")
        
        if hasattr(total_stock, 'dp_physical_qty') and total_stock.dp_physical_qty:
            print(f"[get_total_quantity_for_lot] Using dp_physical_qty: {total_stock.dp_physical_qty}")
            return total_stock.dp_physical_qty
            
        if hasattr(total_stock, 'total_stock') and total_stock.total_stock:
            print(f"[get_total_quantity_for_lot] Using total_stock: {total_stock.total_stock}")
            return total_stock.total_stock
            
        if hasattr(total_stock, 'batch_id') and total_stock.batch_id:
            if hasattr(total_stock.batch_id, 'total_batch_quantity'):
                print(f"[get_total_quantity_for_lot] Using batch total_batch_quantity: {total_stock.batch_id.total_batch_quantity}")
                return total_stock.batch_id.total_batch_quantity
                
        print(f"[get_total_quantity_for_lot] No valid quantity found, returning 0")
        return 0
    except Exception as e:
        print(f"[get_total_quantity_for_lot] Error: {e}")
        return 0


def get_tray_capacities_for_lot(lot_id):
    """
    Get all tray capacities for a lot (in case different trays have different capacities)
    Returns list of capacities corresponding to each tray
    """
    try:
        print(f"[get_tray_capacities_for_lot] Getting all capacities for lot_id: {lot_id}")
        
        from modelmasterapp.models import TrayId
        tray_objects = TrayId.objects.filter(lot_id=lot_id).exclude(rejected_tray=True).order_by('date')
        
        capacities = []
        for tray in tray_objects:
            capacity = getattr(tray, 'tray_capacity', None)
            if capacity and capacity > 0:
                capacities.append(capacity)
            else:
                # Fallback to standard capacity if not set
                standard_capacity = get_tray_capacity_for_lot(lot_id)
                capacities.append(standard_capacity)
                
        print(f"[get_tray_capacities_for_lot] Capacities: {capacities}")
        return capacities
        
    except Exception as e:
        print(f"[get_tray_capacities_for_lot] Error: {e}")
        return []


def get_tray_capacity_for_lot(lot_id):
    """
    Get tray capacity for a lot from TrayId table (DYNAMIC)
    Returns the tray capacity used for this specific lot
    """
    try:
        print(f"[get_tray_capacity_for_lot] Getting capacity for lot_id: {lot_id}")
        
        # Get tray capacity from TrayId table for this specific lot
        from modelmasterapp.models import TrayId
        tray_objects = TrayId.objects.filter(lot_id=lot_id).exclude(rejected_tray=True)
        
        if tray_objects.exists():
            # Get tray_capacity from first tray (all trays in same lot should have same capacity)
            first_tray = tray_objects.first()
            tray_capacity = getattr(first_tray, 'tray_capacity', None)
            
            if tray_capacity and tray_capacity > 0:
                print(f"[get_tray_capacity_for_lot] Found tray_capacity from TrayId: {tray_capacity}")
                return tray_capacity
                
            # If tray_capacity is not set, check all trays for a valid capacity
            for tray in tray_objects:
                capacity = getattr(tray, 'tray_capacity', None)
                if capacity and capacity > 0:
                    print(f"[get_tray_capacity_for_lot] Found valid tray_capacity: {capacity}")
                    return capacity
        
        # Fallback: Get from TotalStockModel > batch_id
        from modelmasterapp.models import TotalStockModel
        total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if total_stock and hasattr(total_stock, 'batch_id') and total_stock.batch_id:
            batch_capacity = getattr(total_stock.batch_id, 'tray_capacity', None)
            if batch_capacity and batch_capacity > 0:
                print(f"[get_tray_capacity_for_lot] Using batch tray_capacity: {batch_capacity}")
                return batch_capacity
                
        print(f"[get_tray_capacity_for_lot] Using default capacity: 12")
        return 12  # Final fallback
        
    except Exception as e:
        print(f"[get_tray_capacity_for_lot] Error: {e}")
        import traceback
        traceback.print_exc()
        return 12
#===========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unscanned_trays(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        trays = TrayId.objects.filter(lot_id=lot_id, scanned=False)
        data = [
            {
                'tray_id': tray.tray_id,
                'tray_quantity': tray.tray_quantity,
            }
            for tray in trays
        ]
        return Response({'success': True, 'trays': data})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
    
    
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class VerifyTopTrayQtyAPIView(APIView):
    """
    API View to verify top tray quantity in Input Screening
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            verified_tray_qty = data.get('verified_tray_qty')
            original_tray_qty = data.get('original_tray_qty', 0)
            
            if not lot_id or verified_tray_qty is None:
                return JsonResponse({
                    'success': False, 
                    'error': 'lot_id and verified_tray_qty are required'
                }, status=400)
            
            try:
                verified_tray_qty = int(verified_tray_qty)
                original_tray_qty = int(original_tray_qty)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'error': 'verified_tray_qty must be a valid integer'
                }, status=400)
            
            if verified_tray_qty <= 0:
                return JsonResponse({
                    'success': False, 
                    'error': 'verified_tray_qty must be greater than 0'
                }, status=400)
            
            if verified_tray_qty > original_tray_qty:
                return JsonResponse({
                    'success': False, 
                    'error': f'verified_tray_qty cannot exceed original quantity ({original_tray_qty})'
                }, status=400)
            
            # Find the TotalStockModel record by lot_id
            try:
                total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            except TotalStockModel.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Stock record not found for the provided lot_id'
                }, status=404)
            
            # Check if already verified
            if total_stock.ip_top_tray_qty_verified:
                return JsonResponse({
                    'success': False, 
                    'error': 'Top tray quantity is already verified'
                }, status=400)
            
            # Calculate modification amount (difference)
            modification_amount = original_tray_qty - verified_tray_qty
            
            # Update the verification fields
            total_stock.ip_top_tray_qty_verified = True
            total_stock.ip_verified_tray_qty = verified_tray_qty
            # FIX: Store the verified quantity, not the modification amount
            total_stock.ip_top_tray_qty_modify = verified_tray_qty
            
            # Save the changes
            total_stock.save(update_fields=[
                'ip_top_tray_qty_verified', 
                'ip_verified_tray_qty', 
                'ip_top_tray_qty_modify'
            ])
            
            return JsonResponse({
                'success': True, 
                'message': 'Top tray quantity verified successfully',
                'verified_qty': verified_tray_qty,
                'modification_amount': modification_amount,
                'lot_id': lot_id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            # Log the error for debugging
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False, 
                'error': f'Unexpected error occurred: {str(e)}'
            }, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class IPTrayValidateAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id_input = str(data.get('batch_id')).strip()
            tray_id = str(data.get('tray_id')).strip()
            tray_position = data.get('tray_position')  # Add this parameter
            lot_id = data.get('lot_id')  # Add this parameter
            
            print(f"[TrayValidateAPIView] User entered: batch_id={batch_id_input}, tray_id={tray_id}, position={tray_position}")

            # Try to match batch_id by code part (after last '-')
            trays = TrayId.objects.filter(batch_id__batch_id__icontains=batch_id_input)
            exists = trays.filter(tray_id=tray_id).exists()
            
            # Save verification status
            if lot_id and tray_position:
                verification_status = 'pass' if exists else 'fail'
                
                # Update or create verification record
                obj, created = IP_TrayVerificationStatus.objects.update_or_create(
                    lot_id=lot_id,
                    tray_position=tray_position,
                    defaults={
                        'tray_id': tray_id,
                        'is_verified': True,
                        'verification_status': verification_status,
                        'verified_by': request.user
                    }
                )
                # ✅ Update TrayId.ip_tray_verified if verified
                if obj.is_verified and obj.tray_id:
                    TrayId.objects.filter(tray_id=obj.tray_id).update(IP_tray_verified=True)
            
                
                print(f"Saved verification: Position {tray_position}, Status: {verification_status}")

            return JsonResponse({
                'success': True, 
                'exists': exists,
                'verification_status': 'pass' if exists else 'fail'
            })
        except Exception as e:
            print(f"[TrayValidateAPIView] Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tray_verification_status(request):
    """Get existing tray verification status for a lot"""
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        verification_records = IP_TrayVerificationStatus.objects.filter(lot_id=lot_id)
        
        verification_data = {}
        for record in verification_records:
            verification_data[record.tray_position] = {
                'tray_id': record.tray_id,
                'is_verified': record.is_verified,
                'verification_status': record.verification_status,
                'verified_at': record.verified_at.isoformat() if record.verified_at else None
            }
            
        
        return Response({
            'success': True,
            'verification_data': verification_data
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_tray_verification_for_lot(request):
    """
    Reset all tray verifications for a given lot_id.
    Deletes all IP_TrayVerificationStatus records for the lot,
    sets IP_tray_verified=False for all related TrayId records,
    and resets TotalStockModel fields for this lot.
    POST: { "lot_id": "..." }
    """
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
        lot_id = data.get('lot_id')
        if not lot_id:
            return JsonResponse({'success': False, 'error': 'Missing lot_id'}, status=400)

        # Get all verified tray_ids for this lot
        verified_records = IP_TrayVerificationStatus.objects.filter(lot_id=lot_id)
        tray_ids = list(verified_records.values_list('tray_id', flat=True))

        # Delete all verification records for this lot
        deleted_count, _ = verified_records.delete()

        # Set IP_tray_verified=False for all those tray_ids in this lot
        if tray_ids:
            TrayId.objects.filter(tray_id__in=tray_ids, lot_id=lot_id).update(IP_tray_verified=False)

        # --- NEW: Reset TotalStockModel fields for this lot ---
        total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if total_stock:
            total_stock.dp_physical_qty = 0
            total_stock.dp_physical_qty_edited = False
            total_stock.ip_onhold_picking = False
            total_stock.save(update_fields=[
                'dp_physical_qty',
                'dp_physical_qty_edited',
                'ip_onhold_picking'
            ])

        return JsonResponse({
            'success': True,
            'deleted_verifications': deleted_count,
            'updated_trays': len(tray_ids)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@method_decorator(csrf_exempt, name='dispatch')
class IPCompletedTrayIdListAPIView(APIView):
    def get(self, request):
        batch_id = request.GET.get('batch_id')
        if not batch_id:
            return JsonResponse({'success': False, 'error': 'Missing batch_id'}, status=400)

        try:
            # Get existing tray data from database - ORDER BY POSITION/TOP_TRAY
            existing_trays = TrayId.objects.filter(
                batch_id__batch_id=batch_id,
                rejected_tray=False,
                delink_tray=False
            ).order_by('-top_tray', 'id')  # top_tray first, then by id
            
            data = []
            for idx, tray in enumerate(existing_trays):
                data.append({
                    's_no': idx + 1,
                    'tray_id': tray.tray_id or '',  # ✅ ALWAYS include tray_id from DB
                    'tray_quantity': tray.tray_quantity or 0,
                    'is_top_tray': tray.top_tray,
                    'exists_in_db': True,
                    'IP_tray_verified': getattr(tray, 'IP_tray_verified', False)  # ✅ Include verification status
                })
            
            return JsonResponse({'success': True, 'trays': data})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
   

# ✅ UPDATED: Modified get_accepted_tray_scan_data function for single top tray calculation
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accepted_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if not stock:
            return Response({'success': False, 'error': 'Stock not found'}, status=404)
        
        model_no = stock.model_stock_no.model_no if stock.model_stock_no else ""
        tray_capacity = stock.batch_id.tray_capacity if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity') else 10

        # Get rejection qty for display/logging only
        reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
        total_rejection_qty = reason_store.total_rejection_quantity if reason_store else 0

        # 🔥 FIX: Calculate available_qty as total_stock - total_rejection_qty
        available_qty = (stock.total_stock or 0) - (total_rejection_qty or 0)
        print(f"📐 [get_accepted_tray_scan_data] available_qty = {available_qty}")

        if available_qty <= 0:
            print(f"❌ [get_accepted_tray_scan_data] ERROR: available_qty is {available_qty}")
            return Response({
                'success': False, 
                'error': f'Available quantity is {available_qty}. Cannot proceed with accepted tray scan.'
            }, status=400)

        # Calculate top tray quantity using available_qty
        full_trays = available_qty // tray_capacity
        top_tray_qty = available_qty % tray_capacity

        # If remainder is 0, it means we need full tray capacity for top tray
        if top_tray_qty == 0 and available_qty > 0:
            top_tray_qty = tray_capacity

        print(f"📊 [get_accepted_tray_scan_data] Tray calculation: {available_qty} qty = {full_trays} full trays + {top_tray_qty} top tray")

        # Check for existing draft data
        has_draft = IP_Accepted_TrayID_Store.objects.filter(lot_id=lot_id, is_draft=True).exists()
        draft_tray_id = ""
        delink_tray_id = ""
        delink_tray_qty = None
        
        if has_draft:
            draft_record = IP_Accepted_TrayID_Store.objects.filter(
                lot_id=lot_id, 
                is_draft=True
            ).first()
            if draft_record:
                draft_tray_id = draft_record.top_tray_id
                delink_tray_id = draft_record.delink_tray_id
                delink_tray_qty = draft_record.delink_tray_qty
        
        top_tray_verified = stock.ip_top_tray_qty_verified or False
        verified_tray_qty = stock.ip_verified_tray_qty or 0
        
        return Response({
            'success': True,
            'model_no': model_no,
            'tray_capacity': tray_capacity,
            'dp_physical_qty': available_qty,  # For reference
            'available_qty': available_qty,    # Primary quantity to use
            'total_rejection_qty': total_rejection_qty,  # For display/info only
            'top_tray_qty': top_tray_qty,      # Calculated from available_qty
            'has_draft': has_draft,
            'draft_tray_id': draft_tray_id,
            'delink_tray_id': delink_tray_id,
            'delink_tray_qty': delink_tray_qty,
            'top_tray_verified': top_tray_verified,
            'verified_tray_qty': verified_tray_qty,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)
 
# ✅ NEW: Updated check_tray_id function with proper validation for top tray
@require_GET
def check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    lot_id = request.GET.get('lot_id', '')

    try:
        # Get the tray object if it exists
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        
        if not tray_obj:
            return JsonResponse({
                'exists': False,
                'error': 'Tray ID not found',
                'already_rejected': False,
                'not_in_same_lot': False
            })
        # ✅ ADD THIS: Only allow if IP_tray_verified is True
        if not getattr(tray_obj, 'IP_tray_verified', False):
            return JsonResponse({
                'exists': False,
                'error': 'Tray id is not verified',
                'tray_status': 'not_verified'
            })
        
        # ✅ VALIDATION 1: Check if tray belongs to same lot
        same_lot = str(tray_obj.lot_id) == str(lot_id) if tray_obj.lot_id else False
        
        # ✅ VALIDATION 2: Check if tray is already rejected
        already_rejected = tray_obj.rejected_tray or False
        
        # ✅ VALIDATION 3: Check if tray is already used in IP_Rejected_TrayScan
        already_used_in_rejection = IP_Rejected_TrayScan.objects.filter(
            lot_id=lot_id,
            rejected_tray_id=tray_id
        ).exists()
        
        # ✅ VALIDATION 4: Check if tray is already used in IP_Accepted_TrayID_Store
        already_used_in_acceptance = IP_Accepted_TrayID_Store.objects.filter(
            lot_id=lot_id,
            top_tray_id=tray_id
        ).exists()
        
        # Determine if tray is valid
        is_valid = (
            tray_obj and 
            same_lot and 
            not already_rejected and 
            not already_used_in_rejection and
            not already_used_in_acceptance
        )
        
        return JsonResponse({
            'exists': is_valid,
            'already_rejected': already_rejected or already_used_in_rejection,
            'not_in_same_lot': not same_lot,
            'already_used_in_acceptance': already_used_in_acceptance,
            'tray_status': 'valid' if is_valid else 'invalid'
        })
        
    except Exception as e:
        return JsonResponse({
            'exists': False,
            'error': 'System error',
            'already_rejected': False,
            'not_in_same_lot': False
        })


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_single_top_tray_scan(request):
    try:
        data = request.data
        lot_id = data.get('lot_id')
        tray_id = data.get('tray_id')
        tray_qty = data.get('tray_qty')
        draft_save = data.get('draft_save', False)
        delink_trays = data.get('delink_trays', [])  # ✅ NEW: Get delink tray data
        user = request.user

        if not lot_id or not tray_id or not tray_qty:
            return Response({
                'success': False, 
                'error': 'Missing lot_id, tray_id, or tray_qty'
            }, status=400)

        # ✅ UPDATED: Validation - Prevent same tray ID for delink and top tray
        delink_tray_ids = [delink['tray_id'] for delink in delink_trays if delink.get('tray_id')]
        if tray_id in delink_tray_ids:
            return Response({
                'success': False,
                'error': 'To be delink tray should not be as Top tray'
            }, status=400)

        # Validate top tray_id exists and is valid
        top_tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        if not top_tray_obj:
            return Response({
                'success': False,
                'error': f'Top tray ID "{tray_id}" does not exist.'
            }, status=400)
        
        # Validate top tray belongs to same lot
        if str(top_tray_obj.lot_id) != str(lot_id):
            return Response({
                'success': False,
                'error': f'Top tray ID "{tray_id}" does not belong to this lot.'
            }, status=400)
        
        # Validate top tray is not rejected
        if top_tray_obj.rejected_tray:
            return Response({
                'success': False,
                'error': f'Top tray ID "{tray_id}" is already rejected.'
            }, status=400)

        # ✅ NEW: Validate all delink trays (only if not draft and delink_trays exist)
        if not draft_save and delink_trays:
            for delink in delink_trays:
                delink_tray_id = delink.get('tray_id')
                if not delink_tray_id:
                    continue
                    
                delink_tray_obj = TrayId.objects.filter(tray_id=delink_tray_id).first()
                if not delink_tray_obj:
                    return Response({
                        'success': False,
                        'error': f'Delink tray ID "{delink_tray_id}" does not exist.'
                    }, status=400)
                
                # Validate delink tray belongs to same lot
                if str(delink_tray_obj.lot_id) != str(lot_id):
                    return Response({
                        'success': False,
                        'error': f'Delink tray ID "{delink_tray_id}" does not belong to this lot.'
                    }, status=400)
                
                # Validate delink tray is not rejected
                if delink_tray_obj.rejected_tray:
                    return Response({
                        'success': False,
                        'error': f'Delink tray ID "{delink_tray_id}" is already rejected.'
                    }, status=400)

         # Remove existing records for this lot (to avoid duplicates)
        IP_Accepted_TrayID_Store.objects.filter(lot_id=lot_id).delete()

        # Prepare delink tray info for saving (only first delink tray for now)
        delink_tray_id = delink_tray_ids[0] if delink_tray_ids else None
        delink_tray_qty = None
        if delink_trays and delink_trays[0].get('tray_qty'):
            delink_tray_qty = delink_trays[0]['tray_qty']

        # Save new record
        IP_Accepted_TrayID_Store.objects.create(
            lot_id=lot_id,
            top_tray_id=tray_id,
            top_tray_qty=tray_qty,
            user=user,
            is_draft=draft_save,
            is_save=not draft_save,
            delink_tray_id=delink_tray_id,
            delink_tray_qty=delink_tray_qty
        )

        # ✅ NEW: Handle TrayId table updates only for final submit (not draft)
        delink_count = 0
        if not draft_save:
            # Update top tray in TrayId table
            top_tray_obj.ip_top_tray = True
            top_tray_obj.ip_top_tray_qty = tray_qty
            top_tray_obj.save(update_fields=['ip_top_tray', 'ip_top_tray_qty'])
            
            # Update delink trays in TrayId table
            for delink in delink_trays:
                delink_tray_id = delink.get('tray_id')
                if delink_tray_id:
                    delink_tray_obj = TrayId.objects.filter(tray_id=delink_tray_id).first()
                    if delink_tray_obj:
                        delink_tray_obj.delink_tray = True
                        delink_tray_obj.lot_id = None
                        delink_tray_obj.batch_id = None
                        delink_tray_obj.scanned = False
                        delink_tray_obj.IP_tray_verified = False
                        delink_tray_obj.top_tray = False
                        delink_tray_obj.save(update_fields=[
                            'delink_tray', 'lot_id', 'batch_id', 'scanned', 'IP_tray_verified', 'top_tray'
                        ])
                        delink_count += 1

        # Update TotalStockModel flags only if it's a final save (not draft)
        if not draft_save:
            stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if stock:
                stock.accepted_tray_scan_status = True
                stock.next_process_module = "Brass QC"
                stock.last_process_module = "Input Screening"
                stock.ip_onhold_picking = False
                stock.last_process_date_time = timezone.now()  # Set last_process_date_time to now
                stock.save(update_fields=[
                    'accepted_tray_scan_status', 
                    'next_process_module', 
                    'last_process_module', 
                    'ip_onhold_picking',
                    'last_process_date_time'
                ])

        # ✅ UPDATED: Enhanced response message
        if draft_save:
            message = 'Top tray scan saved as draft successfully.'
        else:
            message = f'Top tray scan completed successfully.'
            if delink_count > 0:
                message += f' {delink_count} tray(s) marked for delink.'

        return Response({
            'success': True, 
            'message': message,
            'delink_count': delink_count,
            'top_tray_id': tray_id,
            'is_draft': draft_save
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ip_get_rejected_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        rows = []
        for obj in IP_Rejected_TrayScan.objects.filter(lot_id=lot_id):
            rows.append({
                'tray_id': obj.rejected_tray_id,
                'qty': obj.rejected_tray_quantity,
                'reason': obj.rejection_reason.rejection_reason,
                'reason_id': obj.rejection_reason.rejection_reason_id,
            })
        return Response({'success': True, 'rows': rows})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Ip_check_accepted_tray_draft(request):
    """Check if draft data exists for accepted tray scan"""
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        has_draft = IP_Accepted_TrayID_Store.objects.filter(
            lot_id=lot_id, 
            is_draft=True
        ).exists()
        
        return Response({
            'success': True,
            'has_draft': has_draft
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

import pytz

class IS_Completed_Table(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_Completed_Table.html'
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        from django.utils import timezone
        from datetime import datetime, timedelta

        user = request.user
        
        # ✅ COPIED FROM DP: Use IST timezone
        tz = pytz.timezone("Asia/Kolkata")
        now_local = timezone.now().astimezone(tz)
        today = now_local.date()
        yesterday = today - timedelta(days=1)

        # ✅ COPIED FROM DP: Use created_at for date filtering
        # Get all related created_at values for completed batches
        completed_batches = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0,
        ).values_list('batch_id', flat=True)

        # ✅ COPIED FROM DP: Get min/max created_at from TotalStockModel
        created_at_qs = TotalStockModel.objects.filter(
            batch_id__batch_id__in=completed_batches
        )
        min_created_at = created_at_qs.order_by('created_at').values_list('created_at', flat=True).first()
        max_created_at = created_at_qs.order_by('-created_at').values_list('created_at', flat=True).first()

        # ✅ COPIED FROM DP: Always use current date in IST
        today = now_local.date()
        yesterday = today - timedelta(days=1)

        # ✅ COPIED FROM DP: Get date filter parameters from request
        from_date_str = request.GET.get('from_date')
        to_date_str = request.GET.get('to_date')

        # ✅ COPIED FROM DP: Calculate date range
        if from_date_str and to_date_str:
            try:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            except ValueError:
                from_date = yesterday
                to_date = today
        else:
            from_date = yesterday
            to_date = today

        # ✅ COPIED FROM DP: Convert dates to datetime objects for filtering
        from_datetime = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
        to_datetime = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))

        # ✅ COPIED FROM DP: Filter by created_at in TotalStockModel
        # Get batch_ids where created_at is in range
        batch_ids_in_range = list(
            TotalStockModel.objects.filter(
                created_at__range=(from_datetime, to_datetime)
            ).values_list('batch_id__batch_id', flat=True)
        )
       
        # Create subqueries for all fields
        last_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('last_process_module')[:1]

        ip_person_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_person_qty_verified')[:1]
        
        lot_id_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('lot_id')[:1]
        
        next_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('next_process_module')[:1]
        
        dp_physical_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty')[:1]
        
        dp_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty_edited')[:1]
        
        accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_Ip_stock')[:1]

        few_cases_accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('few_cases_accepted_Ip_stock')[:1]
        
        accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_tray_scan_status')[:1]
        
        IP_pick_remarks_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('IP_pick_remarks')[:1]
        
        rejected_ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('rejected_ip_stock')[:1]
        
        ip_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_onhold_picking')[:1]

        total_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('total_stock')[:1]

        wiping_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('wiping_status')[:1]
        
        # ✅ COPIED FROM DP: Add created_at subquery
        created_at_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('created_at')[:1]
        
        # 🔥 UPDATED: Build queryset with date filtering and existing filters
        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0,
            batch_id__in=batch_ids_in_range  # ✅ COPIED FROM DP: Use batch_ids_in_range

        ).annotate(
            last_process_module=Subquery(last_process_module_subquery),
            next_process_module=Subquery(next_process_module_subquery),
            ip_person_qty_verified=Subquery(ip_person_qty_verified_subquery),
            dp_physical_qty=Subquery(dp_physical_qty_subquery),
            dp_physical_qty_edited=Subquery(dp_physical_qty_edited_subquery),
            accepted_Ip_stock=Subquery(accepted_Ip_stock_subquery),
            few_cases_accepted_Ip_stock=Subquery(few_cases_accepted_Ip_stock_subquery),
            IP_pick_remarks=Subquery(IP_pick_remarks_subquery),
            accepted_tray_scan_status=Subquery(accepted_tray_scan_status_subquery),
            rejected_ip_stock=Subquery(rejected_ip_stock_subquery),
            ip_onhold_picking=Subquery(ip_onhold_picking_subquery),
            total_stock=Subquery(total_stock_subquery),
            total_ip_accepted_quantity=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('total_IP_accpeted_quantity')[:1]
            ), 
                      
            stock_lot_id=Subquery(lot_id_subquery),
            wiping_status=Subquery(wiping_status_subquery),
            
            # ✅ COPIED FROM DP: Use created_at instead of last_process_date_time
            created_at=Subquery(created_at_subquery),
            last_process_date_time=Subquery(TotalStockModel.objects.filter(
                batch_id=OuterRef('pk')
            ).values('last_process_date_time')[:1]),
            
        ).filter(
            Q(accepted_Ip_stock=True) |
            Q(rejected_ip_stock=True) |
            Q(few_cases_accepted_Ip_stock=True) & Q(ip_onhold_picking=False)
        ).order_by('-last_process_date_time')  # ✅ COPIED FROM DP: Order by created_at

        print(f"📊 Found {queryset.count()} records in date range {from_date} to {to_date}")
        
        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(page_number)

        master_data = list(page_obj.object_list.values(
            'batch_id',
            'date_time',
            'model_stock_no__model_no',
            'plating_color',
            'polish_finish',
            'version__version_name',
            'vendor_internal',
            'location__location_name',
            'no_of_trays',
            'tray_type',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'stock_lot_id',
            'ip_person_qty_verified',
            'dp_physical_qty',
            'dp_physical_qty_edited',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'IP_pick_remarks',
            'rejected_ip_stock',
            'ip_onhold_picking',
            'total_batch_quantity',
            'total_ip_accepted_quantity',
            'total_stock',
            'wiping_status',
            'last_process_date_time',
            'created_at',  # ✅ COPIED FROM DP: Add created_at to values
            'plating_stk_no',
            'polishing_stk_no',
            'category',
            'version__version_internal',
        ))

        # MANUAL APPROACH: Add rejection quantities manually
        # Since the subquery approach isn't working, let's add it manually
        for data in master_data:
            stock_lot_id = data.get('stock_lot_id')
            
            # Get rejection quantity from IP_Rejection_ReasonStore only
            if stock_lot_id:
                try:
                    rejection_qty = 0
                    rejection_record = IP_Rejection_ReasonStore.objects.filter(
                        lot_id=stock_lot_id
                    ).first()
                    
                    if rejection_record and rejection_record.total_rejection_quantity:
                        rejection_qty = rejection_record.total_rejection_quantity
                        print(f"Found rejection for {stock_lot_id}: {rejection_record.total_rejection_quantity}")
                    
                    # Set rejection quantity (only from IP_Rejection_ReasonStore)
                    data['ip_rejection_total_qty'] = rejection_qty
                    print(f"Set rejection qty for {stock_lot_id}: {rejection_qty}")
                                
                except Exception as e:
                    print(f"Error getting rejection for {stock_lot_id}: {str(e)}")
                    data['ip_rejection_total_qty'] = 0
            else:
                data['ip_rejection_total_qty'] = 0
                print(f"No stock_lot_id for batch {data.get('batch_id')}")
            
            # Rest of your existing logic
            total_stock = data.get('total_stock', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(total_stock / tray_capacity)
            else:
                data['no_of_trays'] = 0
                
            mmc = ModelMasterCreation.objects.filter(batch_id=data['batch_id']).first()
            images = []
            if mmc and mmc.model_stock_no:
                for img in mmc.model_stock_no.images.all():
                    if img.master_image:
                        images.append(img.master_image.url)
            if not images:
                images = [static('assets/images/imagePlaceholder.png')]
            data['model_images'] = images
            
            # Simplified accepted quantity logic
            total_ip_accepted_quantity = data.get('total_ip_accepted_quantity')
            lot_id = data.get('stock_lot_id')

            if total_ip_accepted_quantity and total_ip_accepted_quantity > 0:
                # Use stored accepted quantity if available
                data['display_accepted_qty'] = total_ip_accepted_quantity
            else:
                # Calculate from total_stock - total_rejection_qty (ignoring dp_missing_qty)
                total_rejection_qty = 0
                rejection_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
                if rejection_store and rejection_store.total_rejection_quantity:
                    total_rejection_qty = rejection_store.total_rejection_quantity

                total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
                
                if total_stock_obj and total_rejection_qty > 0:
                    # Calculate: total_stock - rejection_qty
                    data['display_accepted_qty'] = max(total_stock_obj.total_stock - total_rejection_qty, 0)
                    print(f"Calculated accepted qty for {lot_id}: {total_stock_obj.total_stock} - {total_rejection_qty} = {data['display_accepted_qty']}")
                else:
                    # No rejections or no stock data = 0 accepted
                    data['display_accepted_qty'] = 0
        print("=== END MANUAL LOOKUP ===")
        accepted_data = [d for d in master_data if d.get('accepted_Ip_stock')]
        rejected_data = [d for d in master_data if d.get('rejected_ip_stock') or d.get('few_cases_accepted_Ip_stock')]

        
        # 🔥 NEW: Add date information to context
        context = {

            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'from_date': from_date.strftime('%Y-%m-%d'),  # 🔥 NEW: Pass dates to template
            'to_date': to_date.strftime('%Y-%m-%d'),      # 🔥 NEW: Pass dates to template
            'date_filter_applied': bool(from_date_str and to_date_str),  # 🔥 NEW: Flag to show if custom dates used
        }
        return Response(context, template_name=self.template_name)
    
class IS_AcceptTable(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_AcceptTable.html'
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user
        
        # Create subqueries for all fields
        last_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('last_process_module')[:1]

        ip_person_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_person_qty_verified')[:1]
        
        lot_id_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('lot_id')[:1]
        
        next_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('next_process_module')[:1]

        
        dp_physical_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty')[:1]
        
        dp_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty_edited')[:1]
        
        accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_Ip_stock')[:1]

        few_cases_accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('few_cases_accepted_Ip_stock')[:1]
        
        accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_tray_scan_status')[:1]
        
        IP_pick_remarks_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('IP_pick_remarks')[:1]
        
        rejected_ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('rejected_ip_stock')[:1]
        
        ip_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_onhold_picking')[:1]

        total_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('total_stock')[:1]
        
        total_IP_accpeted_quantity_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('total_IP_accpeted_quantity')[:1]
        
        wiping_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('wiping_status')[:1]
        
        # FIXED: Use a more explicit approach for the rejection quantity
        # Instead of trying to reference the lot_id directly, we'll get it step by step
        
        # Only show rows where accepted_Ip_stock is True
        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0
        ).annotate(
            last_process_module=Subquery(last_process_module_subquery),
            next_process_module=Subquery(next_process_module_subquery),
            ip_person_qty_verified=Subquery(ip_person_qty_verified_subquery),
            dp_physical_qty=Subquery(dp_physical_qty_subquery),
            dp_physical_qty_edited=Subquery(dp_physical_qty_edited_subquery),
            accepted_Ip_stock=Subquery(accepted_Ip_stock_subquery),
            few_cases_accepted_Ip_stock=Subquery(few_cases_accepted_Ip_stock_subquery),
            IP_pick_remarks=Subquery(IP_pick_remarks_subquery),
            accepted_tray_scan_status=Subquery(accepted_tray_scan_status_subquery),
            rejected_ip_stock=Subquery(rejected_ip_stock_subquery),
            ip_onhold_picking=Subquery(ip_onhold_picking_subquery),
            total_stock=Subquery(total_stock_subquery),
            total_IP_accpeted_quantity=Subquery(total_IP_accpeted_quantity_subquery),
            stock_lot_id=Subquery(lot_id_subquery),
            wiping_status=Subquery(wiping_status_subquery),
            last_process_date_time=Subquery(TotalStockModel.objects.filter(
                batch_id=OuterRef('pk')
            ).values('last_process_date_time')[:1]),
        ).filter(
            Q(accepted_Ip_stock=True)|
            Q(few_cases_accepted_Ip_stock=True) & Q(ip_onhold_picking=False)
            
            
        ).order_by('-last_process_date_time')
        
        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(page_number)

        master_data = list(page_obj.object_list.values(
            'batch_id',
            'date_time',
            'model_stock_no__model_no',
            'plating_color',
            'polish_finish',
            'version__version_name',
            'vendor_internal',
            'location__location_name',
            'no_of_trays',
            'tray_type',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'stock_lot_id',
            'ip_person_qty_verified',
            'dp_physical_qty',
            'dp_physical_qty_edited',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'IP_pick_remarks',
            'rejected_ip_stock',
            'ip_onhold_picking',
            'total_batch_quantity',
            'total_IP_accpeted_quantity',
            'total_stock',
            'wiping_status',
            'last_process_date_time',
            'plating_stk_no',
            'polishing_stk_no',
            'category'
        ))

        # MANUAL APPROACH: Add rejection quantities manually
        # Since the subquery approach isn't working, let's add it manually
        for data in master_data:
            stock_lot_id = data.get('stock_lot_id')
            
                       
            # Rest of your existing logic
            total_stock = data.get('total_stock', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(total_stock / tray_capacity)
            else:
                data['no_of_trays'] = 0
                
            mmc = ModelMasterCreation.objects.filter(batch_id=data['batch_id']).first()
            images = []
            if mmc and mmc.model_stock_no:
                for img in mmc.model_stock_no.images.all():
                    if img.master_image:
                        images.append(img.master_image.url)
            if not images:
                images = [static('assets/images/imagePlaceholder.png')]
            data['model_images'] = images
            
        # Simplified accepted quantity logic
            total_IP_accpeted_quantity = data.get('total_IP_accpeted_quantity')
            lot_id = data.get('stock_lot_id')

            if total_IP_accpeted_quantity and total_IP_accpeted_quantity > 0:
                # Use stored accepted quantity if available
                data['display_accepted_qty'] = total_IP_accpeted_quantity
            else:
                # Calculate from total_stock - total_rejection_qty (ignoring dp_missing_qty)
                total_rejection_qty = 0
                rejection_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
                if rejection_store and rejection_store.total_rejection_quantity:
                    total_rejection_qty = rejection_store.total_rejection_quantity

                total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
                
                if total_stock_obj and total_rejection_qty > 0:
                    # Calculate: total_stock - rejection_qty
                    data['display_accepted_qty'] = max(total_stock_obj.total_stock - total_rejection_qty, 0)
                    print(f"Calculated accepted qty for {lot_id}: {total_stock_obj.total_stock} - {total_rejection_qty} = {data['display_accepted_qty']}")
                else:
                    # No rejections or no stock data = 0 accepted
                    data['display_accepted_qty'] = 0
        
        print("=== END MANUAL LOOKUP ===")
            
        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
        }
        return Response(context, template_name=self.template_name)

class IS_RejectTable(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_RejectTable.html'
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        user = request.user
        
        # Create subqueries for all fields
        last_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('last_process_module')[:1]

        ip_person_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_person_qty_verified')[:1]
        
        lot_id_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('lot_id')[:1]
        
        next_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('next_process_module')[:1]
               
        dp_physical_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty')[:1]
        
        dp_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_physical_qty_edited')[:1]
        
        accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_Ip_stock')[:1]

        few_cases_accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('few_cases_accepted_Ip_stock')[:1]
        
        accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_tray_scan_status')[:1]
        
        IP_pick_remarks_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('IP_pick_remarks')[:1]
        
        rejected_ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('rejected_ip_stock')[:1]
        
        ip_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('ip_onhold_picking')[:1]

        total_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('total_stock')[:1]
        
        
        # FIXED: Use a more explicit approach for the rejection quantity
        # Instead of trying to reference the lot_id directly, we'll get it step by step
        
        # Only show rows where accepted_Ip_stock is True
        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0
        ).annotate(
            last_process_module=Subquery(last_process_module_subquery),
            next_process_module=Subquery(next_process_module_subquery),
            ip_person_qty_verified=Subquery(ip_person_qty_verified_subquery),
            dp_physical_qty=Subquery(dp_physical_qty_subquery),
            dp_physical_qty_edited=Subquery(dp_physical_qty_edited_subquery),
            accepted_Ip_stock=Subquery(accepted_Ip_stock_subquery),
            few_cases_accepted_Ip_stock=Subquery(few_cases_accepted_Ip_stock_subquery),
            IP_pick_remarks=Subquery(IP_pick_remarks_subquery),
            accepted_tray_scan_status=Subquery(accepted_tray_scan_status_subquery),
            rejected_ip_stock=Subquery(rejected_ip_stock_subquery),
            ip_onhold_picking=Subquery(ip_onhold_picking_subquery),
            total_stock=Subquery(total_stock_subquery),
            stock_lot_id=Subquery(lot_id_subquery),
            last_process_date_time=Subquery(TotalStockModel.objects.filter(
                batch_id=OuterRef('pk')
            ).values('last_process_date_time')[:1]),

        ).filter(
            Q(rejected_ip_stock=True) |
            Q(few_cases_accepted_Ip_stock=True) & Q(ip_onhold_picking=False)
        ).order_by('-last_process_date_time')
        
        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(page_number)

        master_data = list(page_obj.object_list.values(
            'batch_id',
            'date_time',
            'model_stock_no__model_no',
            'plating_color',
            'polish_finish',
            'version__version_name',
            'vendor_internal',
            'location__location_name',
            'no_of_trays',
            'tray_type',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'stock_lot_id',
            'ip_person_qty_verified',
            'dp_physical_qty',
            'dp_physical_qty_edited',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'IP_pick_remarks',
            'rejected_ip_stock',
            'ip_onhold_picking',
            'total_batch_quantity',
            'total_stock',
            'last_process_date_time',
            'plating_stk_no',
            'polishing_stk_no',
            'category',
            'version__version_internal',
        ))

        # MANUAL APPROACH: Add rejection quantities manually
        # Since the subquery approach isn't working, let's add it manually
        # In the IS_RejectTable class, update the data processing section:
        for row in master_data:
            stock_lot_id = row.get('stock_lot_id')
            # Check if there are any REJECTED trays for this lot_id
            row['tray_id_in_trayid'] = TrayId.objects.filter(
                lot_id=stock_lot_id, 
                rejected_tray=True
            ).exists() if stock_lot_id else False
        for data in master_data:
            stock_lot_id = data.get('stock_lot_id')
            rejection_letters = []
            batch_rejection = False
        
            # Existing: Get rejection reasons from ReasonStore
            reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=stock_lot_id).first()
            if reason_store:
                batch_rejection = reason_store.batch_rejection
                reasons = reason_store.rejection_reason.all()
                for r in reasons:
                    if r.rejection_reason.upper() != 'SHORTAGE':
                        rejection_letters.append(r.rejection_reason[0].upper())
        
            # NEW: Check for SHORTAGE in IP_Rejected_TrayScan
            shortage_exists = IP_Rejected_TrayScan.objects.filter(
                lot_id=stock_lot_id,
                rejection_reason__rejection_reason__iexact='SHORTAGE'
            ).exists()
            if shortage_exists:
                rejection_letters.append('S')
        
            data['rejection_reason_letters'] = rejection_letters
            data['batch_rejection'] = batch_rejection
            # ...rest of your code...
            # Get rejection quantity from IP_Rejection_ReasonStore only
            if stock_lot_id:
                try:
                    rejection_qty = 0
                    rejection_record = IP_Rejection_ReasonStore.objects.filter(
                        lot_id=stock_lot_id
                    ).first()
                    
                    if rejection_record and rejection_record.total_rejection_quantity:
                        rejection_qty = rejection_record.total_rejection_quantity
                        print(f"Found rejection for {stock_lot_id}: {rejection_record.total_rejection_quantity}")
                    
                    # Set rejection quantity (only from IP_Rejection_ReasonStore)
                    data['ip_rejection_total_qty'] = rejection_qty
                    print(f"Set rejection qty for {stock_lot_id}: {rejection_qty}")
                                
                except Exception as e:
                    print(f"Error getting rejection for {stock_lot_id}: {str(e)}")
                    data['ip_rejection_total_qty'] = 0
            else:
                data['ip_rejection_total_qty'] = 0
                print(f"No stock_lot_id for batch {data.get('batch_id')}")
            # Rest of your existing logic
            total_stock = data.get('ip_rejection_total_qty', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(total_stock / tray_capacity)
            else:
                data['no_of_trays'] = 0
                
            
                

                
            mmc = ModelMasterCreation.objects.filter(batch_id=data['batch_id']).first()
            images = []
            if mmc and mmc.model_stock_no:
                for img in mmc.model_stock_no.images.all():
                    if img.master_image:
                        images.append(img.master_image.url)
            if not images:
                images = [static('assets/images/imagePlaceholder.png')]
            data['model_images'] = images
        
        print("=== END MANUAL LOOKUP ===")
            
        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
        }
        return Response(context, template_name=self.template_name)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rejection_details(request):
    """
    Get rejection reasons for a lot:
    - If batch_rejection=True, show Lot Rejection and total qty from IP_Rejection_ReasonStore.
    - Else, show reasons from IP_Rejected_TrayScan (rejection_reason, rejected_tray_quantity).
    """
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
        data = []

        if reason_store and reason_store.batch_rejection:
            # Batch rejection: show only one row
            data.append({
                'reason': 'Lot Rejection',
                'qty': reason_store.total_rejection_quantity
            })
        else:
            # Not batch rejection: show all tray scan rejections
            tray_scans = IP_Rejected_TrayScan.objects.filter(lot_id=lot_id)
            for scan in tray_scans:
                data.append({
                    'reason': scan.rejection_reason.rejection_reason if scan.rejection_reason else 'Unknown',
                    'qty': scan.rejected_tray_quantity
                })

        if not data:
            data = []

        return Response({'success': True, 'reasons': data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class IPSaveHoldUnholdReasonAPIView(APIView):
    """
    POST with:
    {
        "remark": "Reason text",
        "action": "hold"  # or "unhold"
    }
    """
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            print("DEBUG: Received lot_id:", lot_id)  # <-- Add this line

            remark = data.get('remark', '').strip()
            action = data.get('action', '').strip().lower()

            if not lot_id or not remark or action not in ['hold', 'unhold']:
                return JsonResponse({'success': False, 'error': 'Missing or invalid parameters.'}, status=400)

            obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not obj:
                return JsonResponse({'success': False, 'error': 'LOT not found.'}, status=404)

            if action == 'hold':
                obj.ip_holding_reason = remark
                obj.ip_hold_lot = True
                obj.ip_release_reason = ''
                obj.ip_release_lot = False
            elif action == 'unhold':
                obj.ip_release_reason = remark
                obj.ip_hold_lot = False
                obj.ip_release_lot = True

            obj.save(update_fields=['ip_holding_reason', 'ip_release_reason', 'ip_hold_lot', 'ip_release_lot'])
            return JsonResponse({'success': True, 'message': 'Reason saved.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
        
        
# Add these views to your views.py

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SaveRejectionDraftAPIView(APIView):
    """
    Save rejection data as draft
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            batch_id = data.get('batch_id')
            rejection_data = data.get('rejection_data', [])  # List of {reason_id, qty}
            tray_scans = data.get('tray_scans', [])  # List of {tray_id, tray_qty}
            is_batch_rejection = data.get('is_batch_rejection', False)
            
            if not lot_id:
                return JsonResponse({'success': False, 'error': 'lot_id is required'}, status=400)
            
            # Prepare draft data
            draft_data = {
                'batch_id': batch_id,
                'rejection_data': rejection_data,
                'tray_scans': tray_scans,
                'is_batch_rejection': is_batch_rejection,
                'total_rejection_qty': sum(int(item.get('qty', 0)) for item in rejection_data)
            }
            
            # Save or update draft
            draft_obj, created = IP_Rejection_Draft.objects.update_or_create(
                lot_id=lot_id,
                user=request.user,
                defaults={
                    'draft_data': draft_data
                }
            )
            
            # ✅ NEW: Update ip_onhold_picking to True in TotalStockModel
            try:
                total_stock = TotalStockModel.objects.get(lot_id=lot_id)
                total_stock.ip_onhold_picking = True
                total_stock.save(update_fields=['ip_onhold_picking'])
                print(f"✅ Updated ip_onhold_picking=True for lot_id: {lot_id}")
            except TotalStockModel.DoesNotExist:
                print(f"⚠️ TotalStockModel not found for lot_id: {lot_id}")
                # Don't fail the draft save if TotalStockModel is not found
            except Exception as stock_error:
                print(f"❌ Error updating TotalStockModel for lot_id {lot_id}: {str(stock_error)}")
                # Don't fail the draft save if TotalStockModel update fails
            
            return JsonResponse({
                'success': True, 
                'message': 'Draft saved successfully',
                'created': created
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rejection_draft(request):
    """
    Get draft rejection data for a lot
    """
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        draft = IP_Rejection_Draft.objects.filter(
            lot_id=lot_id, 
            user=request.user
        ).first()
        
        if draft:
            return Response({
                'success': True,
                'has_draft': True,
                'draft_data': draft.draft_data,
                'updated_at': draft.updated_at.isoformat()
            })
        else:
            return Response({
                'success': True,
                'has_draft': False,
                'draft_data': None
            })
            
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_delink_tray_data(request):
    """
    Get delink tray data based on empty trays after all rejections are applied.
    
    CORRECTED LOGIC:
    - Only create delink rows for trays that have 0 quantity after rejections
    - SHORTAGE rejections don't need separate delink rows
    - The empty tray logic already handles cases where shortage creates empty trays
    """
    try:
        lot_id = request.GET.get('lot_id')
        if not lot_id:
            return Response({'success': False, 'error': 'No lot_id provided'}, status=400)
        
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if not stock:
            return Response({'success': False, 'error': 'No stock record found for this lot'}, status=404)
        
        original_distribution = get_actual_tray_distribution_for_delink(lot_id, stock)
        current_distribution = calculate_distribution_after_rejections(lot_id, original_distribution)
        
        # ✅ FIXED: Only create delink rows for empty trays (quantity = 0)
        empty_trays = [i for i, qty in enumerate(current_distribution) if qty == 0]
        delink_data = []
        
        for i, tray_index in enumerate(empty_trays):
            original_qty = original_distribution[tray_index] if tray_index < len(original_distribution) else 0
            delink_data.append({
                'sno': i + 1,
                'tray_id': '',  # Empty - user will scan to delink
                'tray_quantity': original_qty,
                'tray_index': tray_index,
                'source': 'empty_tray'
            })

        # ✅ REMOVED: No longer adding automatic delink rows for SHORTAGE
        # The empty tray logic above already handles cases where shortage creates empty trays

        return Response({
            'success': True,
            'delink_trays': delink_data,
            'total_count': len(delink_data),
            'lot_id': lot_id,
            'original_distribution': original_distribution,
            'current_distribution': current_distribution,
            'empty_trays_count': len(empty_trays),
            'debug_info': {
                'empty_tray_indices': empty_trays,
                'reasoning': 'Only trays with 0 quantity after rejections need delink',
                'logic': 'Delink rows = trays with 0 quantity after all rejections',
                'examples': {
                    'case1': '[14,16] → shortage 4 → [10,16] → no empty trays → no delink',
                    'case2': '[14,16] → shortage 14 → [0,16] → 1 empty tray → 1 delink'
                }
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)
def calculate_distribution_after_rejections(lot_id, original_distribution):
    """
    Calculate the current tray distribution after applying all rejections.
    
    CORRECTED LOGIC:
    - NEW tray usage frees up existing tray space (creates empty trays)
    - Existing tray usage removes that tray entirely from distribution  
    - SHORTAGE rejections consume quantities from existing trays (can create empty trays)
    """
    current_distribution = original_distribution.copy()
    
    # Get all rejections for this lot ordered by creation
    rejections = IP_Rejected_TrayScan.objects.filter(lot_id=lot_id).order_by('id')
    
    print(f"DEBUG: Processing {rejections.count()} rejections for lot {lot_id}")
    print(f"DEBUG: Starting distribution: {original_distribution}")
    
    for rejection in rejections:
        rejected_qty = int(rejection.rejected_tray_quantity) if rejection.rejected_tray_quantity else 0
        tray_id = rejection.rejected_tray_id
        reason = rejection.rejection_reason.rejection_reason if rejection.rejection_reason else 'Unknown'
        
        if rejected_qty <= 0:
            print(f"DEBUG: Skipping rejection with 0 quantity")
            continue
        
        print(f"DEBUG: Processing rejection - Reason: {reason}, Qty: {rejected_qty}, Tray ID: '{tray_id}'")
        
        # ✅ FIXED: Handle SHORTAGE rejections properly
        if not tray_id or tray_id.strip() == '':
            print(f"DEBUG: SHORTAGE rejection - consuming {rejected_qty} from existing trays")
            # SHORTAGE rejections consume quantities from existing trays
            current_distribution = consume_shortage_from_distribution(current_distribution, rejected_qty)
            print(f"DEBUG: Distribution after SHORTAGE: {current_distribution}")
            continue
        
        # Check if NEW tray was used for non-SHORTAGE rejections
        is_new_tray = is_new_tray_by_id(tray_id)
        print(f"DEBUG: is_new_tray_by_id('{tray_id}') = {is_new_tray}")
        
        if is_new_tray:
            print(f"DEBUG: ✅ NEW tray used - freeing up {rejected_qty} space in existing trays")
            current_distribution = free_up_space_optimally(current_distribution, rejected_qty)
        else:
            print(f"DEBUG: ❌ Existing tray used - removing {rejected_qty} from distribution entirely")
            current_distribution = remove_rejected_tray_from_distribution(current_distribution, rejected_qty)
        
        print(f"DEBUG: Distribution after this rejection: {current_distribution}")
    
    print(f"DEBUG: Final distribution: {current_distribution}")
    return current_distribution


def consume_shortage_from_distribution(distribution, shortage_qty):
    """
    ✅ NEW FUNCTION: Handle SHORTAGE rejections by consuming from existing trays
    This will consume from smallest trays first to maximize chance of creating empty trays
    
    Example: [6, 12, 12] with shortage 6 → [0, 12, 12]
    """
    result = distribution.copy()
    remaining_shortage = shortage_qty
    
    print(f"   SHORTAGE: consuming {shortage_qty} from distribution {distribution}")
    
    # Consume from smallest trays first (to create empty trays for delink)
    sorted_indices = sorted(range(len(result)), key=lambda i: result[i])
    
    for i in sorted_indices:
        if remaining_shortage <= 0:
            break
            
        current_qty = result[i]
        if current_qty >= remaining_shortage:
            # This tray can handle all remaining shortage
            result[i] = current_qty - remaining_shortage
            print(f"   SHORTAGE: consumed {remaining_shortage} from tray {i}, remaining: {result[i]}")
            remaining_shortage = 0
        elif current_qty > 0:
            # Consume entire tray and continue
            remaining_shortage -= current_qty
            print(f"   SHORTAGE: consumed entire tray {i}: {current_qty}")
            result[i] = 0
    
    if remaining_shortage > 0:
        print(f"   ⚠️ WARNING: Could not consume all shortage qty, remaining: {remaining_shortage}")
    
    print(f"   SHORTAGE result: {result}")
    return result


def remove_rejected_tray_from_distribution(distribution, rejected_qty):
    """
    EXISTING tray rejection: consume rejection quantity AND remove one tray entirely
    This matches the user's requirement where existing tray usage removes a physical tray
    """
    result = distribution.copy()
    total_available = sum(result)
    
    if total_available < rejected_qty:
        return result  # Not enough quantity, return unchanged
    
    # Step 1: Try to find exact match first
    for i, qty in enumerate(result):
        if qty == rejected_qty:
            result.pop(i)  # Remove the tray with exact quantity
            return result
    
    # Step 2: No exact match - consume rejected_qty and remove one tray
    remaining_to_consume = rejected_qty
    
    # Consume the rejection quantity from available trays
    for i in range(len(result)):
        if remaining_to_consume <= 0:
            break
        current_qty = result[i]
        consume_from_this_tray = min(remaining_to_consume, current_qty)
        result[i] -= consume_from_this_tray
        remaining_to_consume -= consume_from_this_tray
    
    # Step 3: Remove one tray entirely (prefer empty ones first)
    # Remove empty tray first
    for i in range(len(result)):
        if result[i] == 0:
            result.pop(i)
            return result
    
    # If no empty tray, remove the smallest quantity tray
    if result:
        min_qty = min(result)
        for i in range(len(result)):
            if result[i] == min_qty:
                result.pop(i)
                return result
    
    return result

def free_up_space_optimally(distribution, qty_to_free):
    """
    Free up space in existing trays when NEW tray is used for rejection.
    Always zero out the smallest trays first, so delink is possible.
    Example: [6, 12, 12] with NEW tray for 6 qty → [0, 12, 12]
    """
    result = distribution.copy()
    remaining = qty_to_free
    # Free from smallest trays first (to maximize empty trays)
    sorted_indices = sorted(range(len(result)), key=lambda i: result[i])
    for i in sorted_indices:
        if remaining <= 0:
            break
        current_qty = result[i]
        if current_qty >= remaining:
            result[i] = current_qty - remaining
            remaining = 0
        elif current_qty > 0:
            remaining -= current_qty
            result[i] = 0
    return result


def get_original_capacity_for_tray(tray_index, current_distribution):
    """
    Get the original capacity for a tray. 
    For simplicity, we'll assume all trays have the same capacity.
    You can enhance this to get actual individual tray capacities if needed.
    """
    # Find the maximum quantity in current distribution as a reference
    max_qty = max(current_distribution) if current_distribution else 12
    return max_qty if max_qty > 0 else 12


def get_actual_tray_distribution_for_delink(lot_id, stock):
    """
    Get the actual tray distribution for a lot for delink calculations.
    This should match the distribution used in rejection validation.
    """
    try:
        print(f"🔍 DEBUG: get_actual_tray_distribution_for_delink called with lot_id={lot_id}")
        
        # ✅ PRIORITY: Always get fresh data from TotalStockModel using lot_id
        try:
            fresh_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if fresh_stock:
                print(f"🔍 DEBUG: Fresh stock found - total_stock={getattr(fresh_stock, 'total_stock', 'N/A')}")
                print(f"🔍 DEBUG: Fresh stock - dp_physical_qty={getattr(fresh_stock, 'dp_physical_qty', 'N/A')}")
                
                # Get tray capacity
                tray_capacity = 10  # Default fallback
                if fresh_stock.batch_id and hasattr(fresh_stock.batch_id, 'tray_capacity'):
                    tray_capacity = fresh_stock.batch_id.tray_capacity
                print(f"🔍 DEBUG: tray_capacity from fresh_stock = {tray_capacity}")
                
                # Try total_stock first
                total_qty = None
                if hasattr(fresh_stock, 'total_stock') and fresh_stock.total_stock and fresh_stock.total_stock > 0:
                    total_qty = fresh_stock.total_stock
                    print(f"✅ Using total_stock = {total_qty}")
                elif hasattr(fresh_stock, 'dp_physical_qty') and fresh_stock.dp_physical_qty and fresh_stock.dp_physical_qty > 0:
                    total_qty = fresh_stock.dp_physical_qty
                    print(f"✅ Using dp_physical_qty = {total_qty}")
                
                if total_qty and total_qty > 0:
                    # Calculate distribution: remainder first, then full capacity trays
                    remainder = total_qty % tray_capacity
                    full_trays = total_qty // tray_capacity
                    
                    print(f"🔍 CALCULATION: {total_qty} ÷ {tray_capacity} = {full_trays} full trays + {remainder} remainder")
                    
                    distribution = []
                    
                    # Top tray with remainder (if exists)
                    if remainder > 0:
                        distribution.append(remainder)
                        print(f"🔍 Added remainder tray: {remainder}")
                    
                    # Full capacity trays
                    for i in range(full_trays):
                        distribution.append(tray_capacity)
                        print(f"🔍 Added full tray {i+1}: {tray_capacity}")
                    
                    print(f"✅ FINAL calculated distribution: {distribution}")
                    return distribution
                else:
                    print(f"❌ No valid total_qty found in fresh_stock")
        except Exception as fresh_error:
            print(f"❌ Error getting fresh stock: {fresh_error}")
        
        # Method 1: Try to get from TrayId records if they have individual quantities
        print(f"🔍 Trying Method 1: TrayId records")
        tray_records = TrayId.objects.filter(lot_id=lot_id).order_by('created_at')
        if tray_records.exists():
            print(f"🔍 Found {tray_records.count()} TrayId records")
            tray_quantities = []
            for tray in tray_records:
                if hasattr(tray, 'tray_quantity') and tray.tray_quantity:
                    tray_quantities.append(tray.tray_quantity)
                    print(f"🔍 TrayId {tray.tray_id}: quantity = {tray.tray_quantity}")
            
            if tray_quantities:
                print(f"✅ Method 1 SUCCESS: Found tray distribution from TrayId records: {tray_quantities}")
                return tray_quantities
        
        # Get tray capacity from passed stock object
        tray_capacity = 10  # Default fallback
        if hasattr(stock, 'batch_id') and stock.batch_id and hasattr(stock.batch_id, 'tray_capacity'):
            tray_capacity = stock.batch_id.tray_capacity
        
        print(f"🔍 Method 2: Using passed stock object, tray_capacity = {tray_capacity}")
        
        # Method 2: Calculate from total_stock (primary method)
        if hasattr(stock, 'total_stock') and stock.total_stock and stock.total_stock > 0:
            total_qty = stock.total_stock
            print(f"🔍 Method 2: total_stock = {total_qty}")
            
            # Calculate distribution: remainder first, then full capacity trays
            remainder = total_qty % tray_capacity
            full_trays = total_qty // tray_capacity
            
            distribution = []
            
            # Top tray with remainder (if exists)
            if remainder > 0:
                distribution.append(remainder)
            
            # Full capacity trays
            for _ in range(full_trays):
                distribution.append(tray_capacity)
            
            print(f"✅ Method 2 SUCCESS: Calculated from total_stock: total_qty={total_qty}, tray_capacity={tray_capacity}")
            print(f"   Formula: {total_qty} ÷ {tray_capacity} = {full_trays} full trays + {remainder} remainder")
            print(f"   Result: {distribution}")
            return distribution
        
        # Method 3: Try to get from TotalStockModel.dp_physical_qty
        elif hasattr(stock, 'dp_physical_qty') and stock.dp_physical_qty and stock.dp_physical_qty > 0:
            total_qty = stock.dp_physical_qty
            print(f"🔍 Method 3: dp_physical_qty = {total_qty}")
            
            remainder = total_qty % tray_capacity
            full_trays = total_qty // tray_capacity
            
            distribution = []
            if remainder > 0:
                distribution.append(remainder)
            for _ in range(full_trays):
                distribution.append(tray_capacity)
            
            print(f"✅ Method 3 SUCCESS: Calculated from dp_physical_qty: total_qty={total_qty}, tray_capacity={tray_capacity}")
            print(f"   Formula: {total_qty} ÷ {tray_capacity} = {full_trays} full trays + {remainder} remainder")
            print(f"   Result: {distribution}")
            return distribution
        
        # Last resort: minimal fallback
        print(f"⚠️ ALL METHODS FAILED: Using minimal fallback distribution with tray_capacity={tray_capacity}")
        return [tray_capacity]  # At least one tray with standard capacity
        
    except Exception as e:
        print(f"❌ Error getting tray distribution: {e}")
        import traceback
        traceback.print_exc()
        # Emergency fallback - try to get at least tray_capacity
        tray_capacity = 10
        try:
            if hasattr(stock, 'batch_id') and stock.batch_id and hasattr(stock.batch_id, 'tray_capacity'):
                tray_capacity = stock.batch_id.tray_capacity
        except:
            pass
        print(f"⚠️ Emergency fallback: [{tray_capacity}]")
        return [tray_capacity]
    
# ✅ UPDATED: Enhanced delink_check_tray_id function
@require_GET
def delink_check_tray_id(request):
    """
    Validate tray ID for delink process
    Check if tray exists in same lot and is not already rejected
    """
    tray_id = request.GET.get('tray_id', '')
    current_lot_id = request.GET.get('lot_id', '')
    
    try:
        # Get the tray object if it exists
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        
        if not tray_obj:
            # Tray doesn't exist
            return JsonResponse({
                'exists': False,
                'valid_for_delink': False,
                'error': 'Tray ID not found',
                'status_message': 'Not Found'
            })
            
        # ✅ NEW: Only allow if IP_tray_verified is True
        if not getattr(tray_obj, 'IP_tray_verified', False):
            return JsonResponse({
                'exists': False,
                'valid_for_delink': False,
                'error': 'Tray id is not verified',
                'status_message': 'Tray id is not verified',
                'tray_status': 'not_verified'
            })
        
        # ✅ VALIDATION 1: Check if tray belongs to same lot
        if tray_obj.lot_id:
            if str(tray_obj.lot_id).strip() != str(current_lot_id).strip():
                return JsonResponse({
                    'exists': True,
                    'valid_for_delink': False,
                    'error': 'Different lot',
                    'status_message': 'Different Lot',
                    'tray_status': 'different_lot'
                })
        else:
            # Tray has no lot_id assigned
            return JsonResponse({
                'exists': True,
                'valid_for_delink': False,
                'error': 'No lot assigned',
                'status_message': 'No Lot Assigned',
                'tray_status': 'no_lot'
            })
        
        # ✅ VALIDATION 2: Check if tray is already rejected
        if tray_obj.rejected_tray:
            return JsonResponse({
                'exists': True,
                'valid_for_delink': False,
                'error': 'Already rejected',
                'status_message': 'Already Rejected',
                'tray_status': 'already_rejected'
            })
        
        # ✅ SUCCESS: Tray exists, same lot, and not rejected
        return JsonResponse({
            'exists': True,
            'valid_for_delink': True,
            'status_message': 'Available for Delink',
            'tray_status': 'available',
            'tray_quantity': tray_obj.tray_quantity or 0
        })
        
    except Exception as e:
        return JsonResponse({
            'exists': False,
            'valid_for_delink': False,
            'error': 'System error',
            'status_message': 'System Error'
        })
        
@method_decorator(csrf_exempt, name='dispatch')
class TrayValidate_Complete_APIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id_input = str(data.get('batch_id')).strip()
            tray_id = str(data.get('tray_id')).strip()
            
            # Get stock status parameters (optional, for enhanced validation)
            accepted_ip_stock = data.get('accepted_ip_stock', False)
            rejected_ip_stock = data.get('rejected_ip_stock', False)
            few_cases_accepted_ip_stock = data.get('few_cases_accepted_ip_stock', False)
            
            print(f"[TrayValidate_Complete_APIView] User entered: batch_id={batch_id_input}, tray_id={tray_id}")
            print(f"Stock status: accepted={accepted_ip_stock}, rejected={rejected_ip_stock}, few_cases={few_cases_accepted_ip_stock}")

            # Base queryset for trays
            base_queryset = TrayId.objects.filter(
                batch_id__batch_id__icontains=batch_id_input,
                tray_quantity__gt=0
            )
            
            # Apply the same filtering logic as the list API
            if accepted_ip_stock and not few_cases_accepted_ip_stock:
                # Only validate against accepted trays
                trays = base_queryset.filter(rejected_tray=False)
                print(f"Validating against accepted trays only")
            elif rejected_ip_stock and not few_cases_accepted_ip_stock:
                # Only validate against rejected trays
                trays = base_queryset.filter(rejected_tray=True)
                print(f"Validating against rejected trays only")
            else:
                # Validate against all trays (few_cases or default)
                trays = base_queryset
                print(f"Validating against all trays")
            
            print(f"Available tray_ids for validation: {[t.tray_id for t in trays]}")

            exists = trays.filter(tray_id=tray_id).exists()
            print(f"Tray ID '{tray_id}' exists in filtered results? {exists}")

            # Get additional info about the tray if it exists
            tray_info = {}
            if exists:
                tray = trays.filter(tray_id=tray_id).first()
                if tray:
                    tray_info = {
                        'rejected_tray': tray.rejected_tray,
                        'tray_quantity': tray.tray_quantity,
                        'ip_top_tray': tray.ip_top_tray,  # ✅ UPDATED: Use ip_top_tray instead of top_tray
                        'ip_top_tray_qty': tray.ip_top_tray_qty  # ✅ UPDATED: Include ip_top_tray_qty
                    }

            return JsonResponse({
                'success': True, 
                'exists': exists,
                'tray_info': tray_info
            })
            
        except Exception as e:
            print(f"[TrayValidate_Complete_APIView] Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)    
           
           
@method_decorator(csrf_exempt, name='dispatch')
class TrayIdList_Complete_APIView(APIView):
    def get(self, request):
        batch_id = request.GET.get('batch_id')
        stock_lot_id = request.GET.get('stock_lot_id')
        lot_id = request.GET.get('lot_id') or stock_lot_id
        accepted_ip_stock = request.GET.get('accepted_ip_stock', 'false').lower() == 'true'
        rejected_ip_stock = request.GET.get('rejected_ip_stock', 'false').lower() == 'true'
        few_cases_accepted_ip_stock = request.GET.get('few_cases_accepted_ip_stock', 'false').lower() == 'true'
        
        if not batch_id:
            return JsonResponse({'success': False, 'error': 'Missing batch_id'}, status=400)
        
        if not lot_id:
            return JsonResponse({'success': False, 'error': 'Missing lot_id or stock_lot_id'}, status=400)
                
        # ✅ Check for batch rejection
        batch_rejection_record = IP_Rejection_ReasonStore.objects.filter(
            lot_id=lot_id, batch_rejection=True
        ).first()
        is_batch_rejection = bool(batch_rejection_record)

        # ✅ Get rejected tray scans with detailed info
        rejected_tray_scans = IP_Rejected_TrayScan.objects.filter(lot_id=lot_id)
        rejected_tray_ids = []
        rejected_tray_data = {}
        rejected_tray_quantities = {}  # Store quantities from rejection records
        
        for scan in rejected_tray_scans:
            if scan.rejected_tray_id:  # Only include non-empty tray IDs
                rejected_tray_ids.append(scan.rejected_tray_id)
                rejected_tray_quantities[scan.rejected_tray_id] = scan.rejected_tray_quantity
                
                if scan.rejected_tray_id not in rejected_tray_data:
                    rejected_tray_data[scan.rejected_tray_id] = []
                rejected_tray_data[scan.rejected_tray_id].append({
                    'rejected_quantity': scan.rejected_tray_quantity,
                    'rejection_reason': scan.rejection_reason.rejection_reason,
                    'rejection_reason_id': scan.rejection_reason.rejection_reason_id,
                    'user': scan.user.username if scan.user else None
                })
        
        print(f"Found {len(rejected_tray_ids)} rejected tray IDs: {rejected_tray_ids}")
        
        # Base queryset - trays from TrayId table
        base_queryset = TrayId.objects.filter(
            batch_id__batch_id=batch_id,
            tray_quantity__gt=0,
            lot_id=lot_id
        )
        
        # ✅ FIXED: Ensure rejected trays are included even if not in TrayId table
        existing_tray_ids = list(base_queryset.values_list('tray_id', flat=True))
        missing_rejected_trays = [tray_id for tray_id in rejected_tray_ids if tray_id not in existing_tray_ids]
        
        print(f"Existing tray IDs in TrayId table: {existing_tray_ids}")
        print(f"Missing rejected trays (not in TrayId): {missing_rejected_trays}")
        
        # Apply filtering based on stock status
        if accepted_ip_stock and not few_cases_accepted_ip_stock:
            queryset = base_queryset.exclude(tray_id__in=rejected_tray_ids)
            include_missing_rejected = False
            print(f"Filtering for accepted trays only")
        elif rejected_ip_stock and not few_cases_accepted_ip_stock:
            queryset = base_queryset.filter(tray_id__in=rejected_tray_ids)
            include_missing_rejected = True
            print(f"Filtering for rejected trays only")
        elif few_cases_accepted_ip_stock:
            queryset = base_queryset
            include_missing_rejected = True
            print(f"Showing both accepted and rejected trays")
        else:
            queryset = base_queryset
            include_missing_rejected = False
            print(f"Using default filter - showing all trays")
        
        # Determine top tray
        top_tray = None
        if accepted_ip_stock and not few_cases_accepted_ip_stock:
            top_tray = base_queryset.filter(top_tray=True).first()
            ip_top_tray_obj = base_queryset.filter(ip_top_tray=True).first()
            if ip_top_tray_obj:
                top_tray = ip_top_tray_obj
        else:
            top_tray = base_queryset.filter(ip_top_tray=True).first()
        
        # Remove top tray from other_trays queryset
        other_trays = queryset.exclude(pk=top_tray.pk if top_tray else None).order_by('id')
        
        data = []
        row_counter = 1

        # ✅ Helper function to create tray data
        def create_tray_data(tray_obj, tray_id, is_top=False, is_missing=False):
            nonlocal row_counter
            
            # ✅ FIX: Check delink_tray status separately if tray_obj is None
            delink_tray_status = False
            if tray_obj:
                delink_tray_status = getattr(tray_obj, 'delink_tray', False)
            elif is_missing and tray_id:
                # For missing trays, check TrayId table directly for delink status
                try:
                    actual_tray = TrayId.objects.filter(tray_id=tray_id).first()
                    if actual_tray:
                        delink_tray_status = getattr(actual_tray, 'delink_tray', False)
                        print(f"Found missing tray {tray_id} with delink_tray={delink_tray_status}")
                except Exception as e:
                    print(f"Error checking delink status for {tray_id}: {e}")
            
            if is_batch_rejection:
                is_rejected = True
                rejection_details = [{
                    'rejection_reason': 'Lot Rejection',
                    'rejected_quantity': tray_obj.tray_quantity if tray_obj else rejected_tray_quantities.get(tray_id, 0),
                    'user': batch_rejection_record.user.username if batch_rejection_record and batch_rejection_record.user else None
                }]
                tray_qty = tray_obj.tray_quantity if tray_obj else rejected_tray_quantities.get(tray_id, 0)
            else:
                is_rejected = tray_id in rejected_tray_ids
                rejection_details = rejected_tray_data.get(tray_id, []) if is_rejected else []
                
                if is_rejected and is_missing:
                    tray_qty = rejected_tray_quantities.get(tray_id, 0)
                elif is_rejected and tray_obj:
                    tray_qty = rejected_tray_quantities.get(tray_id, tray_obj.tray_quantity)
                else:
                    tray_qty = tray_obj.tray_quantity if tray_obj else 0
            
            return {
                's_no': row_counter,
                'tray_id': tray_id,
                'tray_quantity': tray_qty,
                'position': row_counter - 1,
                'is_top_tray': is_top,
                'rejected_tray': is_rejected,
                'delink_tray': delink_tray_status,  # ✅ FIXED: Use separately checked status
                'rejection_details': rejection_details,
                'ip_top_tray': getattr(tray_obj, 'ip_top_tray', False) if tray_obj else False,
                'ip_top_tray_qty': getattr(tray_obj, 'ip_top_tray_qty', None) if tray_obj else None,
                'top_tray': getattr(tray_obj, 'top_tray', False) if tray_obj else False,
                'is_missing_from_trayid': is_missing
            }
        # Add top tray first if it exists
        if top_tray:
            tray_data = create_tray_data(top_tray, top_tray.tray_id, is_top=True)
            data.append(tray_data)
            row_counter += 1

        # Add other existing trays
        for tray in other_trays:
            tray_data = create_tray_data(tray, tray.tray_id, is_top=False)
            data.append(tray_data)
            row_counter += 1
        
        # ✅ FIXED: Add missing rejected trays if they should be included
        if include_missing_rejected and missing_rejected_trays:
            print(f"Adding {len(missing_rejected_trays)} missing rejected trays to response")
            for missing_tray_id in missing_rejected_trays:
                tray_data = create_tray_data(None, missing_tray_id, is_top=False, is_missing=True)
                data.append(tray_data)
                row_counter += 1
            
        print(f"Total trays returned: {len(data)}")
        
        # Rejection summary
        rejection_summary = {
            'total_rejected_trays': len(rejected_tray_ids),
            'rejected_tray_ids': rejected_tray_ids,
            'batch_rejection': is_batch_rejection,
            'shortage_rejections': IP_Rejected_TrayScan.objects.filter(
                lot_id=lot_id, 
                rejected_tray_id__isnull=True
            ).count() or IP_Rejected_TrayScan.objects.filter(
                lot_id=lot_id, 
                rejected_tray_id=''
            ).count(),
            'missing_rejected_trays': missing_rejected_trays  # ✅ NEW: Track missing trays
            
        }
        
        return JsonResponse({
            'success': True, 
            'trays': data,
            'rejection_summary': rejection_summary
        })   
        
@method_decorator(csrf_exempt, name='dispatch')
class GetShortageRejectionsView(APIView):
    def get(self, request):
        lot_id = request.GET.get('lot_id')
        
        if not lot_id:
            return JsonResponse({'success': False, 'error': 'Missing lot_id'}, status=400)
        
        # Get SHORTAGE rejections (where rejected_tray_id is empty or null)
        shortage_rejections = IP_Rejected_TrayScan.objects.filter(
            lot_id=lot_id,
            rejected_tray_id__isnull=True
        ).union(
            IP_Rejected_TrayScan.objects.filter(
                lot_id=lot_id,
                rejected_tray_id=''
            )
        )
        
        shortage_data = []
        for shortage in shortage_rejections:
            shortage_data.append({
                'quantity': shortage.rejected_tray_quantity,
                'reason': shortage.rejection_reason.rejection_reason,
                'user': shortage.user.username if shortage.user else None
            })
        
        return JsonResponse({
            'success': True,
            'shortage_rejections': shortage_data
        })

@csrf_exempt
def delink_selected_trays(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            # Check if we received stock_lot_ids or tray_ids
            stock_lot_ids = data.get('stock_lot_ids', [])
            tray_ids = data.get('tray_ids', [])  # Keep backward compatibility
            
            updated = 0
            lots_processed = 0
            not_found = []
            
            if stock_lot_ids:
                # New logic: Delink only REJECTED trays for the given lot IDs
                for stock_lot_id in stock_lot_ids:
                    # Find only REJECTED tray IDs associated with this lot
                    rejected_tray_ids = TrayId.objects.filter(
                        lot_id=stock_lot_id, 
                        rejected_tray=True
                    ).values_list('tray_id', flat=True)
                    
                    if rejected_tray_ids:
                        # Update only rejected trays for this lot
                        updated_count = TrayId.objects.filter(
                            lot_id=stock_lot_id,
                            rejected_tray=True
                        ).update(
                            delink_tray=True,
                            lot_id=None,
                            batch_id=None,
                            scanned=False,
                            IP_tray_verified=False,
                            rejected_tray=False,  # ✅ ADD THIS - Reset rejected_tray to False
                            top_tray=False
                        )
                        updated += updated_count
                        lots_processed += 1
                        print(f"Delinked {updated_count} REJECTED trays for lot {stock_lot_id}: {list(rejected_tray_ids)}")
                    else:
                        not_found.append(stock_lot_id)
                        print(f"No REJECTED trays found for lot {stock_lot_id}")
                
                return JsonResponse({
                    'success': True, 
                    'updated': updated, 
                    'lots_processed': lots_processed,
                    'not_found': not_found
                })
            
            elif tray_ids:
                # Original logic: Delink specific tray IDs (keep for backward compatibility)
                for tray_id in tray_ids:
                    delink_tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
                    if delink_tray_obj:
                        delink_tray_obj.delink_tray = True
                        delink_tray_obj.lot_id = None
                        delink_tray_obj.batch_id = None
                        delink_tray_obj.scanned = False
                        delink_tray_obj.IP_tray_verified = False
                        delink_tray_obj.rejected_tray = False  # Reset rejected_tray to False
                        delink_tray_obj.top_tray = False
                        delink_tray_obj.save(update_fields=[
                            'delink_tray', 'lot_id', 'batch_id', 'scanned', 'IP_tray_verified', 'top_tray', 'rejected_tray'
                        ])
                        updated += 1
                    else:
                        not_found.append(tray_id)
                
                return JsonResponse({'success': True, 'updated': updated, 'not_found': not_found})
            
            else:
                return JsonResponse({'success': False, 'error': 'No stock_lot_ids or tray_ids provided'})
                
        except Exception as e:
            print(f"Error in delink_selected_trays: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)