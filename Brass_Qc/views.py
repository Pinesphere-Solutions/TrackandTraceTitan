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
from rest_framework.permissions import IsAuthenticated

class BrassPickTableView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Brass_Qc/Brass_PickTable.html'

    def get(self, request):
        user = request.user
        is_admin = user.groups.filter(name='Admin').exists() if user.is_authenticated else False

                # ✅ NEW: Add subquery to check for draft status
        has_draft_subquery = Exists(
            Brass_QC_Draft_Store.objects.filter(
                lot_id=OuterRef('stock_lot_id')
            )
        )
        
        # ✅ NEW: Add subquery to get draft type
        draft_type_subquery = Brass_QC_Draft_Store.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('draft_type')[:1]
        # Use your Brass QC models here if different
        
       
        accepted_exists = Exists(
            TotalStockModel.objects.filter(
                batch_id=OuterRef('pk')
            ).filter(
                Q(accepted_Ip_stock=True) | 
                Q(few_cases_accepted_Ip_stock=True, ip_onhold_picking=False)
            )
        )
        
        
        brass_rejection_reasons = Brass_QC_Rejection_Table.objects.all()

        # Add the subquery for brass_physical_qty_edited
        brass_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_physical_qty_edited')[:1]
        
        send_brass_qc_subquery=TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('send_brass_qc')[:1]
        
        iqf_acceptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_acceptance')[:1]
        
        brass_qc_accptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_accptance')[:1]
        
        brass_accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_accepted_tray_scan_status')[:1]
        
        brass_qc_rejection_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_rejection')[:1]
        
        brass_qc_few_cases_accptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_few_cases_accptance')[:1]
        
        brass_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_onhold_picking')[:1]
        
        brass_rejection_qty_subquery = Brass_QC_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('total_rejection_quantity')[:1]

       
        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0
        ).annotate(
            last_process_module=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('last_process_module')[:1]
            ),
            next_process_module=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('next_process_module')[:1]
            ),
            wiping_required=F('model_stock_no__wiping_required'),
            accepted_exists=accepted_exists,
            stock_lot_id=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('lot_id')[:1]
            ),
            brass_qc_accepted_qty_verified=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_qc_accepted_qty_verified')[:1]
            ),
            brass_qc_accepted_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_qc_accepted_qty')[:1]
            ),
            last_process_date_time=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('last_process_date_time')[:1]
            ),
            brass_missing_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_missing_qty')[:1]
            ),
            brass_physical_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_physical_qty')[:1]
            ),
            brass_physical_qty_edited=brass_physical_qty_edited_subquery,
            brass_qc_accptance=brass_qc_accptance_subquery,
            brass_accepted_tray_scan_status=brass_accepted_tray_scan_status_subquery,
            brass_qc_rejection=brass_qc_rejection_subquery,
            brass_qc_few_cases_accptance=brass_qc_few_cases_accptance_subquery,
            brass_onhold_picking=brass_onhold_picking_subquery,
            iqf_acceptance=iqf_acceptance_subquery,
            send_brass_qc=send_brass_qc_subquery,
            brass_rejection_total_qty=Subquery(brass_rejection_qty_subquery),
        
            accepted_Ip_stock=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('accepted_Ip_stock')[:1]
            ),
            rejected_ip_stock=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('rejected_ip_stock')[:1]
            ),
            few_cases_accepted_Ip_stock=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('few_cases_accepted_Ip_stock')[:1]
            ),
            accepted_tray_scan_status=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('accepted_tray_scan_status')[:1]
            ),
            Bq_pick_remarks=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('Bq_pick_remarks')[:1]
            ),
            total_IP_accpeted_quantity=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('total_IP_accpeted_quantity')[:1]
            ),
            brass_hold_lot=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_hold_lot')[:1]
            ),
        
            brass_holding_reason=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_holding_reason')[:1]
            ),
            brass_release_lot=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_release_lot')[:1]
            ),
            brass_release_reason=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_release_reason')[:1]
            ),
            # ✅ NEW: Add draft status annotations
            has_draft=has_draft_subquery,
            draft_type=draft_type_subquery,
        
        ).filter(
            Q(brass_qc_accptance__isnull=True) | Q(brass_qc_accptance=False),
            Q(brass_qc_rejection__isnull=True) | Q(brass_qc_rejection=False),
            ~Q(brass_qc_few_cases_accptance=True, brass_onhold_picking=False),
            # ✅ UPDATED: Only show records with accepted_Ip_stock=True
            accepted_exists=True
        )
        # Pagination
        queryset = queryset.order_by('-date_time', '-batch_id')  # or any unique field

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
            'total_IP_accpeted_quantity',
            'tray_capacity',
            'Moved_to_D_Picker',
            'last_process_module',
            'next_process_module',
            'Draft_Saved',
            'wiping_required',
            'stock_lot_id',
            'brass_qc_accepted_qty_verified',
            'brass_qc_accepted_qty',
            'brass_rejection_total_qty',
            'brass_missing_qty',
            'brass_physical_qty',
            'brass_physical_qty_edited',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'Bq_pick_remarks',
            'brass_qc_accptance',
            'brass_accepted_tray_scan_status',
            'brass_qc_rejection',
            'brass_qc_few_cases_accptance',
            'brass_onhold_picking',
            'iqf_acceptance',
            'send_brass_qc',
            'last_process_date_time',
            'plating_stk_no',
            'polishing_stk_no',
            'category',
            'brass_hold_lot',
            'brass_holding_reason',
            'brass_release_lot',
            'brass_release_reason',
            'has_draft',
            'draft_type',

        ))

       
        for data in master_data:   
            total_IP_accpeted_quantity = data.get('total_IP_accpeted_quantity', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            
            # ✅ FIRST: Calculate display_accepted_qty
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
        
            # ✅ THEN: Calculate no_of_trays based on display_accepted_qty instead of total_IP_accpeted_quantity
            display_qty = data.get('display_accepted_qty', 0)
            if tray_capacity > 0 and display_qty > 0:
                data['no_of_trays'] = math.ceil(display_qty / tray_capacity)
            else:
                data['no_of_trays'] = 0
        
            # Get the ModelMasterCreation instance
            mmc = ModelMasterCreation.objects.filter(batch_id=data['batch_id']).first()
            images = []
            if mmc:
                model_master = mmc.model_stock_no
                for img in model_master.images.all():
                    if img.master_image:
                        images.append(img.master_image.url)
            if not images:
                images = [static('assets/images/imagePlaceholder.png')]
            data['model_images'] = images
        
            # Add available_qty for each row
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock_obj:
                if total_stock_obj.brass_physical_qty and total_stock_obj.brass_physical_qty > 0:
                    data['available_qty'] = total_stock_obj.brass_physical_qty
                else:
                    data['available_qty'] = total_stock_obj.total_IP_accpeted_quantity
            else:
                data['available_qty'] = 0
        
           
        print(f"[DEBUG] Master data loaded with {len(master_data)} entries.")

        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'is_admin': is_admin,
            'brass_rejection_reasons':brass_rejection_reasons,
                'pick_table_count': len(master_data),  # <-- Add this line

        }
        return Response(context, template_name=self.template_name)
    
