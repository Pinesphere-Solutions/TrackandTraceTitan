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



class IS_PickTable(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_PickTable.html'

    def get(self, request):
        user = request.user

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
        
        ip_rejection_qty_subquery = IP_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('total_rejection_quantity')[:1]
        
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
            
            dp_missing_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('dp_missing_qty')[:1]
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
            ip_rejection_total_qty=Subquery(ip_rejection_qty_subquery),
            tray_scan_exists=tray_scan_exists,

            IP_pick_remarks=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('IP_pick_remarks')[:1]
            ),
            last_process_date_time=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('last_process_date_time')[:1]
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
            'total_batch_quantity',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'wiping_required',
            'stock_lot_id',
            'ip_person_qty_verified',
            'ip_rejection_total_qty',
            'dp_missing_qty',
            'dp_physical_qty',
            'dp_physical_qty_edited',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'IP_pick_remarks',
            'rejected_ip_stock',
            'ip_onhold_picking',
            'last_process_date_time',
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
            
            # Fallback logic for accepted quantity
            total_ip_accepted_quantity = data.get('total_ip_accepted_quantity')
            lot_id = data.get('stock_lot_id')
            accepted_tray_quantity = 0

            if not total_ip_accepted_quantity or total_ip_accepted_quantity == 0:
                # Fetch total_rejection_quantity from IP_Rejection_ReasonStore
                total_rejection_qty = 0
                rejection_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
                if rejection_store and rejection_store.total_rejection_quantity:
                    total_rejection_qty = rejection_store.total_rejection_quantity
            
                # Fetch dp_physical_qty from TotalStockModel
                dp_physical_qty = 0
                total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
                if total_stock_obj and total_stock_obj.dp_physical_qty:
                    dp_physical_qty = total_stock_obj.dp_physical_qty
            
                # Calculate display_accepted_qty
                data['display_accepted_qty'] = max(dp_physical_qty - total_rejection_qty, 0)
            else:
                data['display_accepted_qty'] = total_ip_accepted_quantity

            
             # --- Add available_qty for each row ---
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

        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'ip_rejection_reasons':ip_rejection_reasons,
        }
        return Response(context, template_name=self.template_name)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')  
