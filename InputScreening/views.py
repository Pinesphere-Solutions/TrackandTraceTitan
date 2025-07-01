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

        # Use your Brass QC models here if different

        ip_rejection_reasons = IP_Rejection_Table.objects.select_related('group').all()
        
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
        for reason in ip_rejection_reasons:
            group_name = reason.group.group_name if reason.group else ""
            reason.row_color = group_color_map.get(group_name, "#222")  # default dark gray

        
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
            

           
        ).filter(tray_scan_exists=True).order_by('-last_process_date_time') 

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
                # Try to get accepted_tray_quantity from IP_Accepted_TrayScan
                accepted_scan = IP_Accepted_TrayScan.objects.filter(lot_id=lot_id).order_by('-id').first()
                if accepted_scan and accepted_scan.accepted_tray_quantity:
                    accepted_tray_quantity = accepted_scan.accepted_tray_quantity
                # Set the display value
                data['display_accepted_qty'] = accepted_tray_quantity or 0
            else:
                data['display_accepted_qty'] = total_ip_accepted_quantity

            
             # --- Add available_qty for each row ---
            lot_id = data.get('stock_lot_id')
            total_stock_obj = TotalStockModel.objects.filter(lot_id=lot_id).first()
            if total_stock_obj:
                if total_stock_obj.rejected_ip_stock and total_stock_obj.dp_physical_qty > 0:
                    data['available_qty'] = total_stock_obj.dp_physical_qty
                else:
                    data['available_qty'] = total_stock_obj.total_stock
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