@method_decorator(csrf_exempt, name='dispatch')
class BrassSaveHoldUnholdReasonAPIView(APIView):
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
                obj.brass_holding_reason = remark
                obj.brass_hold_lot = True
                obj.brass_release_reason = ''
                obj.brass_release_lot = False
            elif action == 'unhold':
                obj.brass_release_reason = remark
                obj.brass_hold_lot = False
                obj.brass_release_lot = True

            obj.save(update_fields=['brass_holding_reason', 'brass_release_reason', 'brass_hold_lot', 'brass_release_lot'])
            return JsonResponse({'success': True, 'message': 'Reason saved.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
          
    
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')  
class BrassSaveIPCheckboxView(APIView):
        def post(self, request, format=None):
            try:
                data = request.data
                lot_id = data.get("lot_id")
                missing_qty = data.get("missing_qty")
    
                if not lot_id:
                    return Response({"success": False, "error": "Lot ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
                total_stock = TotalStockModel.objects.get(lot_id=lot_id)
                total_stock.brass_qc_accepted_qty_verified = True
    
                # ✅ UPDATED: Calculate display_accepted_qty instead of using total_IP_accpeted_quantity
                display_accepted_qty = 0
                
                if total_stock.total_IP_accpeted_quantity and total_stock.total_IP_accpeted_quantity > 0:
                    # Use stored accepted quantity if available
                    display_accepted_qty = total_stock.total_IP_accpeted_quantity
                else:
                    # Calculate from total_stock - total_rejection_qty (ignoring dp_missing_qty)
                    total_rejection_qty = 0
                    rejection_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
                    if rejection_store and rejection_store.total_rejection_quantity:
                        total_rejection_qty = rejection_store.total_rejection_quantity
    
                    if total_rejection_qty > 0:
                        # Calculate: total_stock - rejection_qty
                        display_accepted_qty = max(total_stock.total_stock - total_rejection_qty, 0)
                    else:
                        # No rejections = 0 accepted
                        display_accepted_qty = 0
    
                if missing_qty not in [None, ""]:
                    try:
                        missing_qty = int(missing_qty)
                    except ValueError:
                        return Response({"success": False, "error": "Missing quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
    
                    # ✅ UPDATED: Validate against display_accepted_qty instead of total_IP_accpeted_quantity
                    if missing_qty > display_accepted_qty:
                        return Response(
                            {"success": False, "error": f"Missing quantity must be less than or equal to display accepted quantity ({display_accepted_qty})."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
    
                    # ✅ UPDATED: Calculate brass_physical_qty using display_accepted_qty
                    total_stock.brass_missing_qty = missing_qty
                    total_stock.brass_physical_qty = display_accepted_qty - missing_qty
    
                total_stock.save()
                return Response({"success": True})
    
            except TotalStockModel.DoesNotExist:
                return Response({"success": False, "error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)
    
            except Exception as e:
                traceback.print_exc()   
                return Response({"success": False, "error": "Unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        def get(self, request, format=None):
            return Response(
                {"success": False, "error": "Invalid request method."},
                status=status.HTTP_400_BAD_REQUEST
            )  
        
@method_decorator(csrf_exempt, name='dispatch')
class BrassSaveIPPickRemarkAPIView(APIView):
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
            batch_obj.Bq_pick_remarks = remark
            batch_obj.save(update_fields=['Bq_pick_remarks'])
            return JsonResponse({'success': True, 'message': 'Remark saved'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BQDeleteBatchAPIView(APIView):
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
class BQ_Accepted_form(APIView):

    def post(self, request, format=None):
        data = request.data
        lot_id = data.get("stock_lot_id")
        try:
            total_stock_data = TotalStockModel.objects.get(lot_id=lot_id)
            
            # If iqf_acceptance is True, set it to False and set send_brass_qc = True
            if total_stock_data.iqf_acceptance:
                total_stock_data.iqf_acceptance = False
                total_stock_data.send_brass_qc = True
                total_stock_data.brass_qc_few_cases_accptance =False
                total_stock_data.brass_qc_rejection =False
                
            total_stock_data.brass_qc_accptance = True
    
            # Use brass_physical_qty if set and > 0, else use total_stock
            physical_qty = total_stock_data.brass_physical_qty

            total_stock_data.brass_qc_accepted_qty = physical_qty
    
            # Update process modules
            total_stock_data.next_process_module = "Jig Loading"
            total_stock_data.last_process_module = "Brass QC"
            total_stock_data.bq_last_process_date_time = timezone.now()  # Set the last process date/time
            
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
class BQBatchRejectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            lot_id = data.get('lot_id')  # <-- get lot_id from POST
            total_qty = data.get('total_qty', 0)
            lot_rejected_comment = data.get('lot_rejected_comment', '').strip()  # <-- NEW: Get lot rejection remarks

            # Validate required fields
            if not batch_id or not lot_id:
                return Response({'success': False, 'error': 'Missing batch_id or lot_id'}, status=400)
            
            # ✅ NEW: Validate lot rejection remarks (required for batch rejection)
            if not lot_rejected_comment:
                return Response({'success': False, 'error': 'Lot rejection remarks are required for batch rejection'}, status=400)

            # Get ModelMasterCreation by batch_id string
            mmc = ModelMasterCreation.objects.filter(batch_id=batch_id).first()
            if not mmc:
                return Response({'success': False, 'error': 'Batch not found'}, status=404)

            # Get TotalStockModel using lot_id (not batch_id)
            total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not total_stock:
                return Response({'success': False, 'error': 'TotalStockModel not found'}, status=404)

            # Get brass_physical_qty if set and > 0, else use total_stock
            qty = total_stock.brass_physical_qty 

            # Set brass_qc_rejection = True
            total_stock.brass_qc_rejection = True
            total_stock.last_process_module = "Brass QC"
            total_stock.next_process_module = "Jig Loading"
            total_stock.bq_last_process_date_time = timezone.now()  # Set the last process date/time
            total_stock.save(update_fields=['brass_qc_rejection', 'last_process_module', 'next_process_module', 'bq_last_process_date_time'])
            
            updated_trays_count = TrayId.objects.filter(lot_id=lot_id).update(brass_rejected_tray=True)

            # ✅ UPDATED: Create Brass_QC_Rejection_ReasonStore entry with lot rejection remarks
            Brass_QC_Rejection_ReasonStore.objects.create(
                lot_id=lot_id,
                user=request.user,
                total_rejection_quantity=qty,
                batch_rejection=True,
                lot_rejected_comment=lot_rejected_comment  # <-- NEW: Save lot rejection remarks
            )

            return Response({'success': True, 'message': 'Batch rejection saved with remarks.'})

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BQTrayRejectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            batch_id = data.get('batch_id')
            tray_rejections = data.get('tray_rejections', [])  # List of {reason_id, qty, tray_id}

            print(f"🔍 [BQTrayRejectionAPIView] Received tray_rejections: {tray_rejections}")
            print(f"🔍 [BQTrayRejectionAPIView] Lot ID: {lot_id}, Batch ID: {batch_id}")

            if not lot_id or not tray_rejections:
                return Response({'success': False, 'error': 'Missing lot_id or tray_rejections'}, status=400)

            # Get the TotalStockModel for this lot_id
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if not total_stock_obj:
                return Response({'success': False, 'error': 'TotalStockModel not found'}, status=404)

            # Use brass_physical_qty if set and > 0, else use total_IP_accpeted_quantity
            available_qty = total_stock_obj.brass_physical_qty 
            
            # Calculate the running total and check for exceeding
            running_total = 0
            for idx, item in enumerate(tray_rejections):
                qty = int(item.get('qty', 0))
                running_total += qty
                if running_total > available_qty:
                    return Response({
                        'success': False,
                        'error': f'Quantity exceeds available ({available_qty}).'
                    }, status=400)

            # ✅ ENHANCED: Process each tray rejection INDIVIDUALLY with detailed logging
            total_qty = 0
            saved_rejections = []
            reason_ids_used = set()  # Track unique reason IDs for summary
            
            print(f"🔍 [BQTrayRejectionAPIView] Processing {len(tray_rejections)} individual tray rejections...")
            
            # ✅ CRITICAL: Process each rejection individually (no grouping)
            for idx, item in enumerate(tray_rejections):
                tray_id = item.get('tray_id', '').strip()
                reason_id = item.get('reason_id', '').strip()
                qty = int(item.get('qty', 0))
                
                print(f"🔍 [BQTrayRejectionAPIView] Processing rejection {idx + 1}:")
                print(f"   - Tray ID: '{tray_id}'")
                print(f"   - Reason ID: '{reason_id}'")
                print(f"   - Quantity: {qty}")
                
                if qty <= 0:
                    print(f"   ⚠️ Skipping - zero or negative quantity")
                    continue
                    
                if not tray_id or not reason_id:
                    print(f"   ⚠️ Skipping - missing tray_id or reason_id")
                    continue
                
                try:
                    reason_obj = Brass_QC_Rejection_Table.objects.get(rejection_reason_id=reason_id)
                    print(f"   ✅ Found rejection reason: {reason_obj.rejection_reason}")
                    
                    # ✅ CREATE INDIVIDUAL RECORD FOR EACH TRAY + REASON COMBINATION
                    rejection_record = Brass_QC_Rejected_TrayScan.objects.create(
                        lot_id=lot_id,
                        rejected_tray_quantity=qty,  # Individual tray quantity
                        rejection_reason=reason_obj,
                        user=request.user,
                        rejected_tray_id=tray_id  # Individual tray ID
                    )
                    
                    saved_rejections.append({
                        'record_id': rejection_record.id,
                        'tray_id': tray_id,
                        'qty': qty,
                        'reason': reason_obj.rejection_reason,
                        'reason_id': reason_id
                    })
                    
                    total_qty += qty
                    reason_ids_used.add(reason_id)
                    
                    print(f"   ✅ SAVED rejection record ID {rejection_record.id}: tray_id={tray_id}, qty={qty}, reason={reason_obj.rejection_reason}")
                    
                except Brass_QC_Rejection_Table.DoesNotExist:
                    print(f"   ❌ Rejection reason {reason_id} not found")
                    return Response({
                        'success': False,
                        'error': f'Rejection reason {reason_id} not found'
                    }, status=400)
                except Exception as e:
                    print(f"   ❌ Error creating rejection record: {e}")
                    return Response({
                        'success': False,
                        'error': f'Error creating rejection record: {str(e)}'
                    }, status=500)

            if not saved_rejections:
                return Response({
                    'success': False,
                    'error': 'No valid rejections were processed'
                }, status=400)

            # ✅ Create ONE summary record for the lot (with all unique rejection reasons)
            if reason_ids_used:
                reasons = Brass_QC_Rejection_Table.objects.filter(rejection_reason_id__in=list(reason_ids_used))
                
                reason_store = Brass_QC_Rejection_ReasonStore.objects.create(
                    lot_id=lot_id,
                    user=request.user,
                    total_rejection_quantity=total_qty,
                    batch_rejection=False
                )
                reason_store.rejection_reason.set(reasons)
                
                print(f"✅ [BQTrayRejectionAPIView] Created summary record: total_qty={total_qty}, reasons={len(reasons)}")

            # ✅ Update TrayId records for ALL individual tray IDs
            unique_tray_ids = list(set([item['tray_id'] for item in saved_rejections]))
            updated_tray_count = 0
            
            print(f"🔍 [BQTrayRejectionAPIView] Updating TrayId records for {len(unique_tray_ids)} unique trays: {unique_tray_ids}")
            
            for tray_id in unique_tray_ids:
                tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
                if tray_obj:
                    # Calculate total quantity for this specific tray across all its rejections
                    tray_total_qty = sum([item['qty'] for item in saved_rejections if item['tray_id'] == tray_id])
                    
                    # Check for new_tray flag
                    is_new_tray = getattr(tray_obj, 'new_tray', False)
                    print(f"🔍 [BQTrayRejectionAPIView] Updating tray {tray_id}: new_tray={is_new_tray}, total_qty={tray_total_qty}")
                    
                    # Update fields
                    if is_new_tray:
                        tray_obj.lot_id = lot_id  # Assign to selected lot_id if not already
                        tray_obj.brass_rejected_tray = True
                        tray_obj.top_tray = False
                        tray_obj.tray_quantity = tray_total_qty  # Save the total quantity for this tray
                        tray_obj.save(update_fields=['lot_id', 'brass_rejected_tray', 'top_tray', 'tray_quantity'])
                        print(f"✅ [BQTrayRejectionAPIView] Updated NEW tray {tray_id}: lot_id={lot_id}, brass_rejected_tray=True, tray_quantity={tray_total_qty}")
                    else:
                        # For existing trays, just mark as rejected
                        tray_obj.brass_rejected_tray = True
                        tray_obj.top_tray = False
                        tray_obj.save(update_fields=['brass_rejected_tray', 'top_tray'])
                        print(f"✅ [BQTrayRejectionAPIView] Updated EXISTING tray {tray_id}: brass_rejected_tray=True")
                    
                    updated_tray_count += 1
                else:
                    print(f"⚠️ [BQTrayRejectionAPIView] Tray {tray_id} not found in TrayId table")
            
            print(f"✅ [BQTrayRejectionAPIView] Updated {updated_tray_count} tray IDs as rejected")

            # Set brass_qc_few_cases_accptance = True
            total_stock_obj.brass_onhold_picking = True
            total_stock_obj.brass_qc_few_cases_accptance = True
            total_stock_obj.brass_qc_accepted_qty = available_qty - total_qty
            total_stock_obj.bq_last_process_date_time = timezone.now()  # Set the last process date/time

            total_stock_obj.save(update_fields=['brass_qc_few_cases_accptance', 'brass_onhold_picking', 'brass_qc_accepted_qty', 'bq_last_process_date_time'])

            # ✅ ENHANCED: Return detailed information about what was saved
            return Response({
                'success': True, 
                'message': f'Tray rejections saved: {len(saved_rejections)} individual records created for {len(unique_tray_ids)} trays.',
                'saved_rejections': saved_rejections,
                'total_qty': total_qty,
                'total_records': len(saved_rejections),
                'unique_tray_ids': unique_tray_ids,
                'updated_tray_count': updated_tray_count
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)

@require_GET
def brass_reject_check_tray_id(request):
    """
    Check if tray_id exists and is valid for brass QC rejection
    Only allow:
    1. Trays with same lot_id that are verified and not rejected
    2. New trays without lot_id assignment
    """
    tray_id = request.GET.get('tray_id', '').strip()
    lot_id = request.GET.get('lot_id', '').strip()  # This is your stock_lot_id
    print(f"DEBUG: Checking tray_id={tray_id}, lot_id={lot_id}")  # Debug log
    if not tray_id:
        return JsonResponse({'exists': False, 'error': 'Tray ID is required'})
    
    try:
        # Get the tray object if it exists
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        
        if not tray_obj:
            return JsonResponse({
                'exists': False,
                'error': 'Tray ID not found',
                'status_message': 'Not Found'
            })

        # ✅ CHECK 1: For new trays without lot_id, show "New Tray Available"
        is_new_tray = getattr(tray_obj, 'new_tray', False) or not tray_obj.lot_id or tray_obj.lot_id == '' or tray_obj.lot_id is None
        
        if is_new_tray:
            return JsonResponse({
                'exists': True,
                'status_message': 'New Tray Available',
                'validation_type': 'new_tray'
            })

        # ✅ CHECK 2: For existing trays, must belong to same lot
        if tray_obj.lot_id:
            if str(tray_obj.lot_id).strip() != str(lot_id).strip():
                return JsonResponse({
                    'exists': False,
                    'error': 'Different lot',
                    'status_message': 'Different Lot'
                })
        else:
            # This case should be caught by CHECK 1, but just in case
            return JsonResponse({
                'exists': True,
                'status_message': 'New Tray Available',
                'validation_type': 'new_tray'
            })

        # ✅ CHECK 3: Must NOT be already rejected
        if hasattr(tray_obj, 'brass_rejected_tray') and tray_obj.brass_rejected_tray:
            return JsonResponse({
                'exists': False,
                'error': 'Already rejected',
                'status_message': 'Already Rejected'
            })

        # ✅ CHECK 4: Must NOT be in Brass_QC_Rejected_TrayScan for this lot
        already_rejected_in_brass = Brass_QC_Rejected_TrayScan.objects.filter(
            lot_id=lot_id,
            rejected_tray_id=tray_id
        ).exists()
        
        if already_rejected_in_brass:
            return JsonResponse({
                'exists': False,
                'error': 'Already rejected in Brass QC',
                'status_message': 'Already Rejected'
            })

        # ✅ SUCCESS: Tray is valid for brass QC rejection
        return JsonResponse({
            'exists': True,
            'status_message': 'Available for Rejection',
            'validation_type': 'existing_valid',
            'tray_quantity': getattr(tray_obj, 'tray_quantity', 0) or 0
        })
        
    except Exception as e:
        return JsonResponse({
            'exists': False,
            'error': 'System error',
            'status_message': 'System Error'
        })

# Tray ID Allowance based on condition in rejection

@require_GET
def brass_reject_check_tray_id_simple(request):
    """
    Enhanced tray validation for Brass QC: Check if existing tray rejection can accommodate remaining pieces
    with proper rearrangement logic
    """
    tray_id = request.GET.get('tray_id', '')
    current_lot_id = request.GET.get('lot_id', '')
    rejection_qty = int(request.GET.get('rejection_qty', 0))
    
    # ✅ NEW: Get current session allocations from frontend
    current_session_allocations_str = request.GET.get('current_session_allocations', '[]')
    
    print(f"[Brass Simple Validation] tray_id: {tray_id}, lot_id: {current_lot_id}, qty: {rejection_qty}")
    print(f"[Brass Simple Validation] Current session allocations: {current_session_allocations_str}")

    try:
        # Parse current session allocations
        try:
            current_session_allocations = json.loads(current_session_allocations_str)
        except:
            current_session_allocations = []
        
        # Get tray object
        from modelmasterapp.models import TrayId
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        
        # Check if tray_id exists
        if not tray_obj:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Tray ID not found',
                'status_message': 'Not Found'
            })

        # ✅ CRITICAL CHECK: Reject if already rejected in Input Screening
        if hasattr(tray_obj, 'rejected_tray') and tray_obj.rejected_tray == True:
            print(f"[Brass Simple Validation] BLOCKED: Tray {tray_id} has rejected_tray=True (Input Screening rejection)")
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Already rejected in Input Screening',
                'status_message': 'Already Rejected in Input Screening'
            })

        # ✅ CRITICAL CHECK: Reject if already rejected in Brass QC  
        if hasattr(tray_obj, 'brass_rejected_tray') and tray_obj.brass_rejected_tray == True:
            print(f"[Brass Simple Validation] BLOCKED: Tray {tray_id} has brass_rejected_tray=True (Brass QC rejection)")
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Already rejected in Brass QC',
                'status_message': 'Already Rejected in Brass QC'
            })

        # ✅ Debug: Print tray rejection status
        print(f"[Brass Simple Validation] Tray {tray_id} rejection status:")
        print(f"  - rejected_tray: {getattr(tray_obj, 'rejected_tray', 'Not found')}")
        print(f"  - brass_rejected_tray: {getattr(tray_obj, 'brass_rejected_tray', 'Not found')}")

        # ✅ Check if it's marked as new_tray in database
        is_new_tray = getattr(tray_obj, 'new_tray', False)
        
        # ✅ Also check if lot_id is empty/null (indicates new tray)
        if not tray_obj.lot_id or tray_obj.lot_id == '' or tray_obj.lot_id is None:
            is_new_tray = True
        
        print(f"[Brass Simple Validation] Tray found in DB - new_tray flag: {getattr(tray_obj, 'new_tray', False)}, lot_id: '{tray_obj.lot_id}', is_new_tray: {is_new_tray}")

        # ✅ NEW TRAY: Always allow (any quantity)
        if is_new_tray:
            return JsonResponse({
                'exists': True,
                'valid_for_rejection': True,
                'status_message': 'New Tray Available',
                'validation_type': 'new_tray'
            })

        # Basic validations for EXISTING trays
        if not getattr(tray_obj, 'IP_tray_verified', False):
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Tray not verified',
                'status_message': 'Not Verified'
            })

        # Check if already rejected in Brass QC scan records
        if Brass_QC_Rejected_TrayScan.objects.filter(
            lot_id=current_lot_id,
            rejected_tray_id=tray_id
        ).exists():
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Already rejected in Brass QC',
                'status_message': 'Already Rejected'
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
            # This should be caught as new_tray above, but just in case
            return JsonResponse({
                'exists': True,
                'valid_for_rejection': True,
                'status_message': 'New Tray Available',
                'validation_type': 'new_tray'
            })

        # ✅ FIXED: Continue with space validation for existing trays
        # Get original distribution and capacities
        original_distribution = get_brass_original_tray_distribution(current_lot_id)
        original_capacities = get_brass_tray_capacities_for_lot(current_lot_id)
        
        print(f"[Brass Simple Validation] Original distribution: {original_distribution}")
        print(f"[Brass Simple Validation] Original capacities: {original_capacities}")
        
        # Apply only SAVED rejections (not current session)
        available_quantities = original_distribution.copy()
        saved_rejections = Brass_QC_Rejected_TrayScan.objects.filter(lot_id=current_lot_id).order_by('id')
        
        for rejection in saved_rejections:
            rejected_qty = rejection.rejected_tray_quantity or 0
            rejected_tray_id = rejection.rejected_tray_id
            
            if rejected_qty <= 0:
                continue
                
            if rejected_tray_id and is_new_tray_by_id(rejected_tray_id):
                # NEW tray creates actual free space
                available_quantities = brass_reduce_quantities_optimally(available_quantities, rejected_qty, is_new_tray=True)
                print(f"[Brass Simple Validation] Applied saved NEW tray rejection: {rejected_qty}")
            else:
                # EXISTING tray just consumes available quantities
                available_quantities = brass_reduce_quantities_optimally(available_quantities, rejected_qty, is_new_tray=False)
                print(f"[Brass Simple Validation] Applied saved EXISTING tray rejection: {rejected_qty}")

        # Apply current session allocations EXCEPT the current rejection being validated
        for allocation in current_session_allocations:
            try:
                reason_text = allocation.get('reason_text', '')
                qty = int(allocation.get('qty', 0))
                tray_ids = allocation.get('tray_ids', [])
                
                # Skip the current rejection being validated (avoid double counting)
                if qty == rejection_qty and not tray_ids:
                    print(f"[Brass Simple Validation] Skipping current rejection in session: qty={qty}")
                    continue
                
                if qty <= 0:
                    continue
                
                # Check if NEW tray was used by looking at tray_ids
                is_new_tray_used = False
                if tray_ids:
                    for session_tray_id in tray_ids:
                        if session_tray_id and is_new_tray_by_id(session_tray_id):
                            is_new_tray_used = True
                            break
                
                if is_new_tray_used:
                    available_quantities = brass_reduce_quantities_optimally(available_quantities, qty, is_new_tray=True)
                    print(f"[Brass Simple Validation] Applied session NEW tray: qty={qty}")
                else:
                    available_quantities = brass_reduce_quantities_optimally(available_quantities, qty, is_new_tray=False)
                    print(f"[Brass Simple Validation] Applied session EXISTING tray: qty={qty}")
            except Exception as e:
                print(f"[Brass Simple Validation] Error processing allocation: {e}")
                continue

        # Calculate current state after saved rejections + other session allocations
        total_current_qty = sum(available_quantities)
        
        print(f"[Brass Simple Validation] After applying saved + other session (excluding current):")
        print(f"[Brass Simple Validation] Available quantities: {available_quantities}")
        print(f"[Brass Simple Validation] Total current qty: {total_current_qty}")
        print(f"[Brass Simple Validation] Current rejection qty: {rejection_qty}")

        # ✅ ENHANCED: Check if current rejection is possible with proper rearrangement logic
        if rejection_qty <= total_current_qty:
            # The remaining pieces after THIS rejection
            remaining_after_this_rejection = total_current_qty - rejection_qty
            
            print(f"[Brass Simple Validation] Remaining after THIS rejection: {remaining_after_this_rejection}")
            
            # Check if remaining pieces can be rearranged optimally within existing tray capacities
            can_rearrange_result = can_rearrange_remaining_pieces(
                available_quantities, 
                original_capacities, 
                rejection_qty, 
                remaining_after_this_rejection
            )
            
            if can_rearrange_result['success']:
                return JsonResponse({
                    'exists': True,
                    'valid_for_rejection': True,
                    'status_message': f'Available ({can_rearrange_result["message"]})',
                    'validation_type': 'existing_sufficient_space',
                    'available_quantities': available_quantities,
                    'total_current': total_current_qty,
                    'remaining_after_rejection': remaining_after_this_rejection,
                    'rearrangement_plan': can_rearrange_result.get('plan', [])
                })
            else:
                return JsonResponse({
                    'exists': False,
                    'valid_for_rejection': False,
                    'error': 'Insufficient rearrangement space',
                    'status_message': f'Need NEW tray ({can_rearrange_result["message"]})',
                    'validation_type': 'existing_no_space',
                    'available_quantities': available_quantities,
                    'remaining_after_rejection': remaining_after_this_rejection
                })
        else:
            # Rejection quantity exceeds total available
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Insufficient total quantity',
                'status_message': f'Need NEW tray (have {total_current_qty}, need {rejection_qty})',
                'validation_type': 'existing_insufficient',
                'available_quantities': available_quantities,
                'total_current': total_current_qty
            })

    except Exception as e:
        print(f"[Brass Simple Validation] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'exists': False,
            'valid_for_rejection': False,
            'error': 'System error',
            'status_message': 'System Error'
        })


def can_rearrange_remaining_pieces(available_quantities, original_capacities, rejection_qty, remaining_qty):
    """
    ENHANCED: Progressive validation for multiple rejection rows
    - Each row validates against the current state after previous rejections
    - Takes into account the cumulative effect of session allocations
    """
    try:
        print(f"[Progressive Rearrangement Check] Input:")
        print(f"  Available quantities: {available_quantities}")
        print(f"  Original capacities: {original_capacities}")
        print(f"  Current rejection qty: {rejection_qty}")
        print(f"  Remaining qty after this rejection: {remaining_qty}")
        
        if remaining_qty == 0:
            return {'success': True, 'message': 'no pieces left', 'plan': []}
        
        # ✅ STEP 1: Check if we have enough quantity for this specific rejection
        total_current_qty = sum(available_quantities)
        if rejection_qty > total_current_qty:
            return {
                'success': False,
                'message': f'insufficient quantity: need {rejection_qty}, have {total_current_qty}',
                'plan': []
            }
        
        # ✅ STEP 2: Simulate this specific rejection
        temp_quantities = available_quantities.copy()
        temp_remaining_to_reject = rejection_qty
        
        # Consume rejection quantity from largest trays first
        sorted_indices = sorted(range(len(temp_quantities)), key=lambda i: temp_quantities[i], reverse=True)
        
        consumed_from_trays = []
        
        for i in sorted_indices:
            if temp_remaining_to_reject <= 0:
                break
            current_qty = temp_quantities[i]
            if current_qty > 0:
                consume_from_this_tray = min(temp_remaining_to_reject, current_qty)
                temp_quantities[i] -= consume_from_this_tray
                temp_remaining_to_reject -= consume_from_this_tray
                consumed_from_trays.append({
                    'tray_index': i,
                    'consumed_qty': consume_from_this_tray,
                    'remaining_in_tray': temp_quantities[i],
                    'tray_capacity': original_capacities[i] if i < len(original_capacities) else 0
                })
                print(f"  Consumed {consume_from_this_tray} from tray {i}, remaining: {temp_quantities[i]}")
        
        print(f"  After this rejection: {temp_quantities}")
        
        # ✅ STEP 3: Check if partial pieces can be accommodated
        for consumption in consumed_from_trays:
            tray_index = consumption['tray_index']
            remaining_in_tray = consumption['remaining_in_tray']
            tray_capacity = consumption['tray_capacity']
            
            # If we partially emptied a tray, check if remaining pieces can be moved
            if remaining_in_tray > 0 and remaining_in_tray < tray_capacity:
                print(f"  Tray {tray_index} has {remaining_in_tray} pieces left (partial)")
                
                # Check available space in other trays after this rejection
                available_space_in_other_trays = 0
                for j, qty in enumerate(temp_quantities):
                    if j != tray_index and j < len(original_capacities):
                        capacity = original_capacities[j]
                        available_space = capacity - qty
                        available_space_in_other_trays += max(0, available_space)
                        print(f"    Tray {j}: {qty}/{capacity}, free space: {max(0, available_space)}")
                
                print(f"  Total available space in other trays: {available_space_in_other_trays}")
                print(f"  Partial pieces to relocate: {remaining_in_tray}")
                
                # If partial pieces can't fit in other trays, reject this rejection
                if remaining_in_tray > available_space_in_other_trays:
                    return {
                        'success': False,
                        'message': f'partial {remaining_in_tray} pieces from tray {tray_index} cannot fit in other trays (only {available_space_in_other_trays} space)',
                        'plan': []
                    }
        
        # ✅ STEP 4: Calculate optimal final distribution
        total_remaining = sum(temp_quantities)
        final_distribution = [0] * len(temp_quantities)
        remaining_to_distribute = total_remaining
        
        # Fill trays optimally (largest capacity first)
        capacity_priority = []
        for i in range(len(temp_quantities)):
            if i < len(original_capacities):
                capacity = original_capacities[i]
                capacity_priority.append((capacity, i))
        
        capacity_priority.sort(reverse=True)
        
        for capacity, idx in capacity_priority:
            if remaining_to_distribute <= 0:
                break
            
            fill_amount = min(remaining_to_distribute, capacity)
            final_distribution[idx] = fill_amount
            remaining_to_distribute -= fill_amount
            print(f"  Final distribution: Put {fill_amount} in tray {idx} (capacity {capacity})")
        
        print(f"  Final distribution: {final_distribution}")
        print(f"  Remaining undistributed: {remaining_to_distribute}")
        
        if remaining_to_distribute == 0:
            return {
                'success': True,
                'message': f'can rearrange to {final_distribution}',
                'plan': final_distribution
            }
        else:
            return {
                'success': False,
                'message': f'cannot fit {remaining_to_distribute} pieces after rearrangement',
                'plan': []
            }
            
    except Exception as e:
        print(f"[Progressive Rearrangement Check] Error: {e}")
        return {'success': False, 'message': 'rearrangement check failed', 'plan': []}

def get_brass_available_quantities_with_session_allocations(lot_id, current_session_allocations):
    """
    Calculate available tray quantities and ACTUAL free space for Brass QC
    """
    try:
        # Get original distribution and track free space separately
        original_distribution = get_brass_original_tray_distribution(lot_id)
        original_capacities = get_brass_tray_capacities_for_lot(lot_id)
        
        available_quantities = original_distribution.copy()
        new_tray_usage_count = 0  # Track NEW tray usage for free space calculation
        
        print(f"[Brass Session Validation] Starting with: {available_quantities}")
        
        # First, apply saved rejections
        saved_rejections = Brass_QC_Rejected_TrayScan.objects.filter(lot_id=lot_id).order_by('id')
        
        for rejection in saved_rejections:
            rejected_qty = rejection.rejected_tray_quantity or 0
            tray_id = rejection.rejected_tray_id
            
            if rejected_qty <= 0:
                continue
                
            if tray_id and is_new_tray_by_id(tray_id):
                # NEW tray creates actual free space
                new_tray_usage_count += 1
                available_quantities = brass_reduce_quantities_optimally(available_quantities, rejected_qty, is_new_tray=True)
                print(f"[Brass Session Validation] NEW tray saved rejection: freed up {rejected_qty} space")
            else:
                # EXISTING tray just consumes available quantities
                available_quantities = brass_reduce_quantities_optimally(available_quantities, rejected_qty, is_new_tray=False)
                print(f"[Brass Session Validation] EXISTING tray saved rejection: removed tray")
        
        # Then, apply current session allocations
        for allocation in current_session_allocations:
            try:
                reason_text = allocation.get('reason_text', '')
                qty = int(allocation.get('qty', 0))
                tray_ids = allocation.get('tray_ids', [])
                
                if qty <= 0:
                    continue
                
                # Check if NEW tray was used by looking at tray_ids
                is_new_tray_used = False
                if tray_ids:
                    for tray_id in tray_ids:
                        if tray_id and is_new_tray_by_id(tray_id):
                            is_new_tray_used = True
                            break
                
                if is_new_tray_used:
                    new_tray_usage_count += 1
                    available_quantities = brass_reduce_quantities_optimally(available_quantities, qty, is_new_tray=True)
                    print(f"[Brass Session Validation] NEW tray session: freed up {qty} space using tray {tray_ids}")
                else:
                    available_quantities = brass_reduce_quantities_optimally(available_quantities, qty, is_new_tray=False)
                    print(f"[Brass Session Validation] EXISTING tray session: removed tray")
            except Exception as e:
                print(f"[Brass Session Validation] Error processing allocation: {e}")
                continue
        
        # Calculate ACTUAL current free space
        actual_free_space = 0
        if len(available_quantities) <= len(original_capacities):
            for i, qty in enumerate(available_quantities):
                if i < len(original_capacities):
                    capacity = original_capacities[i]
                    actual_free_space += max(0, capacity - qty)
        
        # Calculate totals
        total_available = sum(available_quantities)
        total_capacity = sum(original_capacities[:len(available_quantities)])  # Only count current trays
        
        print(f"[Brass Session Validation] FINAL:")
        print(f"  Available quantities: {available_quantities}")
        print(f"  Total available: {total_available}")
        print(f"  Total capacity of current trays: {total_capacity}")
        print(f"  ACTUAL free space in current trays: {actual_free_space}")
        print(f"  NEW tray usage count: {new_tray_usage_count}")
        
        return available_quantities, actual_free_space
        
    except Exception as e:
        print(f"[Brass Session Validation] Error: {e}")
        return get_brass_original_tray_distribution(lot_id), 0

def brass_reduce_quantities_optimally(available_quantities, qty_to_reduce, is_new_tray=True):
    """
    Reduce quantities optimally for Brass QC with enhanced logic
    """
    quantities = available_quantities.copy()
    remaining = qty_to_reduce

    if is_new_tray:
        # NEW tray usage should FREE UP space from existing trays
        print(f"[brass_reduce_quantities_optimally] NEW tray: freeing up {qty_to_reduce} space")
        
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
        # ✅ ENHANCED: EXISTING tray should consume rejection quantity precisely
        total_available = sum(quantities)
        if total_available < qty_to_reduce:
            print(f"[brass_reduce_quantities_optimally] EXISTING tray: insufficient quantity ({total_available} < {qty_to_reduce})")
            return quantities  # Not enough quantity available
        
        print(f"[brass_reduce_quantities_optimally] EXISTING tray: consuming {qty_to_reduce} pieces")
        
        # ✅ STRATEGY: Consume from trays optimally to minimize fragmentation
        temp_quantities = quantities.copy()
        remaining_to_consume = qty_to_reduce
        
        # ✅ NEW: Try to consume from larger trays first to minimize fragmentation
        sorted_indices = sorted(range(len(temp_quantities)), key=lambda i: temp_quantities[i], reverse=True)
        
        for i in sorted_indices:
            if remaining_to_consume <= 0:
                break
            current_qty = temp_quantities[i]
            if current_qty > 0:
                consume_from_this_tray = min(remaining_to_consume, current_qty)
                temp_quantities[i] -= consume_from_this_tray
                remaining_to_consume -= consume_from_this_tray
                print(f"  Consumed {consume_from_this_tray} from tray {i}, new qty: {temp_quantities[i]}")
                
                if remaining_to_consume == 0:
                    break
        
        print(f"  Final quantities after consumption: {temp_quantities}")
        return temp_quantities


def get_brass_original_tray_distribution(lot_id):
    """
    Get original tray quantity distribution for the lot in Brass QC context
    ✅ FIXED: Exclude trays rejected in Input Screening (rejected_tray=True)
    """
    try:
        print(f"[Brass Original Distribution] Getting distribution for lot_id: {lot_id}")
        
        # ✅ CRITICAL FIX: Exclude trays rejected in Input Screening AND Brass QC
        from modelmasterapp.models import TrayId
        tray_objects = TrayId.objects.filter(lot_id=lot_id).exclude(
            rejected_tray=True  # ✅ Exclude Input Screening rejected trays
        ).exclude(
            brass_rejected_tray=True  # ✅ Exclude Brass QC rejected trays
        ).order_by('date')
        
        print(f"[Brass Original Distribution] Found {tray_objects.count()} valid tray objects (excluding rejected trays)")
        
        if tray_objects.exists():
            # Use actual tray quantities from database
            quantities = []
            for tray in tray_objects:
                tray_qty = getattr(tray, 'tray_quantity', None)
                rejected_tray = getattr(tray, 'rejected_tray', False)
                brass_rejected_tray = getattr(tray, 'brass_rejected_tray', False)
                
                print(f"[Brass Original Distribution] Tray {tray.tray_id}: quantity = {tray_qty}, rejected_tray = {rejected_tray}, brass_rejected_tray = {brass_rejected_tray}")
                
                # ✅ Double-check: Only include non-rejected trays
                if not rejected_tray and not brass_rejected_tray and tray_qty and tray_qty > 0:
                    quantities.append(tray_qty)
                else:
                    print(f"[Brass Original Distribution] SKIPPED tray {tray.tray_id} - rejected or zero quantity")
            
            if quantities:
                print(f"[Brass Original Distribution] From valid TrayId objects: {quantities}")
                return quantities
        
        # Fallback: Calculate from brass_physical_qty and standard capacity
        total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if not total_stock:
            print(f"[Brass Original Distribution] No TotalStockModel found for lot_id: {lot_id}")
            return []
        
        # Use brass_physical_qty if available, otherwise total_IP_accpeted_quantity
        total_qty = 0
        if hasattr(total_stock, 'brass_physical_qty') and total_stock.brass_physical_qty:
            total_qty = total_stock.brass_physical_qty
        elif hasattr(total_stock, 'total_IP_accpeted_quantity') and total_stock.total_IP_accpeted_quantity:
            total_qty = total_stock.total_IP_accpeted_quantity
        
        tray_capacity = get_brass_tray_capacity_for_lot(lot_id)
        
        print(f"[Brass Original Distribution] Fallback calculation - total_qty: {total_qty}, tray_capacity: {tray_capacity}")
        
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
        
        print(f"[Brass Original Distribution] Calculated: {distribution} (total: {total_qty}, capacity: {tray_capacity})")
        return distribution
        
    except Exception as e:
        print(f"[Brass Original Distribution] Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_brass_tray_capacities_for_lot(lot_id):
    """
    Get all tray capacities for a lot in Brass QC context
    ✅ FIXED: Exclude rejected trays from capacity calculation
    """
    try:
        print(f"[get_brass_tray_capacities_for_lot] Getting all capacities for lot_id: {lot_id}")
        
        from modelmasterapp.models import TrayId
        # ✅ CRITICAL FIX: Exclude rejected trays from capacity calculation
        tray_objects = TrayId.objects.filter(lot_id=lot_id).exclude(
            rejected_tray=True  # ✅ Exclude Input Screening rejected trays
        ).exclude(
            brass_rejected_tray=True  # ✅ Exclude Brass QC rejected trays
        ).order_by('date')
        
        capacities = []
        for tray in tray_objects:
            capacity = getattr(tray, 'tray_capacity', None)
            if capacity and capacity > 0:
                capacities.append(capacity)
            else:
                # Fallback to standard capacity if not set
                standard_capacity = get_brass_tray_capacity_for_lot(lot_id)
                capacities.append(standard_capacity)
                
        print(f"[get_brass_tray_capacities_for_lot] Capacities: {capacities}")
        return capacities
        
    except Exception as e:
        print(f"[get_brass_tray_capacities_for_lot] Error: {e}")
        return []

def get_brass_tray_capacity_for_lot(lot_id):
    """
    Get tray capacity for a lot from TrayId table (DYNAMIC) - Brass QC version
    """
    try:
        print(f"[get_brass_tray_capacity_for_lot] Getting capacity for lot_id: {lot_id}")
        
        # Get tray capacity from TrayId table for this specific lot
        from modelmasterapp.models import TrayId
        tray_objects = TrayId.objects.filter(lot_id=lot_id).exclude(brass_rejected_tray=True)
        
        if tray_objects.exists():
            # Get tray_capacity from first tray (all trays in same lot should have same capacity)
            first_tray = tray_objects.first()
            tray_capacity = getattr(first_tray, 'tray_capacity', None)
            
            if tray_capacity and tray_capacity > 0:
                print(f"[get_brass_tray_capacity_for_lot] Found tray_capacity from TrayId: {tray_capacity}")
                return tray_capacity
                
            # If tray_capacity is not set, check all trays for a valid capacity
            for tray in tray_objects:
                capacity = getattr(tray, 'tray_capacity', None)
                if capacity and capacity > 0:
                    print(f"[get_brass_tray_capacity_for_lot] Found valid tray_capacity: {capacity}")
                    return capacity
        
        # Fallback: Get from TotalStockModel > batch_id
        total_stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if total_stock and hasattr(total_stock, 'batch_id') and total_stock.batch_id:
            batch_capacity = getattr(total_stock.batch_id, 'tray_capacity', None)
            if batch_capacity and batch_capacity > 0:
                print(f"[get_brass_tray_capacity_for_lot] Using batch tray_capacity: {batch_capacity}")
                return batch_capacity
                
        print(f"[get_brass_tray_capacity_for_lot] Using default capacity: 12")
        return 12  # Final fallback
        
    except Exception as e:
        print(f"[get_brass_tray_capacity_for_lot] Error: {e}")
        import traceback
        traceback.print_exc()
        return 12


def is_new_tray_by_id(tray_id):
    """
    Check if a tray is marked as new_tray
    """
    try:
        from modelmasterapp.models import TrayId
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        return getattr(tray_obj, 'new_tray', False) if tray_obj else False
    except Exception as e:
        print(f"[is_new_tray_by_id] Error: {e}")
        return False
#=======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brass_get_delink_tray_data(request):
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
            return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
        
        print(f"🔍 [brass_get_delink_tray_data] Processing lot_id: {lot_id}")
        
        # Get the TotalStockModel for this lot
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if not stock:
            return Response({'success': False, 'error': 'Stock not found'}, status=400)
        
        # Get actual tray distribution for this lot
        original_distribution = get_brass_actual_tray_distribution_for_delink(lot_id, stock)
        print(f"🔍 [brass_get_delink_tray_data] Original distribution: {original_distribution}")
        
        if not original_distribution:
            return Response({
                'success': True,
                'delink_trays': [],
                'message': 'No tray distribution found'
            })
        
        # Calculate current distribution after all rejections
        current_distribution = brass_calculate_distribution_after_rejections(lot_id, original_distribution)
        print(f"🔍 [brass_get_delink_tray_data] Current distribution after rejections: {current_distribution}")
        
        # Find empty trays (quantity = 0) that need delink scanning
        delink_trays = []
        for i, qty in enumerate(current_distribution):
            if qty == 0:
                # Get original capacity for this tray position
                original_capacity = original_distribution[i] if i < len(original_distribution) else 0
                
                delink_trays.append({
                    'tray_number': i + 1,
                    'original_capacity': original_capacity,
                    'current_qty': 0,
                    'needs_delink': True
                })
                print(f"🔍 [brass_get_delink_tray_data] Empty tray found: position {i+1}, original capacity: {original_capacity}")
        
        print(f"🔍 [brass_get_delink_tray_data] Total empty trays needing delink: {len(delink_trays)}")
        
        return Response({
            'success': True,
            'delink_trays': delink_trays,
            'original_distribution': original_distribution,
            'current_distribution': current_distribution,
            'total_empty_trays': len(delink_trays)
        })
        
    except Exception as e:
        print(f"❌ [brass_get_delink_tray_data] Error: {e}")
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)


def get_brass_actual_tray_distribution_for_delink(lot_id, stock):
    """
    Get the actual tray distribution for a lot for delink calculations in Brass QC context.
    """
    try:
        print(f"🔍 [get_brass_actual_tray_distribution_for_delink] Getting distribution for lot_id: {lot_id}")
        
        # Method 1: Try to get from TrayId records if they have individual quantities
        print(f"🔍 Trying Method 1: TrayId records")
        # ✅ FIXED: Use 'date' instead of 'created_at'
        tray_records = TrayId.objects.filter(lot_id=lot_id).exclude(brass_rejected_tray=True).order_by('date')
        if tray_records.exists():
            quantities = []
            for tray in tray_records:
                if hasattr(tray, 'tray_quantity') and tray.tray_quantity:
                    quantities.append(tray.tray_quantity)
                    print(f"🔍 TrayId {tray.tray_id}: quantity = {tray.tray_quantity}")
            
            if quantities:
                print(f"✅ Method 1 SUCCESS: Found tray distribution from TrayId records: {quantities}")
                return quantities
        
        # Method 2: Calculate from brass_physical_qty and standard capacity
        print(f"🔍 Method 2: Using brass_physical_qty from TotalStockModel")
        
        # Use brass_physical_qty if available, otherwise total_IP_accpeted_quantity
        total_qty = 0
        if hasattr(stock, 'brass_physical_qty') and stock.brass_physical_qty:
            total_qty = stock.brass_physical_qty
            print(f"🔍 Using brass_physical_qty: {total_qty}")
        elif hasattr(stock, 'total_IP_accpeted_quantity') and stock.total_IP_accpeted_quantity:
            total_qty = stock.total_IP_accpeted_quantity
            print(f"🔍 Using total_IP_accpeted_quantity: {total_qty}")
        
        tray_capacity = get_brass_tray_capacity_for_lot(lot_id)
        print(f"🔍 tray_capacity = {tray_capacity}")
        
        if not total_qty or not tray_capacity:
            print(f"⚠️ Insufficient data: total_qty={total_qty}, tray_capacity={tray_capacity}")
            return []
        
        # Calculate distribution: remainder first, then full trays
        remainder = total_qty % tray_capacity
        full_trays = total_qty // tray_capacity
        
        distribution = []
        if remainder > 0:
            distribution.append(remainder)
        
        for _ in range(full_trays):
            distribution.append(tray_capacity)
        
        print(f"🔍 Method 2 SUCCESS: {distribution} (total: {total_qty}, capacity: {tray_capacity})")
        return distribution
        
    except Exception as e:
        print(f"❌ Error getting tray distribution: {e}")
        import traceback
        traceback.print_exc()
        return []


def brass_calculate_distribution_after_rejections(lot_id, original_distribution):
    """
    Calculate the current tray distribution after applying all rejections.
    
    CORRECTED LOGIC:
    - NEW tray usage frees up existing tray space (creates empty trays)
    - Existing tray usage removes that tray entirely from distribution  
    - SHORTAGE rejections consume quantities from existing trays (can create empty trays)
    """
    current_distribution = original_distribution.copy()
    
    # Get all rejections for this lot ordered by creation
    rejections = Brass_QC_Rejected_TrayScan.objects.filter(lot_id=lot_id).order_by('id')
    
    print(f"DEBUG: Processing {rejections.count()} rejections for lot {lot_id}")
    print(f"DEBUG: Starting distribution: {original_distribution}")
    
    for rejection in rejections:
        rejected_qty = int(rejection.rejected_tray_quantity) if rejection.rejected_tray_quantity else 0
        tray_id = rejection.rejected_tray_id
        reason = rejection.rejection_reason.rejection_reason if rejection.rejection_reason else 'Unknown'
        
        if rejected_qty <= 0:
            continue
        
        print(f"DEBUG: Processing rejection - Reason: {reason}, Qty: {rejected_qty}, Tray ID: '{tray_id}'")
        
        # ✅ FIXED: Handle SHORTAGE rejections properly
        if not tray_id or tray_id.strip() == '':
            # SHORTAGE rejection - consume from existing trays
            current_distribution = brass_consume_shortage_from_distribution(current_distribution, rejected_qty)
            continue
        
        # Check if NEW tray was used for non-SHORTAGE rejections
        is_new_tray = is_new_tray_by_id(tray_id)
        print(f"DEBUG: is_new_tray_by_id('{tray_id}') = {is_new_tray}")
        
        if is_new_tray:
            # NEW tray creates empty trays by freeing up space
            current_distribution = brass_free_up_space_optimally(current_distribution, rejected_qty)
            print(f"DEBUG: NEW tray freed up {rejected_qty} space")
        else:
            # EXISTING tray removes entire tray from distribution
            current_distribution = brass_remove_rejected_tray_from_distribution(current_distribution, rejected_qty)
            print(f"DEBUG: EXISTING tray removed from distribution")
        
        print(f"DEBUG: Distribution after this rejection: {current_distribution}")
    
    print(f"DEBUG: Final distribution: {current_distribution}")
    return current_distribution


def brass_consume_shortage_from_distribution(distribution, shortage_qty):
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
            result[i] -= remaining_shortage
            print(f"   Consumed {remaining_shortage} from tray {i}, remaining: {result[i]}")
            remaining_shortage = 0
        elif current_qty > 0:
            remaining_shortage -= current_qty
            print(f"   Consumed all {current_qty} from tray {i}")
            result[i] = 0
    
    if remaining_shortage > 0:
        print(f"   ⚠️ WARNING: Could not consume all shortage qty, remaining: {remaining_shortage}")
    
    print(f"   SHORTAGE result: {result}")
    return result


def brass_remove_rejected_tray_from_distribution(distribution, rejected_qty):
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
            del result[i]
            print(f"   Removed tray {i} with exact matching qty {rejected_qty}")
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
            del result[i]
            print(f"   Removed empty tray at position {i}")
            return result
    
    # If no empty tray, remove the smallest quantity tray
    if result:
        min_qty = min(result)
        for i in range(len(result)):
            if result[i] == min_qty:
                del result[i]
                print(f"   Removed tray {i} with smallest qty {min_qty}")
                return result
    
    return result


def brass_free_up_space_optimally(distribution, qty_to_free):
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
            print(f"  Freed {remaining} from tray {i}, new qty: {result[i]}")
            remaining = 0
        elif current_qty > 0:
            remaining -= current_qty
            print(f"  Freed entire tray {i}: {current_qty}")
            result[i] = 0
    return result

@require_GET
def brass_delink_check_tray_id(request):
    """
    Validate tray ID for delink process in Brass QC
    Check if tray exists in same lot and is not already rejected
    ✅ UPDATED: Do NOT allow new trays (without lot_id)
    """
    tray_id = request.GET.get('tray_id', '')
    current_lot_id = request.GET.get('lot_id', '')
    
    try:
        if not tray_id:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Tray ID is required',
                'status_message': 'Required'
            })
        
        # Get the tray object if it exists
        tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
        
        if not tray_obj:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Tray ID not found',
                'status_message': 'Not Found'
            })

        # ✅ UPDATED: Check 1 - Do NOT allow new trays (without lot_id)
        if not tray_obj.lot_id or tray_obj.lot_id == '' or tray_obj.lot_id is None:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'New trays not allowed for delink',
                'status_message': 'New Tray Not Allowed'
            })

        # ✅ CHECK 2: Must belong to same lot
        if str(tray_obj.lot_id).strip() != str(current_lot_id).strip():
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Different lot',
                'status_message': 'Different Lot'
            })

        # ✅ CHECK 3: Must NOT be already rejected
        if hasattr(tray_obj, 'brass_rejected_tray') and tray_obj.brass_rejected_tray:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Already rejected',
                'status_message': 'Already Rejected'
            })

        # ✅ CHECK 4: Must NOT be in Brass_QC_Rejected_TrayScan for this lot
        already_rejected_in_brass = Brass_QC_Rejected_TrayScan.objects.filter(
            lot_id=current_lot_id,
            rejected_tray_id=tray_id
        ).exists()
        
        if already_rejected_in_brass:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Already rejected in Brass QC',
                'status_message': 'Already Rejected'
            })

        # ✅ CHECK 5: Must NOT be already delinked
        if hasattr(tray_obj, 'delink_tray') and tray_obj.delink_tray:
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Already delinked',
                'status_message': 'Already Delinked'
            })

        # ✅ CHECK 6: Must be verified (additional validation for delink)
        if not getattr(tray_obj, 'IP_tray_verified', False):
            return JsonResponse({
                'exists': False,
                'valid_for_rejection': False,
                'error': 'Tray not verified',
                'status_message': 'Not Verified'
            })

        # ✅ SUCCESS: Tray is valid for delink
        return JsonResponse({
            'exists': True,
            'valid_for_rejection': True,
            'status_message': 'Available for Delink',
            'validation_type': 'existing_valid',
            'tray_quantity': getattr(tray_obj, 'tray_quantity', 0) or 0
        })
        
    except Exception as e:
        print(f"❌ [brass_delink_check_tray_id] Error: {e}")
        return JsonResponse({
            'exists': False,
            'valid_for_rejection': False,
            'error': 'System error',
            'status_message': 'System Error'
        })