class SaveIPCheckboxView(APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            lot_id = data.get("lot_id")
            missing_qty = data.get("missing_qty")
            edited_tray_qty = data.get("edited_tray_qty")  # <-- Get edited qty from frontend
            print(f"[SaveIPCheckboxView] edited_tray_qty received: {edited_tray_qty}")

            if not lot_id:
                return Response({"success": False, "error": "Lot ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            total_stock.ip_person_qty_verified = True

            # --- NEW LOGIC: If edited_tray_qty is provided, update TrayId and accumulate missing_qty ---
            if edited_tray_qty not in [None, ""]:
                try:
                    edited_tray_qty = int(edited_tray_qty)
                    # Find the top tray for this lot
                    top_tray = TrayId.objects.filter(lot_id=lot_id, top_tray=True).first()
                    if top_tray:
                        prev_qty = top_tray.tray_quantity or 0
                        original_qty = prev_qty
                        diff = (original_qty - edited_tray_qty)
                        if diff < 0:
                            diff = 0  # Prevent negative missing
                        prev_missing = total_stock.dp_missing_qty or 0
                        new_missing_qty = prev_missing + diff
                        # Update the tray_quantity in TrayId
                        top_tray.tray_quantity = edited_tray_qty
                        top_tray.save(update_fields=['tray_quantity'])
                        print(f"✅ Updated top tray {top_tray.tray_id} qty from {original_qty} to {edited_tray_qty}")
                        missing_qty = new_missing_qty
                    else:
                        print("⚠️ Top tray not found for lot:", lot_id)
                        original_qty = total_stock.dp_physical_qty or total_stock.total_stock or 0
                        diff = (original_qty - edited_tray_qty)
                        if diff < 0:
                            diff = 0
                        prev_missing = total_stock.dp_missing_qty or 0
                        missing_qty = prev_missing + diff
                except ValueError:
                    return Response({"success": False, "error": "Edited tray qty must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            # --- NEW: Mark unverified trays as rejected ---
            unverified_trays = TrayId.objects.filter(lot_id=lot_id, IP_tray_verified=False)
            updated_count = unverified_trays.update(rejected_tray=True)
            if updated_count > 0:
                print(f"Marked {updated_count} unverified trays as rejected for lot {lot_id}")
            
                # --- Create IP_Rejection_ReasonStore instance for these trays ---
                from django.contrib.auth import get_user_model
                User = get_user_model()
                current_user = request.user
            
                # Calculate total_rejection_quantity as the sum of tray_quantity for these trays
                total_rejection_quantity = sum(tray.tray_quantity or 0 for tray in unverified_trays)
            
                IP_Rejection_ReasonStore.objects.create(
                    lot_id=lot_id,
                    user=current_user,
                    total_rejection_quantity=total_rejection_quantity
                )
                print(f"Created IP_Rejection_ReasonStore for lot {lot_id} with total_rejection_quantity={total_rejection_quantity}")
            # ...existing code...
            # --- Save missing qty and physical qty ---
            if missing_qty not in [None, ""]:
                try:
                    missing_qty = int(missing_qty)
                except ValueError:
                    return Response({"success": False, "error": "Missing quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

                if missing_qty > total_stock.total_stock:
                    return Response(
                        {"success": False, "error": "Missing quantity must be less than or equal to assigned quantity."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                total_stock.dp_missing_qty = missing_qty
                total_stock.dp_physical_qty = total_stock.total_stock - missing_qty
                total_stock.ip_onhold_picking = False

                # Optionally: Add verification timestamp and method
                from django.utils import timezone
                total_stock.ip_verification_timestamp = timezone.now()
                total_stock.ip_verification_method = "tray_scan_auto" if missing_qty == 0 else "manual_entry"

            total_stock.save()
            return Response({"success": True})

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
            
            # Set created_at to now
            total_stock_data.created_at = timezone.now()
            
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
            # Set created_at to now
            total_stock.created_at = timezone.now()

            total_stock.save(update_fields=[
                'rejected_ip_stock',
                'ip_onhold_picking',
                'last_process_module',
                'next_process_module',
                'created_at'
            ])
            
            # Create IP_Rejection_ReasonStore entry
            IP_Rejection_ReasonStore.objects.create(
                lot_id=lot_id,
                user=request.user,
                total_rejection_quantity=qty,
                batch_rejection=True
            )

            return Response({'success': True, 'message': 'Batch rejection saved.'})

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TrayRejectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            batch_id = data.get('batch_id')
            tray_rejections = data.get('tray_rejections', [])  # List of {reason_id, qty, tray_id}

            if not lot_id or not tray_rejections:
                return Response({'success': False, 'error': 'Missing lot_id or tray_rejections'}, status=400)

            # Get the TotalStockModel for this lot_id
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not total_stock_obj:
                return Response({'success': False, 'error': 'TotalStockModel not found'}, status=404)

            # Use dp_physical_qty if set and > 0, else use total_stock
            available_qty = total_stock_obj.dp_physical_qty 
            # Calculate total quantity from individual tray entries
            total_qty = sum(int(item.get('qty', 0)) for item in tray_rejections)
            
            # Check if total quantity exceeds available quantity
            if total_qty > available_qty:
                return Response({
                    'success': False,
                    'error': f'Total rejection quantity ({total_qty}) exceeds available quantity ({available_qty}).'
                }, status=400)

            # Save each tray scan to IP_Rejected_TrayScan and update TrayId
            for item in tray_rejections:
                qty = int(item.get('qty', 0))
                reason_id = item.get('reason_id')
                tray_id = item.get('tray_id', '')
                if qty > 0 and reason_id and tray_id:
                    try:
                        reason_obj = IP_Rejection_Table.objects.get(rejection_reason_id=reason_id)
                        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
                        if tray_obj:
                            # If tray has no lot_id, assign it now
                            if not tray_obj.lot_id:
                                tray_obj.lot_id = lot_id
                                tray_obj.batch_id = total_stock_obj.batch_id
                                tray_obj.tray_quantity = qty
                                tray_obj.save(update_fields=['lot_id', 'batch_id', 'tray_quantity'])
                            # Mark as rejected
                            tray_obj.rejected_tray = True
                            tray_obj.save(update_fields=['rejected_tray'])
                        # Save the rejection scan
                        IP_Rejected_TrayScan.objects.create(
                            lot_id=lot_id,
                            rejected_tray_quantity=qty,
                            rejection_reason=reason_obj,
                            user=request.user,
                            rejected_tray_id=tray_id
                        )
                    except IP_Rejection_Table.DoesNotExist:
                        print(f"Warning: Rejection reason {reason_id} not found")
                        continue

            # Group rejections by reason_id for IP_Rejection_ReasonStore
            reason_groups = {}
            for item in tray_rejections:
                reason_id = item.get('reason_id')
                qty = int(item.get('qty', 0))
                if reason_id and qty > 0:
                    if reason_id not in reason_groups:
                        reason_groups[reason_id] = 0
                    reason_groups[reason_id] += qty

            # Save to IP_Rejection_ReasonStore (grouped by reason)
            if reason_groups:
                reason_ids = list(reason_groups.keys())
                reasons = IP_Rejection_Table.objects.filter(rejection_reason_id__in=reason_ids)
                reason_store = IP_Rejection_ReasonStore.objects.create(
                    lot_id=lot_id,
                    user=request.user,
                    total_rejection_quantity=total_qty,
                    batch_rejection=False
                )
                reason_store.rejection_reason.set(reasons)

            # Update TotalStockModel
            total_stock_obj.ip_onhold_picking = True
            total_stock_obj.few_cases_accepted_Ip_stock = True
            total_stock_obj.dp_physical_qty = available_qty - total_qty
            # Set created_at to now
            total_stock_obj.created_at = timezone.now()
            total_stock_obj.save(update_fields=[
                'few_cases_accepted_Ip_stock',
                'ip_onhold_picking',
                'dp_physical_qty',
                'created_at'
            ])
            return Response({'success': True, 'message': 'Tray rejections saved.'})

        except Exception as e:
            print(f"Error in TrayRejectionAPIView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)

@require_GET
def reject_check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    current_lot_id = request.GET.get('lot_id', '')

    try:
        # Get the tray object if it exists
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()

        if not tray_obj:
            # Tray doesn't exist
            return JsonResponse({
                'exists': False,
                'error': 'Tray ID not found',
                'status_message': 'Not Found'
            })

        # ✅ NEW: Only allow if IP_tray_verified is True, unless new_tray is True
        if not getattr(tray_obj, 'IP_tray_verified', False):
            # Allow if new_tray is True
            if getattr(tray_obj, 'new_tray', False):
                pass  # Allow to proceed
            else:
                return JsonResponse({
                    'exists': False,
                    'error': 'Tray id is not verified',
                    'status_message': 'Tray id is not verified',
                    'tray_status': 'not_verified'
                })

        # ✅ NEW: Get current model's tray type for validation
        current_model_tray_type = None
        if current_lot_id:
            try:
                total_stock = TotalStockModel.objects.filter(lot_id=current_lot_id).first()
                if total_stock and total_stock.batch_id:
                    current_model_tray_type = total_stock.batch_id.tray_type
            except Exception as e:
                print(f"Error getting model tray type: {e}")

        # ✅ NEW VALIDATION: Check tray type matching
        scanned_tray_type = getattr(tray_obj, 'tray_type', 'Normal') or 'Normal'
        if current_model_tray_type and scanned_tray_type:
            if current_model_tray_type.lower() != scanned_tray_type.lower():
                return JsonResponse({
                    'exists': False,
                    'error': f'Wrong tray type',
                    'status_message': f'Wrong Type ({scanned_tray_type})',
                    'tray_status': 'wrong_tray_type',
                    'expected_type': current_model_tray_type,
                    'scanned_type': scanned_tray_type
                })

        # ✅ EXISTING VALIDATION: Check lot_id matching
        if tray_obj.lot_id:  # If tray has an existing lot_id
            if str(tray_obj.lot_id).strip() != str(current_lot_id).strip():
                # Tray belongs to different lot
                return JsonResponse({
                    'exists': False,
                    'error': 'Not in same lot',
                    'status_message': 'Different Lot',
                    'tray_status': 'different_lot'
                })

        # ✅ EXISTING VALIDATION: Check delink_tray and rejected_tray conditions
        if not tray_obj.delink_tray and tray_obj.rejected_tray:
            return JsonResponse({
                'exists': False,
                'error': 'Already rejected',
                'status_message': 'Already Rejected',
                'tray_status': 'rejected_not_delinked'
            })

        # ✅ EXISTING VALIDATION: Check if tray is already used in current process
        if tray_obj.lot_id == current_lot_id and tray_obj.rejected_tray:
            return JsonResponse({
                'exists': False,
                'error': 'Already scanned',
                'status_message': 'Already Scanned',
                'tray_status': 'already_rejected_in_lot'
            })

        # ✅ SUCCESS: Tray exists and passes all validations
        return JsonResponse({
            'exists': True,
            'status_message': f'Available ({scanned_tray_type})',
            'delink_tray': tray_obj.delink_tray,
            'rejected_tray': tray_obj.rejected_tray,
            'tray_status': 'available',
            'tray_type': scanned_tray_type
        })

    except Exception as e:
        return JsonResponse({
            'exists': False,
            'error': 'System error',
            'status_message': 'System Error'
        })

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
            total_stock.dp_missing_qty = 0
            total_stock.dp_physical_qty_edited = False
            total_stock.ip_onhold_picking = False
            total_stock.save(update_fields=[
                'dp_physical_qty',
                'dp_missing_qty',
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
        
        # ✅ UPDATED: Get top tray first, then other trays, and filter out trays with quantity 0
        top_tray = TrayId.objects.filter(
            batch_id__batch_id=batch_id,
            top_tray=True,
            tray_quantity__gt=0  # Only include if quantity > 0
        ).first()
        
        other_trays = TrayId.objects.filter(
            batch_id__batch_id=batch_id,
            top_tray=False,
            tray_quantity__gt=0  # Only include if quantity > 0
        ).order_by('id')
        
        data = []
        
        # Add top tray first if it exists
        if top_tray:
            data.append({
                's_no': 1,  # Always 1 for top tray
                'tray_id': top_tray.tray_id,
                'tray_quantity': top_tray.tray_quantity,
                'position': 0,  # Top position
                'is_top_tray': True
            })
        
        # Add other trays starting from position 2
        for idx, tray in enumerate(other_trays):
            data.append({
                's_no': idx + 2,  # Start from 2 since top tray is 1
                'tray_id': tray.tray_id,
                'tray_quantity': tray.tray_quantity,
                'position': idx + 1,  # Position after top tray
                'is_top_tray': False
            })
        
        return JsonResponse({'success': True, 'trays': data})
   
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
# ...existing code...
class IPSaveTrayDraftAPIView(APIView):
    """
    API View to save tray scan as draft and update quantities
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            total_lot_qty = data.get('total_lot_qty', 0)
            missing_qty = data.get('missing_qty', 0)
            physical_qty = data.get('physical_qty', 0)
            edited_tray_qty = data.get('edited_tray_qty')  # <-- Get edited qty from frontend

            if not lot_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'lot_id is required'
                }, status=400)
            
            # Find the TotalStockModel record by lot_id
            try:
                total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            except TotalStockModel.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Stock record not found for the provided lot_id'
                }, status=404)

            # Print before any edit
            print(f"Avant modification: dp_missing_qty={total_stock.dp_missing_qty}, dp_physical_qty={total_stock.dp_physical_qty}")

            # --- NEW LOGIC: If edited_tray_qty is provided, update TrayId and accumulate missing_qty ---
            if edited_tray_qty not in [None, ""]:
                try:
                    edited_tray_qty = int(edited_tray_qty)
                    if edited_tray_qty == 0:
                        print(f"⚠️ edited_tray_qty est zéro. dp_missing_qty={total_stock.dp_missing_qty}, dp_physical_qty={total_stock.dp_physical_qty}")
                    # Find the top tray for this lot
                    top_tray = TrayId.objects.filter(lot_id=lot_id, top_tray=True).first()
                    if top_tray:
                        prev_qty = top_tray.tray_quantity or 0
                        original_qty = prev_qty
                        diff = (original_qty - edited_tray_qty)
                        if diff < 0:
                            diff = 0  # Prevent negative missing
                        prev_missing = total_stock.dp_missing_qty or 0
                        new_missing_qty = prev_missing + diff

                        # Update the tray_quantity in TrayId
                        top_tray.tray_quantity = edited_tray_qty
                        top_tray.save(update_fields=['tray_quantity'])
                        print(f"✅ [Draft] Updated top tray {top_tray.tray_id} qty from {original_qty} to {edited_tray_qty}")
                        missing_qty = new_missing_qty
                    else:
                        print("⚠️ [Draft] Top tray not found for lot:", lot_id)
                        original_qty = total_stock.dp_physical_qty or total_stock.total_stock or 0
                        diff = (original_qty - edited_tray_qty)
                        if diff < 0:
                            diff = 0
                        prev_missing = total_stock.dp_missing_qty or 0
                        missing_qty = prev_missing + diff
                except ValueError:
                    return JsonResponse({"success": False, "error": "Edited tray qty must be an integer"}, status=400)

            # --- Save missing qty and physical qty ---
            total_stock.ip_onhold_picking = True
            if missing_qty > 0:
                total_stock.dp_missing_qty = missing_qty
                total_stock.dp_physical_qty = total_stock.total_stock - missing_qty
                total_stock.dp_physical_qty_edited = True  # Mark as edited

            total_stock.save(update_fields=[
                'ip_onhold_picking', 
                'dp_missing_qty', 
                'dp_physical_qty', 
                'dp_physical_qty_edited'
            ])
            
            return JsonResponse({
                'success': True, 
                'message': 'Tray scan saved as draft with accumulated missing quantity.',
                'lot_id': lot_id,
                'missing_qty': missing_qty,
                'physical_qty': total_stock.dp_physical_qty
            })
# ...existing code...
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False, 
                'error': f'Unexpected error occurred: {str(e)}'
            }, status=500)

# ✅ UPDATED: Modified get_accepted_tray_scan_data function for single top tray calculation
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accepted_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        # Get TotalStockModel data
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if not stock:
            return Response({'success': False, 'error': 'Stock not found'}, status=404)
        
        # Get model_no and tray_capacity
        model_no = stock.model_stock_no.model_no if stock.model_stock_no else ""
        tray_capacity = stock.batch_id.tray_capacity if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity') else 10
        
        # ✅ NEW: Calculate remaining quantity after rejections
        # Use dp_physical_qty if set and > 0, else use total_stock
        if stock.dp_physical_qty and stock.dp_physical_qty > 0:
            available_qty = stock.dp_physical_qty
        else:
            available_qty = stock.total_stock or 0
        
        # Get total rejection quantity for this lot
        total_rejection_qty = 0
        reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
        if reason_store:
            total_rejection_qty = reason_store.total_rejection_quantity or 0
        
        # ✅ NEW: Calculate remaining quantity and top tray quantity
        remaining_qty = available_qty - total_rejection_qty
        
        if remaining_qty <= 0:
            return Response({
                'success': False, 
                'error': 'No remaining quantity for accepted tray scan'
            }, status=400)
        
        # Calculate top tray quantity (remainder after dividing by tray capacity)
        top_tray_qty = remaining_qty % tray_capacity
        
        # If remainder is 0, it means we need full tray capacity for top tray
        if top_tray_qty == 0:
            top_tray_qty = tray_capacity
        
        # ✅ NEW: Check for existing draft data
        has_draft = IP_Accepted_TrayID_Store.objects.filter(lot_id=lot_id, is_draft=True).exists()
        
        # Get draft tray_id if exists
        draft_tray_id = ""
        if has_draft:
            draft_record = IP_Accepted_TrayID_Store.objects.filter(
                lot_id=lot_id, 
                is_draft=True
            ).first()
            if draft_record:
                draft_tray_id = draft_record.top_tray_id
                delink_tray_id = draft_record.delink_tray_id
                delink_tray_qty = draft_record.delink_tray_qty
        else:
            draft_tray_id = ""
            delink_tray_id = ""
            delink_tray_qty = None
        
        # Get verification status
        top_tray_verified = stock.ip_top_tray_qty_verified or False
        verified_tray_qty = stock.ip_verified_tray_qty or 0
        
        return Response({
            'success': True,
            'model_no': model_no,
            'tray_capacity': tray_capacity,
            'available_qty': available_qty,
            'total_rejection_qty': total_rejection_qty,
            'remaining_qty': remaining_qty,
            'top_tray_qty': top_tray_qty,  # ✅ NEW: Single top tray quantity
            'has_draft': has_draft,
            'draft_tray_id': draft_tray_id,  # ✅ NEW: Draft tray ID if exists
            'delink_tray_id': delink_tray_id,
            'delink_tray_qty': delink_tray_qty,
            'top_tray_verified': top_tray_verified,
            'verified_tray_qty': verified_tray_qty,
            # ✅ REMOVED: No longer sending rows array since we only need single top tray
        })
        
    except Exception as e:
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
                stock.created_at = timezone.now()  # Set created_at to now
                stock.save(update_fields=[
                    'accepted_tray_scan_status', 
                    'next_process_module', 
                    'last_process_module', 
                    'ip_onhold_picking',
                    'created_at'
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

class IS_Completed_Table(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Input_Screening/IS_Completed_Table.html'

    def get(self, request):
        from django.utils import timezone
        from datetime import datetime, timedelta

        user = request.user

        # Get all related brass_saved_time values for completed batches
        completed_batches = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0,
        ).values_list('batch_id', flat=True)

        # Get min/max brass_saved_time from TotalStockModel for these batches
        brass_time_qs = TotalStockModel.objects.filter(
            batch_id__batch_id__in=completed_batches
        )
        min_brass_time = brass_time_qs.order_by('brass_saved_time').values_list('brass_saved_time', flat=True).first()
        max_brass_time = brass_time_qs.order_by('-brass_saved_time').values_list('brass_saved_time', flat=True).first()

        # Default: yesterday and today based on brass_saved_time, fallback to system date if not found
        if min_brass_time and max_brass_time:
            today = max_brass_time.date()
            yesterday = today - timedelta(days=1)
        else:
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)

        # Get date filter parameters from request
        from_date_str = request.GET.get('from_date')
        to_date_str = request.GET.get('to_date')

        # Calculate date range
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

        # Convert dates to datetime objects for filtering (include full day)
        from_datetime = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
        to_datetime = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))

        # Get batch_ids where brass_saved_time is in range
        batch_ids_in_range = list(
            TotalStockModel.objects.filter(
                brass_saved_time__range=(from_datetime, to_datetime)
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
        
        dp_missing_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_missing_qty')[:1]
        
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
        
        # FIXED: Use a more explicit approach for the rejection quantity
        # Instead of trying to reference the lot_id directly, we'll get it step by step
        
        # 🔥 UPDATED: Build queryset with date filtering and existing filters
        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0,
            batch_id__in=batch_ids_in_range

        ).annotate(
            last_process_module=Subquery(last_process_module_subquery),
            next_process_module=Subquery(next_process_module_subquery),
            ip_person_qty_verified=Subquery(ip_person_qty_verified_subquery),
            dp_missing_qty=Subquery(dp_missing_qty_subquery),
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
            brass_saved_time=Subquery(TotalStockModel.objects.filter(
                batch_id=OuterRef('pk')
            ).values('brass_saved_time')[:1]),
            
        ).filter(
            Q(accepted_Ip_stock=True) |
            Q(rejected_ip_stock=True) |
            Q(few_cases_accepted_Ip_stock=True)
        ).order_by('-brass_saved_time')

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
            'dp_missing_qty',
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
            'brass_saved_time',
            'plating_stk_no',
            'polishing_stk_no',
            'category',
            'version__version_internal',
        ))

        # MANUAL APPROACH: Add rejection quantities manually
        # Since the subquery approach isn't working, let's add it manually
        for data in master_data:
            stock_lot_id = data.get('stock_lot_id')
            
            # Get rejection quantity manually
            if stock_lot_id:
                try:
                    rejection_record = IP_Rejection_ReasonStore.objects.filter(
                        lot_id=stock_lot_id
                    ).first()
                    
                    if rejection_record:
                        data['ip_rejection_total_qty'] = rejection_record.total_rejection_quantity
                        print(f"Found rejection for {stock_lot_id}: {rejection_record.total_rejection_quantity}")
                    else:
                        data['ip_rejection_total_qty'] = 0
                        print(f"No rejection found for {stock_lot_id}")
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
            
            # Fallback logic for accepted quantity
            total_ip_accepted_quantity = data.get('total_ip_accepted_quantity')
            lot_id = data.get('stock_lot_id')
            accepted_tray_quantity = 0

            if not total_ip_accepted_quantity or total_ip_accepted_quantity == 0:
                # Fetch total_rejection_quantity from IP_Rejection_ReasonStore
                total_rejection_qty = 0
                rejection_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
                if rejection_store and rejection_store.total_rejection_quantity:
                    total_rejection_qty = rejection_store.total_rejection_quantity
            
                # Fetch dp_physical_qty from TotalStockModel
                dp_physical_qty = 0
                total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
                if total_stock_obj and total_stock_obj.dp_physical_qty:
                    dp_physical_qty = total_stock_obj.dp_physical_qty
            
                # Calculate display_accepted_qty
                data['display_accepted_qty'] = max(dp_physical_qty - total_rejection_qty, 0)
            else:
                data['display_accepted_qty'] = total_ip_accepted_quantity
        
        print("=== END MANUAL LOOKUP ===")
        
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
        
        dp_missing_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_missing_qty')[:1]
        
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
            dp_missing_qty=Subquery(dp_missing_qty_subquery),
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
            Q(accepted_Ip_stock=True)
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
            'dp_missing_qty',
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
            
            # Get rejection quantity manually
            if stock_lot_id:
                try:
                    rejection_record = IP_Rejection_ReasonStore.objects.filter(
                        lot_id=stock_lot_id
                    ).first()
                    
                    if rejection_record:
                        data['ip_rejection_total_qty'] = rejection_record.total_rejection_quantity
                        print(f"Found rejection for {stock_lot_id}: {rejection_record.total_rejection_quantity}")
                    else:
                        data['ip_rejection_total_qty'] = 0
                        print(f"No rejection found for {stock_lot_id}")
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
        
        dp_missing_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('dp_missing_qty')[:1]
        
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
            dp_missing_qty=Subquery(dp_missing_qty_subquery),
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
            Q(few_cases_accepted_Ip_stock=True)
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
            'dp_missing_qty',
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
        for data in master_data:
            stock_lot_id = data.get('stock_lot_id')
            
            # Get rejection quantity manually
            first_letters = []
            if stock_lot_id:
                try:
                    rejection_record = IP_Rejection_ReasonStore.objects.filter(
                        lot_id=stock_lot_id
                    ).first()
                    data['batch_rejection'] = rejection_record.batch_rejection if rejection_record else False

                    if rejection_record:
                        reasons = rejection_record.rejection_reason.all()
                        first_letters = [r.rejection_reason.strip()[0].upper() for r in reasons if r.rejection_reason]
                    data['rejection_reason_letters'] = first_letters       
                    if rejection_record:
                        data['ip_rejection_total_qty'] = rejection_record.total_rejection_quantity
                        print(f"Found rejection for {stock_lot_id}: {rejection_record.total_rejection_quantity}")
                    else:
                        data['ip_rejection_total_qty'] = 0
                        print(f"No rejection found for {stock_lot_id}")
                except Exception as e:
                    print(f"Error getting rejection for {stock_lot_id}: {str(e)}")
                    data['ip_rejection_total_qty'] = 0
            else:
                data['ip_rejection_total_qty'] = 0
                print(f"No stock_lot_id for batch {data.get('batch_id')}")
                data['batch_rejection'] = False
            
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
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
        if not reason_store:
            return Response({'success': True, 'reasons': []})

        reasons = reason_store.rejection_reason.all()
        total_qty = reason_store.total_rejection_quantity

        if reason_store.batch_rejection:
            if reasons.exists():
                data = [{
                    'reason': r.rejection_reason,
                    'qty': total_qty
                } for r in reasons]
            else:
                # No reasons recorded for batch rejection
                data = [{
                    'reason': 'Batch rejection: No individual reasons recorded',
                    'qty': total_qty
                }]
        else:
            data = [{
                'reason': r.rejection_reason,
                'qty': total_qty
            } for r in reasons]

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
    Get delink tray data based on latest rejection reason store for the popup lot.
    Only show as many rows as needed to cover total_rejection_quantity / tray_capacity.
    """
    try:
        # 1. Get the latest IP_Rejection_ReasonStore record
        reason_store = IP_Rejection_ReasonStore.objects.order_by('-id').first()
        if not reason_store:
            return Response({'success': False, 'error': 'No rejection reason found.'}, status=404)

        lot_id = reason_store.lot_id
        total_rejection_qty = reason_store.total_rejection_quantity or 0

        # 2. Get tray_capacity from TotalStockModel
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        tray_capacity = stock.batch_id.tray_capacity if stock and stock.batch_id and hasattr(stock.batch_id, 'tray_capacity') else 10

        # 3. Calculate number of rows to show
        num_rows = (total_rejection_qty // tray_capacity) + (1 if total_rejection_qty % tray_capacity else 0)

        # 4. Get all unscanned trays for this lot
        unscanned_trays = TrayId.objects.filter(
            lot_id=lot_id,
            scanned=False
        ).values('tray_id', 'tray_quantity', 'id').order_by('id')

        # 5. Limit to num_rows
        delink_data = []
        for idx, tray in enumerate(unscanned_trays):
            if idx >= num_rows:
                break
            delink_data.append({
                'sno': idx + 1,
                'tray_id': tray['tray_id'],
                'tray_quantity': tray['tray_quantity'] or 0,
                'id': tray['id']
            })

        return Response({
            'success': True,
            'delink_trays': delink_data,
            'total_count': len(delink_data),
            'lot_id': lot_id,
            'total_rejection_qty': total_rejection_qty,
            'tray_capacity': tray_capacity,
            'num_rows': num_rows
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)


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