# Add this to your views.py file

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SaveWipingStatusAPIView(APIView):
    """
    API View to save wiping status when radio button is checked
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            lot_id = data.get('lot_id')
            wiping_status = data.get('wiping_status', False)  # Expected to be True when checked
            
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
            
            # Update the wiping_status field
            total_stock.wiping_status = wiping_status
            total_stock.save(update_fields=['wiping_status'])
            
            return JsonResponse({
                'success': True, 
                'message': f'Wiping status updated to {wiping_status}',
                'lot_id': lot_id,
                'wiping_status': wiping_status
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

# Alternative GET method to check current wiping status
@require_GET
def get_wiping_status(request):
    """
    GET endpoint to retrieve current wiping status for a lot_id
    """
    lot_id = request.GET.get('lot_id')
    
    if not lot_id:
        return JsonResponse({
            'success': False, 
            'error': 'lot_id parameter is required'
        }, status=400)
    
    try:
        total_stock = TotalStockModel.objects.get(lot_id=lot_id)
        return JsonResponse({
            'success': True,
            'lot_id': lot_id,
            'wiping_status': total_stock.wiping_status,
            'wiping_required': getattr(total_stock.batch_id.model_stock_no, 'wiping_required', False) if total_stock.batch_id and total_stock.batch_id.model_stock_no else False
        })
    except TotalStockModel.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Stock record not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)
    
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')  
class SaveIPCheckboxView(APIView):
    def post(self, request, format=None):
        try:
            data = request.data
            lot_id = data.get("lot_id")
            missing_qty = data.get("missing_qty")

            if not lot_id:
                return Response({"success": False, "error": "Lot ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            total_stock = TotalStockModel.objects.get(lot_id=lot_id)
            total_stock.ip_person_qty_verified = True

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

                # Save missing qty and physical qty
                total_stock.dp_missing_qty = missing_qty
                total_stock.dp_physical_qty = total_stock.total_stock - missing_qty

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
            qty = total_stock.dp_physical_qty if total_stock.dp_physical_qty and total_stock.dp_physical_qty > 0 else total_stock.total_stock

            # Set rejected_ip_stock = True

            total_stock.rejected_ip_stock = True
            total_stock.last_process_module = "Input screening"
            total_stock.next_process_module = "Brass QC"
            total_stock.save(update_fields=['rejected_ip_stock', 'last_process_module', 'next_process_module'])

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

            # Use rejected_ip_stock if set and > 0, else use total_stock
            available_qty = total_stock_obj.dp_physical_qty if total_stock_obj.dp_physical_qty and total_stock_obj.dp_physical_qty > 0 else total_stock_obj.total_stock
            
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

            # 1. Save to IP_Rejection_ReasonStore (all reasons for this lot)
            reason_ids = [item['reason_id'] for item in tray_rejections if int(item['qty']) > 0]
            reasons = IP_Rejection_Table.objects.filter(rejection_reason_id__in=reason_ids)
            total_qty = sum(int(item['qty']) for item in tray_rejections if int(item['qty']) > 0)
            reason_store = IP_Rejection_ReasonStore.objects.create(
                lot_id=lot_id,
                user=request.user,
                total_rejection_quantity=total_qty,
                batch_rejection=False
            )
            reason_store.rejection_reason.set(reasons)

            # 2. Save each tray scan to IP_Rejected_TrayScan
            for item in tray_rejections:
                qty = int(item['qty'])
                if qty > 0:
                    reason_obj = IP_Rejection_Table.objects.get(rejection_reason_id=item['reason_id'])
                    IP_Rejected_TrayScan.objects.create(
                        lot_id=lot_id,
                        rejected_tray_quantity=qty,
                        rejection_reason=reason_obj,
                        user=request.user,
                        rejected_tray_id=item.get('tray_id', '')
                    )
            # --- Set few_cases_accepted_Ip_stock = True ---
          
            total_stock_obj.ip_onhold_picking = True
            total_stock_obj.few_cases_accepted_Ip_stock = True
            total_stock_obj.total_stock = available_qty - total_qty

            total_stock_obj.save(update_fields=['few_cases_accepted_Ip_stock','ip_onhold_picking','total_stock'])


            return Response({'success': True, 'message': 'Tray rejections saved.'})

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

@require_GET
def reject_check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    exists = TrayId.objects.filter(tray_id=tray_id).exists()
    return JsonResponse({'exists': exists})


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



# Update the get_accepted_tray_scan_data function to include verification status
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accepted_tray_scan_data(request):
    lot_id = request.GET.get('lot_id')
    if not lot_id:
        return Response({'success': False, 'error': 'Missing lot_id'}, status=400)
    try:
        tray_id_store_qs = IP_Accepted_TrayID_Store.objects.filter(lot_id=lot_id)
        
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

        # Get model_no, tray_capacity, and verification status from TotalStockModel
        stock = TotalStockModel.objects.filter(lot_id=lot_id).first()
        model_no = ""
        tray_capacity = 0
        total_stock = 0
        top_tray_verified = False
        verified_tray_qty = 0
        
        if stock:
            model_no = stock.model_stock_no.model_no if stock.model_stock_no else ""
            tray_capacity = stock.batch_id.tray_capacity if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity') else 0
            
            # Use dp_physical_qty if set and > 0, else use total_stock
            if stock.dp_physical_qty and stock.dp_physical_qty > 0:
                total_stock = stock.dp_physical_qty
            else:
                total_stock = stock.total_stock or 0
                
            # Get verification status
            top_tray_verified = stock.ip_top_tray_qty_verified or False
            verified_tray_qty = stock.ip_verified_tray_qty or 0

        # Get total rejection quantity for this lot
        total_rejection_qty = 0
        reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=lot_id).order_by('-id').first()
        if reason_store:
            total_rejection_qty = reason_store.total_rejection_quantity

        # Calculate remaining stock for acceptance
        remaining_qty = total_stock - total_rejection_qty

        # If no accepted tray rows, generate rows based on remaining_qty and tray_capacity
        if not tray_id_store_data and stock and tray_capacity > 0 and remaining_qty > 0:
            from math import ceil
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
            'has_draft': has_draft,
            'top_tray_verified': top_tray_verified,  # Add verification status
            'verified_tray_qty': verified_tray_qty,  # Add verified quantity
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ip_view_tray_list(request):
    """
    Returns tray list for a given lot_id based on different conditions:
    1. If accepted_Ip_stock is True: get from TrayId table
    2. If batch_rejection is True: split total_rejection_quantity by tray_capacity and get tray_ids from TrayId
    3. If batch_rejection is False: return all trays from IQF_Accepted_TrayID_Store
    """
    stock_lot_id = request.GET.get('stock_lot_id')
    
    # Validate the stock_lot_id parameter
    if not stock_lot_id or stock_lot_id in ['None', 'null', '']:
        return Response({
            'success': False, 
            'error': 'Valid stock_lot_id parameter is required'
        }, status=400)
    try:
        # Check if this lot has accepted_Ip_stock = True
        stock = TotalStockModel.objects.filter(lot_id=stock_lot_id).first()
        accepted_Ip_stock = False
        tray_capacity = 0
        
        if stock:
            accepted_Ip_stock = stock.accepted_Ip_stock or False
            if stock.batch_id and hasattr(stock.batch_id, 'tray_capacity'):
                tray_capacity = stock.batch_id.tray_capacity or 0

        tray_list = []

        # Condition 1: If accepted_Ip_stock is True, get from TrayId table
        if accepted_Ip_stock:
            trays = TrayId.objects.filter(lot_id=stock_lot_id).order_by('id')
            for idx, tray_obj in enumerate(trays):
                tray_list.append({
                    'sno': idx + 1,
                    'tray_id': tray_obj.tray_id,
                    'tray_qty': tray_obj.tray_quantity,  # Assuming this field exists in TrayId model
                })
            
            return Response({
                'success': True,
                'accepted_Ip_stock': True,
                'batch_rejection': False,
                'total_rejection_qty': 0,
                'tray_capacity': tray_capacity,
                'trays': tray_list,
            })

        # Condition 2 & 3: Check rejection reason store (existing logic)
        reason_store = IP_Rejection_ReasonStore.objects.filter(lot_id=stock_lot_id).order_by('-id').first()
        batch_rejection = False
        total_rejection_qty = 0
        
        if reason_store:
            batch_rejection = reason_store.batch_rejection
            total_rejection_qty = reason_store.total_rejection_quantity

        if batch_rejection and total_rejection_qty > 0 and tray_capacity > 0:
            # Batch rejection: split total_rejection_qty by tray_capacity, get tray_ids from TrayId
            tray_ids = list(TrayId.objects.filter(lot_id=stock_lot_id).values_list('tray_id', flat=True))
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
            # Not batch rejection: get from IP_Accepted_TrayID_Store
            trays = IP_Accepted_TrayID_Store.objects.filter(lot_id=stock_lot_id).order_by('id')
            for idx, obj in enumerate(trays):
                tray_list.append({
                    'sno': idx + 1,
                    'tray_id': obj.tray_id,
                    'tray_qty': obj.tray_qty,
                })

        return Response({
            'success': True,
            'accepted_Ip_stock': accepted_Ip_stock,
            'batch_rejection': batch_rejection,
            'total_rejection_qty': total_rejection_qty,
            'tray_capacity': tray_capacity,
            'trays': tray_list,
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class IPTrayValidateAPIView(APIView):
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
                    'all_trays_in_ip_store': list(all_trays),
                    'tray_exists_in_ip_store': tray_exists
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




@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_accepted_tray_scan(request):
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
        IP_Accepted_TrayID_Store.objects.filter(lot_id=lot_id).delete()

        total_qty = 0
        for row in rows:
            tray_id = row.get('tray_id')
            tray_qty = row.get('tray_qty')
            if not tray_id or tray_qty is None:
                continue
            total_qty += int(tray_qty)
            
            # Create with appropriate boolean flags based on draft_save parameter
            IP_Accepted_TrayID_Store.objects.create(
                lot_id=lot_id,
                tray_id=tray_id,
                tray_qty=tray_qty,
                user=user,
                is_draft=draft_save,      # True if Draft button clicked
                is_save=not draft_save    # True if Submit button clicked
            )

        # Save/Update IP_Accepted_TrayScan for this lot
        accepted_scan, created = IP_Accepted_TrayScan.objects.get_or_create(
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
                stock.next_process_module = "Brass QC"
                stock.last_process_module = "Input Screening"
                stock.ip_onhold_picking = False  # Reset onhold picking status
                stock.save(update_fields=['accepted_tray_scan_status', 'next_process_module', 'last_process_module', 'ip_onhold_picking'])

        return Response({'success': True, 'message': 'Accepted tray scan saved.'})

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


@require_GET
def check_tray_id(request):
    tray_id = request.GET.get('tray_id', '')
    lot_id = request.GET.get('lot_id', '')  # This is your stock_lot_id

    # 1. Must exist in TrayId table and lot_id must match
    tray_obj = TrayId.objects.filter(tray_id=tray_id).first()
    exists = bool(tray_obj)
    same_lot = exists and str(tray_obj.lot_id) == str(lot_id)

    # 2. Must NOT be in IP_Rejected_TrayScan for this lot
    already_rejected = False
    if exists and same_lot and lot_id:
        already_rejected = IP_Rejected_TrayScan.objects.filter(
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
            total_ip_accepted_quantity=Subquery(
                TotalStockModel.objects.filter(batch_id=OuterRef('pk')).values('total_IP_accpeted_quantity')[:1]
            ), 
                      
            stock_lot_id=Subquery(lot_id_subquery),
            wiping_status=Subquery(wiping_status_subquery),
            last_process_date_time=Subquery(TotalStockModel.objects.filter(
                batch_id=OuterRef('pk')
            ).values('last_process_date_time')[:1]),
            
        ).filter(
            Q(accepted_Ip_stock=True) |
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
            'total_ip_accepted_quantity',
            'total_stock',
            'wiping_status',
            'last_process_date_time',
            'plating_stk_no',
            'polishing_stk_no',
            'category',
            'version__version_internal',
            'last_process_date_time',
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
                # Try to get accepted_tray_quantity from IP_Accepted_TrayScan
                accepted_scan = IP_Accepted_TrayScan.objects.filter(lot_id=lot_id).order_by('-id').first()
                if accepted_scan and accepted_scan.accepted_tray_quantity:
                    accepted_tray_quantity = accepted_scan.accepted_tray_quantity
                # Set the display value
                data['display_accepted_qty'] = accepted_tray_quantity or 0
            else:
                data['display_accepted_qty'] = total_ip_accepted_quantity

        
        print("=== END MANUAL LOOKUP ===")
            
        context = {
            'master_data': master_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'user': user,
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


    