#=========================================================

# This endpoint retrieves top tray scan data for a given lot_id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brass_get_accepted_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        if not stock:
            return Response({'success': False, 'error': 'Stock not found'}, status=404)
        
        model_no = stock.model_stock_no.model_no if stock.model_stock_no else ""
        tray_capacity = stock.batch_id.tray_capacity if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity') else 10

        # ✅ UPDATED: Get rejection qty for calculation
        reason_store = Brass_QC_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
        total_rejection_qty = reason_store.total_rejection_quantity if reason_store else 0

        # ✅ UPDATED: Only use brass_physical_qty
        if stock.brass_physical_qty and stock.brass_physical_qty > 0:
            brass_physical_qty = stock.brass_physical_qty
        else:
            return Response({'success': False, 'error': 'No brass physical quantity available'}, status=400)

        # ✅ CORRECTED: Calculate available_qty after subtracting rejections
        available_qty = brass_physical_qty - total_rejection_qty
        
        if available_qty <= 0:
            return Response({'success': False, 'error': 'No available quantity for acceptance after rejections'}, status=400)

        print(f"📐 [brass_get_accepted_tray_scan_data] brass_physical_qty = {brass_physical_qty}")
        print(f"📐 [brass_get_accepted_tray_scan_data] total_rejection_qty = {total_rejection_qty}")
        print(f"📐 [brass_get_accepted_tray_scan_data] available_qty = {available_qty}")

        # ✅ CORRECTED: Calculate top tray quantity using available_qty after rejections
        full_trays = available_qty // tray_capacity
        top_tray_qty = available_qty % tray_capacity

        # ✅ CORRECTED: If remainder is 0 and we have quantity, the last tray should be full capacity
        if top_tray_qty == 0 and available_qty > 0:
            top_tray_qty = tray_capacity

        print(f"📊 [brass_get_accepted_tray_scan_data] Tray calculation: {available_qty} qty = {full_trays} full trays + {top_tray_qty} top tray")
        print(f"📊 [brass_get_accepted_tray_scan_data] Example: If capacity=12, qty=33 → 33÷12=2 full trays (12,12) + 9 top tray")

        # Check for existing draft data
        has_draft = Brass_Qc_Accepted_TrayID_Store.objects.filter(lot_id=lot_id, is_draft=True).exists()
        draft_tray_id = ""
        
        if has_draft:
            draft_record = Brass_Qc_Accepted_TrayID_Store.objects.filter(lot_id=lot_id, is_draft=True).first()
            if (draft_record):
                draft_tray_id = draft_record.tray_id
        
        return Response({
            'success': True,
            'model_no': model_no,
            'tray_capacity': tray_capacity,
            'brass_physical_qty': brass_physical_qty,
            'total_rejection_qty': total_rejection_qty,
            'available_qty': available_qty,  # ✅ NEW: Available qty after rejections
            'top_tray_qty': top_tray_qty,  # ✅ DYNAMIC: Now calculated dynamically
            'has_draft': has_draft,
            'draft_tray_id': draft_tray_id,
        })
    except Exception as e:
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def brass_save_single_top_tray_scan(request):
    try:
        data = request.data
        lot_id = data.get('lot_id')
        tray_id = data.get('tray_id')
        tray_qty = data.get('tray_qty')
        draft_save = data.get('draft_save', False)
        delink_trays = data.get('delink_trays', [])  # ✅ This should now receive data
        user = request.user

        print(f"🔍 [brass_save_single_top_tray_scan] Received data:")
        print(f"  lot_id: {lot_id}")
        print(f"  tray_id: {tray_id}")
        print(f"  tray_qty: {tray_qty}")
        print(f"  draft_save: {draft_save}")
        print(f"  delink_trays: {delink_trays}")

        if not lot_id or not tray_id or not tray_qty:
            return Response({
                'success': False, 
                'error': 'Missing lot_id, tray_id, or tray_qty'
            }, status=400)

        # ✅ Validation - Prevent same tray ID for delink and top tray
        delink_tray_ids = [delink['tray_id'] for delink in delink_trays if delink.get('tray_id')]
        if tray_id in delink_tray_ids:
            return Response({
                'success': False,
                'error': 'Top tray and delink tray cannot be the same'
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
        if top_tray_obj.brass_rejected_tray:
            return Response({
                'success': False,
                'error': f'Top tray ID "{tray_id}" is already rejected.'
            }, status=400)

        # ✅ NEW: Validate all delink trays (only if not draft and delink_trays exist)
        if not draft_save and delink_trays:
            for delink in delink_trays:
                delink_tray_id = delink.get('tray_id', '').strip()
                if delink_tray_id:
                    delink_tray_obj = TrayId.objects.filter(tray_id=delink_tray_id).first()
                    if not delink_tray_obj:
                        return Response({
                            'success': False,
                            'error': f'Delink tray ID "{delink_tray_id}" does not exist.'
                        }, status=400)
                    
                    if str(delink_tray_obj.lot_id) != str(lot_id):
                        return Response({
                            'success': False,
                            'error': f'Delink tray ID "{delink_tray_id}" does not belong to this lot.'
                        }, status=400)
                    
                    if delink_tray_obj.brass_rejected_tray:
                        return Response({
                            'success': False,
                            'error': f'Delink tray ID "{delink_tray_id}" is already rejected.'
                        }, status=400)



        # ✅ NEW: Handle TrayId table updates only for final submit (not draft)
        delink_count = 0
        if not draft_save:
            # Update top tray in TrayId table
            top_tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
            if top_tray_obj:
                top_tray_obj.ip_top_tray = True
                top_tray_obj.ip_top_tray_qty = tray_qty
                top_tray_obj.save(update_fields=['ip_top_tray', 'ip_top_tray_qty'])
                print(f"✅ [brass_save_single_top_tray_scan] Updated top tray: {tray_id}")
            
            # Update delink trays in TrayId table
            for delink in delink_trays:
                delink_tray_id = delink.get('tray_id', '').strip()
                if delink_tray_id:
                    delink_tray_obj = TrayId.objects.filter(tray_id=delink_tray_id).first()
                    if delink_tray_obj:
                        # Mark as delinked
                        delink_tray_obj.delink_tray = True
                        delink_tray_obj.lot_id = None  # Remove lot assignment
                        delink_tray_obj.batch_id = None  # Remove batch assignment
                        delink_tray_obj.scanned = False
                        delink_tray_obj.IP_tray_verified = False
                        delink_tray_obj.ip_top_tray = False
                        delink_tray_obj.top_tray = False
                        delink_tray_obj.save(update_fields=[
                            'delink_tray', 'lot_id', 'batch_id', 'scanned', 
                            'IP_tray_verified', 'ip_top_tray', 'top_tray'
                        ])
                        delink_count += 1
                        print(f"✅ [brass_save_single_top_tray_scan] Delinked tray: {delink_tray_id}")

        # Update TotalStockModel flags only if it's a final save (not draft)
        if not draft_save:
            stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if stock:
                stock.brass_accepted_tray_scan_status = True
                stock.next_process_module = "Jig Loading"
                stock.last_process_module = "Brass QC"
                stock.brass_onhold_picking = False
                stock.save(update_fields=[
                    'brass_accepted_tray_scan_status', 
                    'next_process_module', 
                    'last_process_module', 
                    'brass_onhold_picking'
                ])

        # ✅ Enhanced response message
        if draft_save:
            message = 'Top tray scan saved as draft successfully.'
        else:
            message = f'Top tray scan completed successfully.'
            if delink_count > 0:
                message += f' {delink_count} tray(s) delinked.'

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
def brass_view_tray_list(request):
    """
    Returns tray list for a given lot_id based on different conditions:
    1. If brass_qc_accptance is True: get from TrayId table
    2. If batch_rejection is True: split total_rejection_quantity by tray_capacity and get tray_ids from TrayId
    3. If batch_rejection is False: return all trays from IQF_Accepted_TrayID_Store
    """
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)

    try:
        # Check if this lot has brass_qc_accptance = True
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        brass_qc_accptance = False
        tray_capacity = 0
        
        if stock:
            brass_qc_accptance = stock.brass_qc_accptance or False
            if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity'):
                tray_capacity = stock.batch_id.tray_capacity or 0

        tray_list = []

        # Condition 1: If brass_qc_accptance is True, get from TrayId table
        if brass_qc_accptance:
            trays = TrayId.objects.filter(lot_id=lot_id).order_by('id')
            for idx, tray_obj in enumerate(trays):
                tray_list.append({
                    'sno': idx + 1,
                    'tray_id': tray_obj.tray_id,
                    'tray_qty': tray_obj.tray_quantity,  # Assuming this field exists in TrayId model
                })
            
            return Response({
                'success': True,
                'brass_qc_accptance': True,
                'batch_rejection': False,
                'total_rejection_qty': 0,
                'tray_capacity': tray_capacity,
                'trays': tray_list,
            })

        # Condition 2 & 3: Check rejection reason store (existing logic)
        reason_store = Brass_QC_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
        batch_rejection = False
        total_rejection_qty = 0
        
        if reason_store:
            batch_rejection = reason_store.batch_rejection
            total_rejection_qty = reason_store.total_rejection_quantity

        if batch_rejection and total_rejection_qty > 0 and tray_capacity > 0:
            # Batch rejection: split total_rejection_qty by tray_capacity, get tray_ids from TrayId
            tray_ids = list(TrayId.objects.filter(lot_id=lot_id).values_list('tray_id', flat=True))
            num_trays = ceil(total_rejection_qty / tray_capacity)
            qty_left = total_rejection_qty
            
            for i in range(num_trays):
                qty = tray_capacity if qty_left > tray_capacity else qty_left
                tray_id = tray_ids[i] if i < len(tray_ids) else ""
                tray_list.append({
                    'sno': i + 1,
                    'tray_id': tray_id,
                    'tray_qty': qty,
                })
                qty_left -= qty
        else:
            # Not batch rejection: get from Brass_Qc_Accepted_TrayID_Store
            trays = Brass_Qc_Accepted_TrayID_Store.objects.filter(lot_id=lot_id).order_by('id')
            for idx, obj in enumerate(trays):
                tray_list.append({
                    'sno': idx + 1,
                    'tray_id': obj.tray_id,
                    'tray_qty': obj.tray_qty,
                })

        return Response({
            'success': True,
            'brass_qc_accptance': brass_qc_accptance,
            'batch_rejection': batch_rejection,
            'total_rejection_qty': total_rejection_qty,
            'tray_capacity': tray_capacity,
            'trays': tray_list,
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BrassTrayValidateAPIView(APIView):
    def post(self, request):
        try:
            # Parse request data
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            
            # Get parameters
            lot_id_input = str(data.get('batch_id', '') or data.get('lot_id', '')).strip()
            tray_id = str(data.get('tray_id', '')).strip()
            
            print("="*50)
            print(f"[DEBUG] Raw request data: {data}")
            print(f"[DEBUG] Extracted lot_id: '{lot_id_input}' (length: {len(lot_id_input)})")
            print(f"[DEBUG] Extracted tray_id: '{tray_id}' (length: {len(tray_id)})")
            
            if not lot_id_input or not tray_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Both lot_id and tray_id are required'
                }, status=400)

            # Step 1: Check if lot_id exists in ModelMasterCreation (optional validation)
            print(f"[DEBUG] Checking if lot_id exists in ModelMasterCreation: '{lot_id_input}'")
            try:
                model_master_creation = ModelMasterCreation.objects.get(lot_id=lot_id_input)
                print(f"[DEBUG] Found ModelMasterCreation: batch_id='{model_master_creation.batch_id}', lot_id='{model_master_creation.lot_id}'")
            except ModelMasterCreation.DoesNotExist:
                print(f"[DEBUG] No ModelMasterCreation found with lot_id: '{lot_id_input}'")
                # Continue anyway since we're checking TrayId which uses lot_id directly

            # Step 2: Check if the tray exists in TrayId for this lot_id
            print(f"[DEBUG] Checking if tray '{tray_id}' exists in TrayId for lot_id: '{lot_id_input}'")
            
            tray_exists = TrayId.objects.filter(
                lot_id=lot_id_input,  # Use lot_id directly
                tray_id=tray_id
            ).exists()
            
            print(f"[DEBUG] Tray exists in TrayId: {tray_exists}")
            
            # Additional debugging: show all trays for this lot_id in TrayId
            all_trays = TrayId.objects.filter(
                lot_id=lot_id_input
            ).values_list('tray_id', flat=True)
            print(f"[DEBUG] All trays in TrayId for lot_id '{lot_id_input}': {list(all_trays)}")
            
            # Also check if tray exists anywhere in TrayId (for debugging)
            tray_anywhere = TrayId.objects.filter(tray_id=tray_id)
            if tray_anywhere.exists():
                tray_lot_ids = list(tray_anywhere.values_list('lot_id', flat=True))
                print(f"[DEBUG] Tray '{tray_id}' found in TrayId for lot_ids: {tray_lot_ids}")
            
            print(f"[DEBUG] Final result - exists: {tray_exists}")
            print("="*50)
            
            return JsonResponse({
                'success': True, 
                'exists': tray_exists,
                'debug_info': {
                    'lot_id_received': lot_id_input,
                    'tray_id_received': tray_id,
                    'all_trays_in_brass_qc_store': list(all_trays),
                    'tray_exists_in_brass_qc_store': tray_exists
                }
            })
            
        except Exception as e:
            print(f"[DEBUG] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brass_check_accepted_tray_draft(request):
    """Check if draft data exists for accepted tray scan"""
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        has_draft = Brass_Qc_Accepted_TrayID_Store.objects.filter(
            lot_id=lot_id, 
            is_draft=True
        ).exists()
        
        return Response({
            'success': True,
            'has_draft': has_draft
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def brass_save_accepted_tray_scan(request):
    try:
        data = request.data
        lot_id = data.get('lot_id')
        rows = data.get('rows', [])
        draft_save = data.get('draft_save', False)  # Get draft_save parameter
        user = request.user

        if not lot_id or not rows:
            return Response({'success': False, 'error': 'Missing lot_id or rows'}, status=400)

        # Validate all tray_ids exist in TrayId table
        for idx, row in enumerate(rows):
            tray_id = row.get('tray_id')
            if not tray_id or not TrayId.objects.filter(tray_id=tray_id).exists():
                return Response({
                    'success': False,
                    'error': f'Tray ID "{tray_id}" is not existing (Row {idx+1}).'
                }, status=400)

        # Remove existing tray IDs for this lot (to avoid duplicates)
        Brass_Qc_Accepted_TrayID_Store.objects.filter(lot_id=lot_id).delete()

        total_qty = 0
        for row in rows:
            tray_id = row.get('tray_id')
            tray_qty = row.get('tray_qty')
            if not tray_id or tray_qty is None:
                continue
            total_qty += int(tray_qty)
            
            # Create with appropriate boolean flags based on draft_save parameter
            Brass_Qc_Accepted_TrayID_Store.objects.create(
                lot_id=lot_id,
                tray_id=tray_id,
                tray_qty=tray_qty,
                user=user,
                is_draft=draft_save,      # True if Draft button clicked
                is_save=not draft_save    # True if Submit button clicked
            )

        # Save/Update Brass_Qc_Accepted_TrayScan for this lot
        accepted_scan, created = Brass_Qc_Accepted_TrayScan.objects.get_or_create(
            lot_id=lot_id,
            user=user,
            defaults={'accepted_tray_quantity': total_qty}
        )
        if not created:
            accepted_scan.accepted_tray_quantity = total_qty
            accepted_scan.save(update_fields=['accepted_tray_quantity'])

        # Update TotalStockModel flags only if it's a final save (not draft)
        if not draft_save:
            stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if stock:
                stock.accepted_tray_scan_status = True
                stock.next_process_module = "Jig Loading"
                stock.last_process_module = "Brass QC"
                stock.brass_onhold_picking = False  # Reset onhold picking status
                stock.save(update_fields=['accepted_tray_scan_status', 'next_process_module', 'last_process_module', 'brass_onhold_picking'])

        return Response({'success': True, 'message': 'Accepted tray scan saved.'})

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


# ...existing code...

@require_GET
def brass_check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    lot_id = request.GET.get('lot_id', '')  # This is your stock_lot_id

    # 1. Must exist in TrayId table and lot_id must match
    tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
    exists = bool(tray_obj)
    same_lot = exists and str(tray_obj.lot_id) == str(lot_id)

    # 2. Must NOT be rejected in any module (Input Screening OR Brass QC)
    already_rejected = False
    if exists and same_lot and lot_id:
        # ✅ CHECK 1: Check if rejected in Input Screening (rejected_tray=True)
        input_screening_rejected = getattr(tray_obj, 'rejected_tray', False)
        
        # ✅ CHECK 2: Check if rejected in Brass QC (brass_rejected_tray=True)
        brass_qc_rejected = getattr(tray_obj, 'brass_rejected_tray', False)
        
        # ✅ CHECK 3: Check if rejected in Brass_QC_Rejected_TrayScan for this lot
        brass_qc_scan_rejected = Brass_QC_Rejected_TrayScan.objects.filter(
            lot_id=lot_id,
            rejected_tray_id=tray_id
        ).exists()
        
        # Mark as already rejected if any of the above is true
        already_rejected = input_screening_rejected or brass_qc_rejected or brass_qc_scan_rejected

    # Only valid if exists, same lot, and not already rejected
    is_valid = exists and same_lot and not already_rejected

    return JsonResponse({
        'exists': is_valid,
        'already_rejected': already_rejected,
        'not_in_same_lot': exists and not same_lot,
        'rejected_in_input_screening': exists and getattr(tray_obj, 'rejected_tray', False),
        'rejected_in_brass_qc': exists and getattr(tray_obj, 'brass_rejected_tray', False)
    })

# ...existing code...

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brass_get_rejected_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        rows = []
        for obj in Brass_QC_Rejected_TrayScan.objects.filter(lot_id=lot_id):
            rows.append({
                'tray_id': obj.rejected_tray_id,
                'qty': obj.rejected_tray_quantity,
                'reason': obj.rejection_reason.rejection_reason,
                'reason_id': obj.rejection_reason.rejection_reason_id,
            })
        return Response({'success': True, 'rows': rows})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


class BrassCompletedView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Brass_Qc/Brass_Completed.html'

    def get(self, request):
        from django.utils import timezone
        from datetime import datetime, timedelta
        import pytz

        user = request.user
        
        # ✅ NEW: Add date filtering logic (copied from IS_Completed_Table)
        tz = pytz.timezone("Asia/Kolkata")
        now_local = timezone.now().astimezone(tz)
        today = now_local.date()
        yesterday = today - timedelta(days=1)

        # ✅ NEW: Get date filter parameters from request
        from_date_str = request.GET.get('from_date')
        to_date_str = request.GET.get('to_date')

        # ✅ NEW: Calculate date range
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

        # ✅ NEW: Convert dates to datetime objects for filtering
        from_datetime = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
        to_datetime = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))

        # ✅ NEW: Get batch_ids where bq_last_process_date_time is in range
        batch_ids_in_range = list(
            TotalStockModel.objects.filter(
                bq_last_process_date_time__range=(from_datetime, to_datetime)
            ).values_list('batch_id__batch_id', flat=True)
        )
                
        last_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('last_process_module')[:1]

        brass_qc_accepted_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_accepted_qty_verified')[:1]
        
        brass_qc_accepted_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_accepted_qty')[:1]
        
        brass_rejection_qty_subquery = Brass_QC_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('total_rejection_quantity')[:1]
        
        next_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('next_process_module')[:1]
        
        brass_missing_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_missing_qty')[:1]
        
        brass_physical_qty_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_physical_qty')[:1]
        
        brass_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_physical_qty_edited')[:1]
        
        accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_Ip_stock')[:1]
        
        rejected_ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('rejected_ip_stock')[:1]
         
        few_cases_accepted_Ip_stock_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('few_cases_accepted_Ip_stock')[:1]
        
        accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('accepted_tray_scan_status')[:1]
        
        Bq_pick_remarks_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('Bq_pick_remarks')[:1]
        
        brass_accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_accepted_tray_scan_status')[:1]
        
        brass_qc_rejection_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_rejection')[:1]
        
        brass_qc_few_cases_accptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_few_cases_accptance')[:1]
        
        brass_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_onhold_picking')[:1]
        
        iqf_acceptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_acceptance')[:1]
        
        send_brass_qc_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('send_brass_qc')[:1]

        bq_last_process_date_time = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('bq_last_process_date_time')[:1]

        total_IP_accpeted_quantity_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('total_IP_accpeted_quantity')[:1]

        brass_hold_lot_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_hold_lot')[:1]

        # ✅ UPDATED: Add date filtering to queryset
        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0,
            batch_id__in=batch_ids_in_range  # ✅ NEW: Use batch_ids_in_range for date filtering
        ).annotate(
            brass_qc_accptance=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('brass_qc_accptance')[:1]
            ),
            stock_lot_id=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('lot_id')[:1]
            ),
            last_process_module=Subquery(last_process_module_subquery),
            next_process_module=Subquery(next_process_module_subquery),
            brass_qc_accepted_qty_verified=Subquery(brass_qc_accepted_qty_verified_subquery),
            brass_qc_accepted_qty=Subquery(brass_qc_accepted_qty_subquery),
            brass_rejection_qty=Subquery(brass_rejection_qty_subquery),
            brass_missing_qty=Subquery(brass_missing_qty_subquery),
            brass_physical_qty=Subquery(brass_physical_qty_subquery),
            brass_physical_qty_edited=Subquery(brass_physical_qty_edited_subquery),
            accepted_Ip_stock=Subquery(accepted_Ip_stock_subquery),
            rejected_ip_stock=Subquery(rejected_ip_stock_subquery),
            few_cases_accepted_Ip_stock=Subquery(few_cases_accepted_Ip_stock_subquery),
            accepted_tray_scan_status=Subquery(accepted_tray_scan_status_subquery),
            Bq_pick_remarks=Subquery(Bq_pick_remarks_subquery),
            brass_accepted_tray_scan_status=Subquery(brass_accepted_tray_scan_status_subquery),
            brass_qc_rejection=Subquery(brass_qc_rejection_subquery),
            brass_qc_few_cases_accptance=Subquery(brass_qc_few_cases_accptance_subquery),
            brass_onhold_picking=Subquery(brass_onhold_picking_subquery),
            iqf_acceptance=Subquery(iqf_acceptance_subquery),
            send_brass_qc=Subquery(send_brass_qc_subquery),
            bq_last_process_date_time=Subquery(bq_last_process_date_time),
            total_IP_accpeted_quantity=Subquery(total_IP_accpeted_quantity_subquery),
            brass_hold_lot=Subquery(brass_hold_lot_subquery),
        ).filter(
            Q(brass_qc_accptance=True) |
            Q(brass_qc_rejection=True) |
            Q(brass_qc_few_cases_accptance=True, brass_onhold_picking=False)
        ).order_by('-bq_last_process_date_time')  # ✅ NEW: Order by bq_last_process_date_time

        print(f"📊 Found {queryset.count()} brass records in date range {from_date} to {to_date}")

        # Pagination (optional)
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
            'brass_qc_accepted_qty_verified',
            'brass_qc_accepted_qty',
            'brass_rejection_qty',
            'brass_missing_qty',
            'brass_physical_qty',
            'brass_physical_qty_edited',
            'accepted_Ip_stock',
            'rejected_ip_stock',
            'few_cases_accepted_Ip_stock',
            'accepted_tray_scan_status',
            'Bq_pick_remarks',
            'brass_qc_accptance',
            'brass_accepted_tray_scan_status',
            'brass_qc_rejection',
            'brass_qc_few_cases_accptance',
            'brass_onhold_picking',
            'iqf_acceptance',
            'send_brass_qc',
            'total_IP_accpeted_quantity',
            'plating_stk_no',
            'polishing_stk_no',
            'bq_last_process_date_time',
            'category',
            'brass_hold_lot',
        ))

        for data in master_data:
            total_IP_accpeted_quantity = data.get('total_IP_accpeted_quantity', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            
            # ✅ FIRST: Calculate display_accepted_qty
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
        
            # ✅ THEN: Calculate no_of_trays based on display_accepted_qty instead of total_IP_accpeted_quantity
            display_qty = data.get('display_accepted_qty', 0)
            if tray_capacity > 0 and display_qty > 0:
                data['no_of_trays'] = math.ceil(display_qty / tray_capacity)
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
            
        # ✅ NEW: Add date information to context
        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'from_date': from_date.strftime('%Y-%m-%d'),  # ✅ NEW: Pass dates to template
            'to_date': to_date.strftime('%Y-%m-%d'),      # ✅ NEW: Pass dates to template
            'date_filter_applied': bool(from_date_str and to_date_str),  # ✅ NEW: Flag to show if custom dates used
        }
        return Response(context, template_name=self.template_name)

  
