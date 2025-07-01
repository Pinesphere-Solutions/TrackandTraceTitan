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
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from math import ceil

# Create your views here.


class IQFPickTableView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'IQF/Iqf_PickTable.html'

    def get(self, request):
        user = request.user

  
        iqf_rejection_reasons = IQF_Rejection_Table.objects.select_related('group').all()
        
        # Dynamically assign colors to each group name
        group_names = IP_RejectionGroup.objects.values_list('group_name', flat=True)
        color_palette = [
            "#e53935",  # red
            "#fb8c00",  # orange
            "#43a047",  # green
            "#1e88e5",  # blue
            "#8e24aa",  # purple
            "#fbc02d",  # yellow
            "#00897b",  # teal
            "#6d4c41",  # brown
            "#757575",  # grey
            "#3949ab",  # indigo
        ]
        group_color_map = {}
        for idx, name in enumerate(group_names):
            group_color_map[name] = color_palette[idx % len(color_palette)]

        # Annotate each reason with its color
        for reason in iqf_rejection_reasons:
            group_name = reason.group.group_name if reason.group else ""
            reason.row_color = group_color_map.get(group_name, "#222")  # default dark gray

        
        # Add the subquery for iqf_physical_qty_edited
        iqf_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_physical_qty_edited')[:1]
        
        iqf_acceptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_acceptance')[:1]
        
        brass_rejection_qty_subquery = Brass_QC_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('total_rejection_quantity')[:1]

        # Subquery to get lot_id from Brass_QC_Rejection_ReasonStore (optional, usually same as stock_lot_id)
        brass_rejection_lot_id_subquery = Brass_QC_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('lot_id')[:1]
        

        brass_accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_accepted_tray_scan_status')[:1]
        
        brass_qc_rejection_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_rejection')[:1]
        
        iqf_rejection_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_rejection')[:1]
        
        brass_qc_few_cases_accptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_few_cases_accptance')[:1]
        
        iqf_accepted_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_accepted_qty_verified')[:1]
        
        iqf_few_cases_acceptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_few_cases_acceptance')[:1]
        
        iqf_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_onhold_picking')[:1]
        
        iqf_rejection_qty_subquery = IQF_Rejection_ReasonStore.objects.filter(
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
            stock_lot_id=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('lot_id')[:1]
            ),

            iqf_missing_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('iqf_missing_qty')[:1]
            ),
            iqf_physical_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('iqf_physical_qty')[:1]
            ),
            iqf_physical_qty_edited=iqf_physical_qty_edited_subquery,
            brass_accepted_tray_scan_status=brass_accepted_tray_scan_status_subquery,
            brass_qc_rejection=brass_qc_rejection_subquery,
            brass_qc_few_cases_accptance=brass_qc_few_cases_accptance_subquery,
            brass_rejection_total_qty=Subquery(brass_rejection_qty_subquery),
            brass_rejection_lot_id=Subquery(brass_rejection_lot_id_subquery),
            iqf_accepted_qty_verified=iqf_accepted_qty_verified_subquery,
            iqf_acceptance=Subquery(iqf_acceptance_subquery),
            iqf_rejection=Subquery(iqf_rejection_subquery),
            iqf_few_cases_acceptance=iqf_few_cases_acceptance_subquery,
            iqf_onhold_picking=iqf_onhold_picking_subquery,
            iqf_rejection_qty=Subquery(iqf_rejection_qty_subquery),
            
            iqf_accepted_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('iqf_accepted_qty')[:1]
            ),
            
            accepted_tray_scan_status=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('accepted_tray_scan_status')[:1]
            ),
            IQF_pick_remarks=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('IQF_pick_remarks')[:1]
            ),

            
        ).filter(
            Q(brass_qc_few_cases_accptance=True) | Q(brass_qc_rejection=True)
        )


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
            'wiping_required',
            'stock_lot_id',
            'iqf_missing_qty',
            'iqf_physical_qty',
            'iqf_physical_qty_edited',
            'accepted_tray_scan_status',
            'iqf_rejection_qty',
            'iqf_accepted_qty',
            'IQF_pick_remarks',
            'brass_accepted_tray_scan_status',
            'brass_qc_rejection',
            'brass_rejection_total_qty',
            'brass_rejection_lot_id',
            'brass_qc_few_cases_accptance',
            'iqf_accepted_qty_verified',
            'iqf_acceptance',
            'iqf_rejection',
            'iqf_few_cases_acceptance',
            'iqf_onhold_picking',
        ))
        
        for data in master_data:
            print(data['batch_id'], data['brass_rejection_total_qty'])

        for data in master_data:
            brass_rejection_total_qty = data.get('brass_rejection_total_qty', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(brass_rejection_total_qty / tray_capacity)
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
            lot_id = data.get('stock_lot_id')
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock_obj:
                if total_stock_obj.iqf_physical_qty and total_stock_obj.iqf_physical_qty > 0:
                    data['available_qty'] = total_stock_obj.iqf_physical_qty
                else:
                    data['available_qty'] = data.get('brass_rejection_total_qty', 0)
            else:
                data['available_qty'] = 0

        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'iqf_rejection_reasons':iqf_rejection_reasons,
        }
        return Response(context, template_name=self.template_name)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')  