@method_decorator(csrf_exempt, name='dispatch')
class BrassTrayIdList_Complete_APIView(APIView):
    def get(self, request):
        batch_id = request.GET.get('batch_id')
        stock_lot_id = request.GET.get('stock_lot_id')
        lot_id = request.GET.get('lot_id') or stock_lot_id
        brass_qc_accptance = request.GET.get('brass_qc_accptance', 'false').lower() == 'true'
        brass_qc_rejection = request.GET.get('brass_qc_rejection', 'false').lower() == 'true'
        brass_qc_few_cases_accptance = request.GET.get('brass_qc_few_cases_accptance', 'false').lower() == 'true'
        
        if not batch_id:
            return JsonResponse({'success': False, 'error': 'Missing batch_id'}, status=400)
        
        if not lot_id:
            return JsonResponse({'success': False, 'error': 'Missing lot_id or stock_lot_id'}, status=400)
        
        # ✅ UPDATED: Base queryset - exclude trays rejected in Input Screening
        base_queryset = TrayId.objects.filter(
            tray_quantity__gt=0,
            lot_id=lot_id
        ).exclude(
            rejected_tray=True  # ✅ EXCLUDE trays rejected in Input Screening
        )
        
        # Get rejected and accepted trays directly from TrayId table
        rejected_trays = base_queryset.filter(brass_rejected_tray=True)
        accepted_trays = base_queryset.filter(brass_rejected_tray=False)
        
        print(f"Total trays in lot (excluding Input Screening rejected): {base_queryset.count()}")
        print(f"Rejected trays (Brass QC): {rejected_trays.count()}")
        print(f"Accepted trays: {accepted_trays.count()}")
        
        # Apply filtering based on stock status
        if brass_qc_accptance and not brass_qc_few_cases_accptance:
            # Show only accepted trays
            queryset = accepted_trays
            print("Filtering for accepted trays only")
        elif brass_qc_rejection and not brass_qc_few_cases_accptance:
            # Show only rejected trays
            queryset = rejected_trays
            print("Filtering for rejected trays only")
        elif brass_qc_few_cases_accptance:
            # Show both accepted and rejected trays
            queryset = base_queryset
            print("Showing both accepted and rejected trays")
        else:
            # Default - show all trays
            queryset = base_queryset
            print("Using default filter - showing all trays")
        
        # Determine top tray based on status
        top_tray = None
        if brass_qc_accptance and not brass_qc_few_cases_accptance:
            # For accepted trays, prioritize ip_top_tray, then top_tray
            top_tray = accepted_trays.filter(ip_top_tray=True).first()
            if not top_tray:
                top_tray = accepted_trays.filter(top_tray=True).first()
        else:
            # For all other cases, prioritize ip_top_tray
            top_tray = queryset.filter(ip_top_tray=True).first()
            if not top_tray:
                top_tray = queryset.filter(top_tray=True).first()
        
        # Get other trays (excluding top tray)
        other_trays = queryset.exclude(pk=top_tray.pk if top_tray else None).order_by('id')
        
        data = []
        row_counter = 1

        # Helper function to create tray data
        def create_tray_data(tray_obj, is_top=False):
            nonlocal row_counter
            
            # Get rejection details if tray is rejected
            rejection_details = []
            if tray_obj.brass_rejected_tray:
                # Get rejection details from Brass_QC_Rejected_TrayScan if needed
                rejected_scans = Brass_QC_Rejected_TrayScan.objects.filter(
                    lot_id=lot_id,
                    rejected_tray_id=tray_obj.tray_id
                )
                for scan in rejected_scans:
                    rejection_details.append({
                        'rejected_quantity': scan.rejected_tray_quantity,
                        'rejection_reason': scan.rejection_reason.rejection_reason if scan.rejection_reason else 'Unknown',
                        'rejection_reason_id': scan.rejection_reason.rejection_reason_id if scan.rejection_reason else None,
                        'user': scan.user.username if scan.user else None
                    })
            
            return {
                's_no': row_counter,
                'tray_id': tray_obj.tray_id,
                'tray_quantity': tray_obj.tray_quantity,
                'position': row_counter - 1,
                'is_top_tray': is_top,
                'brass_rejected_tray': tray_obj.brass_rejected_tray,
                'delink_tray': getattr(tray_obj, 'delink_tray', False),
                'rejection_details': rejection_details,
                'ip_top_tray': getattr(tray_obj, 'ip_top_tray', False),
                'ip_top_tray_qty': getattr(tray_obj, 'ip_top_tray_qty', None),
                'top_tray': getattr(tray_obj, 'top_tray', False),
                'rejected_tray': getattr(tray_obj, 'rejected_tray', False)  # ✅ NEW: Include Input Screening rejection status
            }

        # Add top tray first if it exists
        if top_tray:
            tray_data = create_tray_data(top_tray, is_top=True)
            data.append(tray_data)
            row_counter += 1

        # Add other trays
        for tray in other_trays:
            tray_data = create_tray_data(tray, is_top=False)
            data.append(tray_data)
            row_counter += 1
        
        print(f"Total trays returned: {len(data)}")
        
        # ✅ UPDATED: Get shortage rejections count (trays without tray_id) - use correct model
        shortage_count = Brass_QC_Rejected_TrayScan.objects.filter(
            lot_id=lot_id
        ).filter(
            models.Q(rejected_tray_id__isnull=True) | models.Q(rejected_tray_id='')
        ).count()
        
        # ✅ UPDATED: Get count of Input Screening rejected trays for summary
        input_screening_rejected_count = TrayId.objects.filter(
            lot_id=lot_id,
            tray_quantity__gt=0,
            rejected_tray=True
        ).count()
        
        # Rejection summary
        rejection_summary = {
            'total_rejected_trays': rejected_trays.count(),
            'rejected_tray_ids': list(rejected_trays.values_list('tray_id', flat=True)),
            'shortage_rejections': shortage_count,
            'total_accepted_trays': accepted_trays.count(),
            'accepted_tray_ids': list(accepted_trays.values_list('tray_id', flat=True)),
            'input_screening_rejected_count': input_screening_rejected_count  # ✅ NEW: Count of excluded trays
        }
        
        return JsonResponse({
            'success': True, 
            'trays': data,
            'rejection_summary': rejection_summary
        })

        
@method_decorator(csrf_exempt, name='dispatch')
class BrassTrayValidate_Complete_APIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id_input = str(data.get('batch_id')).strip()
            tray_id = str(data.get('tray_id')).strip()
            
            # Get stock status parameters (optional, for enhanced validation)
            brass_qc_accptance = data.get('brass_qc_accptance', False)
            brass_qc_rejection = data.get('brass_qc_rejection', False)
            brass_qc_few_cases_accptance = data.get('brass_qc_few_cases_accptance', False)

            print(f"[BrassTrayValidate_Complete_APIView] User entered: batch_id={batch_id_input}, tray_id={tray_id}")
            print(f"Stock status: accepted={brass_qc_accptance}, rejected={brass_qc_rejection}, few_cases={brass_qc_few_cases_accptance}")

            # Base queryset for trays
            base_queryset = TrayId.objects.filter(
                batch_id__batch_id__icontains=batch_id_input,
                tray_quantity__gt=0
            )
            
            # Apply the same filtering logic as the list API
            if brass_qc_accptance and not brass_qc_few_cases_accptance:
                # Only validate against accepted trays
                trays = base_queryset.filter(brass_rejected_tray=False)
                print(f"Validating against accepted trays only")
            elif brass_qc_rejection and not brass_qc_few_cases_accptance:
                # Only validate against rejected trays
                trays = base_queryset.filter(brass_rejected_tray=True)
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
                        'brass_rejected_tray': tray.brass_rejected_tray,
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
class BrassGetShortageRejectionsView(APIView):
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


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BrassBatchRejectionDraftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            lot_id = data.get('lot_id')
            total_qty = data.get('total_qty', 0)
            lot_rejected_comment = data.get('lot_rejected_comment', '').strip()
            is_draft = data.get('is_draft', True)

            if not batch_id or not lot_id or not lot_rejected_comment:
                return Response({'success': False, 'error': 'Missing required fields'}, status=400)

            # Save as draft
            draft_data = {
                'total_qty': total_qty,
                'lot_rejected_comment': lot_rejected_comment,
                'batch_rejection': True,
                'is_draft': is_draft
            }

            # Update or create draft record
            draft_obj, created = Brass_QC_Draft_Store.objects.update_or_create(
                lot_id=lot_id,
                draft_type='batch_rejection',
                defaults={
                    'batch_id': batch_id,
                    'user': request.user,
                    'draft_data': draft_data
                }
            )

            return Response({
                'success': True, 
                'message': 'Batch rejection draft saved successfully',
                'draft_id': draft_obj.id
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BrassTrayRejectionDraftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            batch_id = data.get('batch_id')
            tray_rejections = data.get('tray_rejections', [])
            is_draft = data.get('is_draft', True)

            if not lot_id or not tray_rejections:
                return Response({'success': False, 'error': 'Missing lot_id or tray_rejections'}, status=400)

            # Save as draft
            draft_data = {
                'tray_rejections': tray_rejections,
                'batch_rejection': False,
                'is_draft': is_draft
            }

            # Update or create draft record
            draft_obj, created = Brass_QC_Draft_Store.objects.update_or_create(
                lot_id=lot_id,
                draft_type='tray_rejection',
                defaults={
                    'batch_id': batch_id,
                    'user': request.user,
                    'draft_data': draft_data
                }
            )

            return Response({
                'success': True, 
                'message': 'Tray rejection draft saved successfully',
                'draft_id': draft_obj.id,
                'total_rejections': len(tray_rejections)
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brass_get_draft_data(request):
    """Get draft data for a lot_id"""
    lot_id = request.GET.get('lot_id')
    draft_type = request.GET.get('draft_type', 'tray_rejection')
    
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        draft_obj = Brass_QC_Draft_Store.objects.filter(
            lot_id=lot_id,
            draft_type=draft_type
        ).first()
        
        if draft_obj:
            return Response({
                'success': True,
                'has_draft': True,
                'draft_data': draft_obj.draft_data,
                'created_at': draft_obj.created_at,
                'updated_at': draft_obj.updated_at
            })
        else:
            return Response({
                'success': True,
                'has_draft': False,
                'draft_data': None
            })
            
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

# Add this new API endpoint to your views.py

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BrassClearDraftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            draft_type = data.get('draft_type')  # 'batch_rejection' or 'tray_rejection'

            if not lot_id or not draft_type:
                return Response({'success': False, 'error': 'Missing lot_id or draft_type'}, status=400)

            # Delete the specific draft type
            deleted_count, _ = Brass_QC_Draft_Store.objects.filter(
                lot_id=lot_id,
                draft_type=draft_type
            ).delete()

            return Response({
                'success': True, 
                'message': f'Cleared {draft_type} draft',
                'deleted_count': deleted_count
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)


# Add this new API endpoint to your views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brass_get_all_drafts(request):
    """Get all draft data for a lot_id"""
    lot_id = request.GET.get('lot_id')
    
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        result = {
            'success': True,
            'batch_rejection_draft': None,
            'tray_rejection_draft': None
        }
        
        # Get batch rejection draft
        batch_draft = Brass_QC_Draft_Store.objects.filter(
            lot_id=lot_id,
            draft_type='batch_rejection'
        ).first()
        
        if batch_draft:
            result['batch_rejection_draft'] = {
                'draft_data': batch_draft.draft_data,
                'created_at': batch_draft.created_at,
                'updated_at': batch_draft.updated_at,
                'user': batch_draft.user.username if batch_draft.user else None
            }
        
        # Get tray rejection draft
        tray_draft = Brass_QC_Draft_Store.objects.filter(
            lot_id=lot_id,
            draft_type='tray_rejection'
        ).first()
        
        if tray_draft:
            result['tray_rejection_draft'] = {
                'draft_data': tray_draft.draft_data,
                'created_at': tray_draft.created_at,
                'updated_at': tray_draft.updated_at,
                'user': tray_draft.user.username if tray_draft.user else None
            }
        
        return Response(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)
    
# Add these API endpoints to your views.py

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BrassTopTrayScanDraftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            tray_id = data.get('tray_id')
            tray_qty = data.get('tray_qty')
            delink_trays = data.get('delink_trays', [])  # Optional delink data
            is_draft = data.get('is_draft', True)

            if not lot_id or not tray_id or not tray_qty:
                return Response({'success': False, 'error': 'Missing required fields'}, status=400)

            # Validate tray_id exists and is valid (optional - add if needed)
            tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
            if not tray_obj:
                return Response({'success': False, 'error': f'Tray ID "{tray_id}" does not exist'}, status=400)

            # Save as draft
            draft_data = {
                'tray_id': tray_id,
                'tray_qty': int(tray_qty),
                'delink_trays': delink_trays,
                'is_draft': is_draft,
                'draft_type': 'top_tray_scan'
            }

            # Update or create draft record
            draft_obj, created = Brass_QC_Draft_Store.objects.update_or_create(
                lot_id=lot_id,
                draft_type='top_tray_scan',
                defaults={
                    'batch_id': data.get('batch_id', ''),
                    'user': request.user,
                    'draft_data': draft_data
                }
            )

            return Response({
                'success': True, 
                'message': 'Top tray scan draft saved successfully',
                'draft_id': draft_obj.id,
                'tray_id': tray_id,
                'tray_qty': tray_qty
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def brass_get_top_tray_draft(request):
    """Get top tray scan draft for a lot_id"""
    lot_id = request.GET.get('lot_id')
    
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        draft_obj = Brass_QC_Draft_Store.objects.filter(
            lot_id=lot_id,
            draft_type='top_tray_scan'
        ).first()
        
        if draft_obj:
            return Response({
                'success': True,
                'has_draft': True,
                'draft_data': draft_obj.draft_data,
                'created_at': draft_obj.created_at,
                'updated_at': draft_obj.updated_at,
                'user': draft_obj.user.username if draft_obj.user else None
            })
        else:
            return Response({
                'success': True,
                'has_draft': False,
                'draft_data': None
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class BrassClearTopTrayDraftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')

            if not lot_id:
                return Response({'success': False, 'error': 'Missing lot_id'}, status=400)

            # Delete the top tray scan draft
            deleted_count, _ = Brass_QC_Draft_Store.objects.filter(
                lot_id=lot_id,
                draft_type='top_tray_scan'
            ).delete()

            return Response({
                'success': True, 
                'message': 'Top tray scan draft cleared',
                'deleted_count': deleted_count
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'error': str(e)}, status=500)

  