class IQFSaveIPCheckboxView(APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            lot_id = data.get("lot_id")
            missing_qty = data.get("missing_qty")

            if not lot_id:
                return Response({"success": False, "error": "Lot ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            total_stock.iqf_accepted_qty_verified = True

            # Fetch brass_rejection_total_qty from Brass_QC_Rejection_ReasonStore
            brass_rejection_obj = Brass_QC_Rejection_ReasonStore.objects.filter(lot_id=lot_id).first()
            brass_rejection_total_qty = brass_rejection_obj.total_rejection_quantity if brass_rejection_obj else 0

            if missing_qty not in [None, ""]:
                try:
                    missing_qty = int(missing_qty)
                except ValueError:
                    return Response({"success": False, "error": "Missing quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

                if missing_qty > brass_rejection_total_qty:
                    return Response(
                        {"success": False, "error": "Missing quantity must be less than or equal to assigned quantity."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Save missing qty and physical qty
                total_stock.iqf_missing_qty = missing_qty
                total_stock.iqf_physical_qty = brass_rejection_total_qty - missing_qty

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
class IQFSaveIPPickRemarkAPIView(APIView):
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
            batch_obj.IQF_pick_remarks = remark
            batch_obj.save(update_fields=['IQF_pick_remarks'])
            return JsonResponse({'success': True, 'message': 'Remark saved'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class IQFUpdateBatchQuantityAPIView(APIView):
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            batch_id = data.get('batch_id')
            new_quantity = data.get('iqf_physical_qty')
            if not batch_id or new_quantity is None:
                return JsonResponse({'success': False, 'error': 'Missing batch_id or quantity'}, status=400)
            # Find the TotalStockModel for this batch
            stock_obj = TotalStockModel.objects.filter(batch_id__batch_id=batch_id).first()
            if not stock_obj:
                return JsonResponse({'success': False, 'error': 'Stock not found for this batch'}, status=404)
            stock_obj.iqf_physical_qty = new_quantity
            stock_obj.iqf_physical_qty_edited = True  # <-- Set the flag here
            stock_obj.save(update_fields=['iqf_physical_qty', 'iqf_physical_qty_edited'])
            return JsonResponse({'success': True, 'message': 'Quantity updated'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class IQF_Accepted_form(APIView):

    def post(self, request, format=None):
        data = request.data
        lot_id = data.get("stock_lot_id")
        try:
            total_stock_data = TotalStockModel.objects.get(lot_id=lot_id)
            total_stock_data.iqf_acceptance = True
    
            # Use iqf_physical_qty if set and > 0, else use total_stock
            physical_qty = total_stock_data.iqf_physical_qty
            if not physical_qty or physical_qty == 0:
                physical_qty = total_stock_data.brass_rejection_total_qty
    
            total_stock_data.iqf_accepted_qty = physical_qty
    
            # Update process modules
            total_stock_data.next_process_module = "IQF"
            total_stock_data.last_process_module = "Brass QC"
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
class IQFBatchRejectionAPIView(APIView):
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

            # Get iqf_physical_qty if set and > 0, else use total_stock
            qty = total_stock.iqf_physical_qty if total_stock.iqf_physical_qty and total_stock.iqf_physical_qty > 0 else total_stock.brass_qc_accepted_qty

            # Set iqf_rejection = True

            total_stock.iqf_rejection = True
            total_stock.last_process_module = "Brass QC"
            total_stock.next_process_module = "Jig Loading"
            total_stock.save(update_fields=['iqf_rejection', 'last_process_module', 'next_process_module'])

            # Create IQF_Rejection_ReasonStore entry
            IQF_Rejection_ReasonStore.objects.create(
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
class IQFTrayRejectionAPIView(APIView):
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

            # Use brass_qc_rejection if set and > 0, else use total_stock
            available_qty = total_stock_obj.iqf_physical_qty if total_stock_obj.iqf_physical_qty and total_stock_obj.iqf_physical_qty > 0 else total_stock_obj.brass_qc_accepted_qty
            
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

            # Validate all tray_ids exist in TrayId table
            for item in tray_rejections:
                tray_id = item.get('tray_id')
                if tray_id and not TrayId.objects.filter(tray_id=tray_id).exists():
                    return Response({'success': False, 'error': f'Tray ID "{tray_id}" is not existing.'}, status=400)

            # 1. Save to IQF_Rejection_ReasonStore (all reasons for this lot)
            reason_ids = [item['reason_id'] for item in tray_rejections if int(item['qty']) > 0]
            reasons = IQF_Rejection_Table.objects.filter(rejection_reason_id__in=reason_ids)
            total_qty = sum(int(item['qty']) for item in tray_rejections if int(item['qty']) > 0)
            reason_store = IQF_Rejection_ReasonStore.objects.create(
                lot_id=lot_id,
                user=request.user,
                total_rejection_quantity=total_qty,
                batch_rejection=False
            )
            reason_store.rejection_reason.set(reasons)

            # 2. Save each tray scan to IQF_Rejected_TrayScan
            for item in tray_rejections:
                qty = int(item['qty'])
                if qty > 0:
                    reason_obj = IQF_Rejection_Table.objects.get(rejection_reason_id=item['reason_id'])
                    IQF_Rejected_TrayScan.objects.create(
                        lot_id=lot_id,
                        rejected_tray_quantity=qty,
                        rejection_reason=reason_obj,
                        user=request.user,
                        rejected_tray_id=item.get('tray_id', '')
                    )
            # --- Set iqf_few_cases_acceptance = True ---
          
            total_stock_obj.iqf_onhold_picking = True
            total_stock_obj.iqf_few_cases_acceptance = True
            total_stock_obj.iqf_accepted_qty = available_qty - total_qty

            total_stock_obj.save(update_fields=['iqf_few_cases_acceptance','iqf_onhold_picking','iqf_accepted_qty'])


            return Response({'success': True, 'message': 'Tray rejections saved.'})

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

@require_GET
def iqf_reject_check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    exists = TrayId.objects.filter(tray_id=tray_id).exists()
    return JsonResponse({'exists': exists})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def iqf_get_accepted_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        tray_id_store_qs = IQF_Accepted_TrayID_Store.objects.filter(lot_id=lot_id)
        
        # Check if there's draft data
        has_draft = tray_id_store_qs.filter(is_draft=True).exists()
        
        tray_id_store_data = [
            {
                'lot_id': obj.lot_id,
                'tray_id': obj.tray_id,
                'tray_qty': obj.tray_qty,
                'user': obj.user.username if obj.user else None,
                'is_draft': obj.is_draft,
                'is_save': obj.is_save,
            }
            for obj in tray_id_store_qs
        ]

        # Get model_no and tray_capacity from TotalStockModel
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        model_no = ""
        tray_capacity = 0
        total_stock = 0
        if stock:
            model_no = stock.model_stock_no.model_no if stock.model_stock_no else ""
            tray_capacity = stock.batch_id.tray_capacity if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity') else 0
            # Use iqf_physical_qty if set and > 0, else use total_stock
            if stock.iqf_physical_qty and stock.iqf_physical_qty > 0:
                total_stock = stock.iqf_physical_qty
            else:
                total_stock = stock.brass_qc_accepted_qty or 0

        # Get total rejection quantity for this lot
        total_rejection_qty = 0
        reason_store = IQF_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
        if reason_store:
            total_rejection_qty = reason_store.total_rejection_quantity

        # Calculate remaining stock for acceptance
        remaining_qty = total_stock - total_rejection_qty

        # If no accepted tray rows, generate rows based on remaining_qty and tray_capacity
        if not tray_id_store_data and stock and tray_capacity > 0 and remaining_qty > 0:
            qty_left = remaining_qty
            tray_id_store_data = []
            for i in range(ceil(remaining_qty / tray_capacity)):
                qty = tray_capacity if qty_left > tray_capacity else qty_left
                tray_id_store_data.append({
                    'lot_id': lot_id,
                    'tray_id': '',
                    'tray_qty': qty,
                    'user': None,
                    'sno': i + 1,
                    'is_draft': False,
                    'is_save': False,
                })
                qty_left -= qty

        # Add S.no for frontend
        for idx, row in enumerate(tray_id_store_data):
            row['sno'] = idx + 1

        return Response({
            'success': True,
            'rows': tray_id_store_data,
            'model_no': model_no,
            'has_draft': has_draft,  # Include draft status
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def iqf_view_tray_list(request):
    """
    Returns tray list for a given lot_id based on different conditions:
    1. If iqf_acceptance is True: get from TrayId table
    2. If batch_rejection is True: split total_rejection_quantity by tray_capacity and get tray_ids from TrayId
    3. If batch_rejection is False: return all trays from IQF_Accepted_TrayID_Store
    """
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)

    try:
        # Check if this lot has iqf_acceptance = True
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        iqf_acceptance = False
        tray_capacity = 0
        
        if stock:
            iqf_acceptance = stock.iqf_acceptance or False
            if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity'):
                tray_capacity = stock.batch_id.tray_capacity or 0

        tray_list = []

        # Condition 1: If iqf_acceptance is True, get from TrayId table
        if iqf_acceptance:
            trays = TrayId.objects.filter(lot_id=lot_id).order_by('id')
            for idx, tray_obj in enumerate(trays):
                tray_list.append({
                    'sno': idx + 1,
                    'tray_id': tray_obj.tray_id,
                    'tray_qty': tray_obj.tray_quantity,  # Assuming this field exists in TrayId model
                })
            
            return Response({
                'success': True,
                'iqf_acceptance': True,
                'batch_rejection': False,
                'total_rejection_qty': 0,
                'tray_capacity': tray_capacity,
                'trays': tray_list,
            })

        # Condition 2 & 3: Check rejection reason store (existing logic)
        reason_store = IQF_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
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
            # Not batch rejection: get from IQF_Accepted_TrayID_Store
            trays = IQF_Accepted_TrayID_Store.objects.filter(lot_id=lot_id).order_by('id')
            for idx, obj in enumerate(trays):
                tray_list.append({
                    'sno': idx + 1,
                    'tray_id': obj.tray_id,
                    'tray_qty': obj.tray_qty,
                })

        return Response({
            'success': True,
            'iqf_acceptance': iqf_acceptance,
            'batch_rejection': batch_rejection,
            'total_rejection_qty': total_rejection_qty,
            'tray_capacity': tray_capacity,
            'trays': tray_list,
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class IQFTrayValidateAPIView(APIView):
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
def IQF_check_accepted_tray_draft(request):
    """Check if draft data exists for accepted tray scan"""
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    
    try:
        has_draft = IQF_Accepted_TrayID_Store.objects.filter(
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
def iqf_save_accepted_tray_scan(request):
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
        IQF_Accepted_TrayID_Store.objects.filter(lot_id=lot_id).delete()

        total_qty = 0
        for row in rows:
            tray_id = row.get('tray_id')
            tray_qty = row.get('tray_qty')
            if not tray_id or tray_qty is None:
                continue
            total_qty += int(tray_qty)
            
            # Create with appropriate boolean flags based on draft_save parameter
            IQF_Accepted_TrayID_Store.objects.create(
                lot_id=lot_id,
                tray_id=tray_id,
                tray_qty=tray_qty,
                user=user,
                is_draft=draft_save,      # True if Draft button clicked
                is_save=not draft_save    # True if Submit button clicked
            )

        # Save/Update IQF_Accepted_TrayScan for this lot
        accepted_scan, created = IQF_Accepted_TrayScan.objects.get_or_create(
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
                stock.iqf_onhold_picking = False  # Reset onhold picking status
                stock.save(update_fields=['accepted_tray_scan_status', 'next_process_module', 'last_process_module', 'iqf_onhold_picking'])

        return Response({'success': True, 'message': 'Accepted tray scan saved.'})

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@require_GET
def iqf_check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    lot_id = request.GET.get('lot_id', '')  # This is your stock_lot_id

    # 1. Must exist in TrayId table and lot_id must match
    tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
    exists = bool(tray_obj)
    same_lot = exists and str(tray_obj.lot_id) == str(lot_id)

    # 2. Must NOT be in IQF_Rejected_TrayScan for this lot
    already_rejected = False
    if exists and same_lot and lot_id:
        already_rejected = IQF_Rejected_TrayScan.objects.filter(
            lot_id=lot_id,
            rejected_tray_id=tray_id
        ).exists()

    # Only valid if exists, same lot, and not already rejected
    is_valid = exists and same_lot and not already_rejected

    return JsonResponse({
        'exists': is_valid,
        'already_rejected': already_rejected,
        'not_in_same_lot': exists and not same_lot
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def iqf_get_rejected_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        rows = []
        for obj in IQF_Rejected_TrayScan.objects.filter(lot_id=lot_id):
            rows.append({
                'tray_id': obj.rejected_tray_id,
                'qty': obj.rejected_tray_quantity,
                'reason': obj.rejection_reason.rejection_reason,
                'reason_id': obj.rejection_reason.rejection_reason_id,
            })
        return Response({'success': True, 'rows': rows})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class IQFDeleteBatchAPIView(APIView):
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


class IQFCompletedTableView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'IQF/Iqf_Completed.html'

    def get(self, request):
        user = request.user

  
        iqf_rejection_reasons = IQF_Rejection_Table.objects.select_related('group').all()
        
        # Dynamically assign colors to each group name
        group_names = IP_RejectionGroup.objects.values_list('group_name', flat=True)
        color_palette = [
            "#e53935",  # red
            "#fb8c00",  # orange
            "#43a047",  # green
            "#1e88e5",  # blue
            "#8e24aa",  # purple
            "#fbc02d",  # yellow
            "#00897b",  # teal
            "#6d4c41",  # brown
            "#757575",  # grey
            "#3949ab",  # indigo
        ]
        group_color_map = {}
        for idx, name in enumerate(group_names):
            group_color_map[name] = color_palette[idx % len(color_palette)]

        # Annotate each reason with its color
        for reason in iqf_rejection_reasons:
            group_name = reason.group.group_name if reason.group else ""
            reason.row_color = group_color_map.get(group_name, "#222")  # default dark gray

        
        # Add the subquery for iqf_physical_qty_edited
        iqf_physical_qty_edited_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_physical_qty_edited')[:1]
        
        iqf_acceptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_acceptance')[:1]
        
        brass_rejection_qty_subquery = Brass_QC_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('total_rejection_quantity')[:1]

        # Subquery to get lot_id from Brass_QC_Rejection_ReasonStore (optional, usually same as stock_lot_id)
        brass_rejection_lot_id_subquery = Brass_QC_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('lot_id')[:1]
        

        brass_accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_accepted_tray_scan_status')[:1]
        
        brass_qc_rejection_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_rejection')[:1]
        
        iqf_rejection_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_rejection')[:1]
        
        brass_qc_few_cases_accptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('brass_qc_few_cases_accptance')[:1]
        
        iqf_accepted_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_accepted_qty_verified')[:1]
        
        iqf_few_cases_acceptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_few_cases_acceptance')[:1]
        
        iqf_onhold_picking_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_onhold_picking')[:1]
        
        iqf_rejection_qty_subquery = IQF_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('stock_lot_id')
        ).values('total_rejection_quantity')[:1]
        
        iqf_accepted_tray_scan_status_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_accepted_tray_scan_status')[:1]

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
            stock_lot_id=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('lot_id')[:1]
            ),

            iqf_missing_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('iqf_missing_qty')[:1]
            ),
            iqf_physical_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('iqf_physical_qty')[:1]
            ),
            iqf_physical_qty_edited=iqf_physical_qty_edited_subquery,
            brass_accepted_tray_scan_status=brass_accepted_tray_scan_status_subquery,
            brass_qc_rejection=brass_qc_rejection_subquery,
            brass_qc_few_cases_accptance=brass_qc_few_cases_accptance_subquery,
            brass_rejection_total_qty=Subquery(brass_rejection_qty_subquery),
            brass_rejection_lot_id=Subquery(brass_rejection_lot_id_subquery),
            iqf_accepted_qty_verified=iqf_accepted_qty_verified_subquery,
            iqf_acceptance=Subquery(iqf_acceptance_subquery),
            iqf_rejection=Subquery(iqf_rejection_subquery),
            iqf_few_cases_acceptance=iqf_few_cases_acceptance_subquery,
            iqf_onhold_picking=iqf_onhold_picking_subquery,
            iqf_rejection_qty=Subquery(iqf_rejection_qty_subquery),
            iqf_accepted_tray_scan_status=iqf_accepted_tray_scan_status_subquery,
            
            iqf_accepted_qty=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('iqf_accepted_qty')[:1]
            ),
            
            accepted_tray_scan_status=Subquery(
                TotalStockModel.objects.filter(lot_id=OuterRef('stock_lot_id')).values('accepted_tray_scan_status')[:1]
            ),
            IQF_pick_remarks=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('IQF_pick_remarks')[:1]
            ),

            
        ).filter(
            Q(iqf_acceptance=True)|Q(iqf_few_cases_acceptance=True)|
            Q(iqf_rejection=True)
        )


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
            'wiping_required',
            'stock_lot_id',
            'iqf_missing_qty',
            'iqf_physical_qty',
            'iqf_physical_qty_edited',
            'accepted_tray_scan_status',
            'iqf_rejection_qty',
            'iqf_accepted_qty',
            'IQF_pick_remarks',
            'brass_accepted_tray_scan_status',
            'brass_qc_rejection',
            'brass_rejection_total_qty',
            'brass_rejection_lot_id',
            'brass_qc_few_cases_accptance',
            'iqf_accepted_qty_verified',
            'iqf_acceptance',
            'iqf_rejection',
            'iqf_few_cases_acceptance',
            'iqf_onhold_picking',
            'iqf_accepted_tray_scan_status',
        ))
        
        for data in master_data:
            print(data['batch_id'], data['brass_rejection_total_qty'])

        for data in master_data:
            brass_rejection_total_qty = data.get('brass_rejection_total_qty', 0)
            tray_capacity = data.get('tray_capacity', 0)
            data['vendor_location'] = f"{data.get('vendor_internal', '')}_{data.get('location__location_name', '')}"
            if tray_capacity > 0:
                data['no_of_trays'] = math.ceil(brass_rejection_total_qty / tray_capacity)
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
            lot_id = data.get('stock_lot_id')
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock_obj:
                if total_stock_obj.iqf_physical_qty and total_stock_obj.iqf_physical_qty > 0:
                    data['available_qty'] = total_stock_obj.iqf_physical_qty
                else:
                    data['available_qty'] = data.get('brass_rejection_total_qty', 0)
            else:
                data['available_qty'] = 0

        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
            'iqf_rejection_reasons':iqf_rejection_reasons,
        }
        return Response(context, template_name=self.template_name)




class IQFRejectTableView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'IQF/Iqf_RejectTable.html'

    def get(self, request):
        user = request.user
        
        # Create subqueries for all fields
        last_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('last_process_module')[:1]

        iqf_accepted_qty_verified_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_accepted_qty_verified')[:1]
        
        lot_id_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('lot_id')[:1]
        
        next_process_module_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('next_process_module')[:1]
        
        iqf_few_cases_acceptance_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_few_cases_acceptance')[:1]
        
        
        
        iqf_rejection_subquery = TotalStockModel.objects.filter(
            batch_id=OuterRef('pk')
        ).values('iqf_rejection')[:1]
        
        iqf_rejection_total_qty_subquery= IQF_Rejection_ReasonStore.objects.filter(
            lot_id=OuterRef('lot_id')
        ).values('total_rejection_quantity')[:1]
        
        
        
        # FIXED: Use a more explicit approach for the rejection quantity
        # Instead of trying to reference the lot_id directly, we'll get it step by step
        
        # Only show rows where accepted_Ip_stock is True
        queryset = ModelMasterCreation.objects.filter(
            total_batch_quantity__gt=0
        ).annotate(
            last_process_module=Subquery(last_process_module_subquery),
            next_process_module=Subquery(next_process_module_subquery),
            iqf_accepted_qty_verified=Subquery(iqf_accepted_qty_verified_subquery),
            iqf_rejection_total_qty=Subquery(iqf_rejection_total_qty_subquery),
            iqf_few_cases_acceptance=Subquery(iqf_few_cases_acceptance_subquery),

            iqf_rejection=Subquery(iqf_rejection_subquery),
           
            stock_lot_id=Subquery(lot_id_subquery),
        ).filter(
            Q(iqf_rejection=True) |
            Q(iqf_few_cases_acceptance=True)
        )
        
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
            'iqf_accepted_qty_verified',
            'iqf_rejection',
            'iqf_few_cases_acceptance',
            'iqf_rejection_total_qty',
  
        ))

        # MANUAL APPROACH: Add rejection quantities manually
        # Since the subquery approach isn't working, let's add it manually
        for data in master_data:
            stock_lot_id = data.get('stock_lot_id')
            
            # Get rejection quantity manually
            first_letters = []
            if stock_lot_id:
                try:
                    rejection_record = IQF_Rejection_ReasonStore.objects.filter(
                        lot_id=stock_lot_id
                    ).first()
                    data['batch_rejection'] = rejection_record.batch_rejection if rejection_record else False

                    if rejection_record:
                        reasons = rejection_record.rejection_reason.all()
                        first_letters = [r.rejection_reason.strip()[0].upper() for r in reasons if r.rejection_reason]
                    data['rejection_reason_letters'] = first_letters       
                    if rejection_record:
                        data['iqf_rejection_total_qty'] = rejection_record.total_rejection_quantity
                        print(f"Found rejection for {stock_lot_id}: {rejection_record.total_rejection_quantity}")
                    else:
                        data['iqf_rejection_total_qty'] = 0
                        print(f"No rejection found for {stock_lot_id}")
                except Exception as e:
                    print(f"Error getting rejection for {stock_lot_id}: {str(e)}")
                    data['iqf_rejection_total_qty'] = 0
            else:
                data['iqf_rejection_total_qty'] = 0
                print(f"No stock_lot_id for batch {data.get('batch_id')}")
                data['batch_rejection'] = False
            
            # Rest of your existing logic
            total_stock = data.get('iqf_rejection_total_qty', 0)
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
def iqf_get_rejection_details(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        reason_store = IQF_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
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
    
