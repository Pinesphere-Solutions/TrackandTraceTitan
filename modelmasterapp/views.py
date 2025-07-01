from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from modelmasterapp.models import *  # Import the TrayId model
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from modelmasterapp.models import TrayId, ModelMasterCreation, TotalStockModel  # Import the required models
from django.contrib.auth import authenticate, login, logout
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class BaseAPIView(APIView):
    """
    API View to return user details, fetch TrayId data based on barcodeInput,
    and fetch additional details from ModelMasterCreation and TotalStockModel.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        # Fetch user details
        user = request.user
        context = {
            'username': user.username,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }

        # Get barcodeInput from query parameters
        barcode_input = request.query_params.get('barcodeInput')
        if barcode_input:
            try:
                # Fetch the TrayId object based on the barcodeInput
                tray = get_object_or_404(TrayId, tray_id=barcode_input)
                print(f"[DEBUG] TrayId fetched: {tray.tray_id} - {tray.lot_id} - {tray.tray_quantity}")

                # Add TrayId details to the response
                context['tray_details'] = {
                    'tray_id': tray.tray_id,
                    'lot_id': tray.lot_id,
                    'tray_quantity': tray.tray_quantity,
                }

                # Fetch the batch_id and model_stock_no from TrayId
                batch_id = tray.batch_id
                model_stock_no = tray.batch_id.model_stock_no if tray.batch_id else None

                if batch_id and model_stock_no:
                    # Check if the batch_id and model_stock_no exist in ModelMasterCreation
                    try:
                        model_master = get_object_or_404(
                            ModelMasterCreation,
                            batch_id=batch_id.batch_id,  # Match batch_id
                            model_stock_no=model_stock_no  # Match model_stock_no
                        )
                        print(f"[DEBUG] ModelMasterCreation fetched for batch_id {batch_id.batch_id} and model_stock_no {model_stock_no}")

                        # Fetch associated images
                        mmc = batch_id  # assuming batch_id is ModelMasterCreation instance
                        model_images = [img.master_image.url for img in mmc.images.all()] if mmc else []
                        print(f"[DEBUG] ModelMasterCreation images fetched: {model_images}")
                        
                        # Add ModelMasterCreation details to the response
                        context['model_master_details'] = {
                            'model_stock_no': model_master.model_stock_no.model_no,
                            'polish_finish': model_master.polish_finish,
                            'plating_color': model_master.plating_color,
                            'version': model_master.version.version_name,
                            'vendor_internal': model_master.vendor_internal,
                            'location': model_master.location.location_name if model_master.location else None,
                            'model_images': model_images,  # ✅ Pass the actual list of URLs
                        }
                    except Exception as e:
                        print(f"[ERROR] Error fetching ModelMasterCreation: {e}")
                        context['model_master_details'] = f"ModelMasterCreation not found for batch_id: {batch_id.batch_id} and model_stock_no: {model_stock_no}"
                else:
                    print("[DEBUG] No batch_id or model_stock_no found in TrayId")
                    context['model_master_details'] = "No batch_id or model_stock_no found in TrayId"

                # Fetch TotalStockModel details based on lot_id
                try:
                    total_stock = get_object_or_404(TotalStockModel, lot_id=tray.lot_id)
                    print(f"[DEBUG] TotalStockModel fetched for lot_id {tray.lot_id}")

                    # Add TotalStockModel details to the response
                    context['total_stock_details'] = {
                        'last_process_date_time': total_stock.last_process_date_time,
                        'last_process_module': total_stock.last_process_module,
                        'next_process_module': total_stock.next_process_module,
                        'total_stock': total_stock.total_stock,  # Include total_stock in the response
                    }
                except Exception as e:
                    print(f"[ERROR] Error fetching TotalStockModel: {e}")
                    context['total_stock_details'] = f"TotalStockModel not found for lot_id: {tray.lot_id}"

            except Exception as e:
                print(f"[ERROR] Error fetching TrayId: {e}")
                return Response({
                    'success': False,
                    'error': f"TrayId not found for barcodeInput: {barcode_input}"
                }, status=status.HTTP_404_NOT_FOUND)

        return Response(context, status=status.HTTP_200_OK)
    
class LoginAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        return Response({}, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username') or request.POST.get('username')
        password = request.data.get('password') or request.POST.get('password')

        # Basic validation
        if not username or not password:
            error_msg = 'Please enter both username and password.'
            if request.accepted_renderer.format == 'html':
                return Response({
                    'error': error_msg,
                    'username': username or ''
                }, template_name=self.template_name, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'success': False, 
                'message': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                # ✅ Set session!
                login(request, user)  # <-- This is required for session authentication

                # If the request is from a browser (HTML form), redirect to index
                if request.accepted_renderer.format == 'html':
                    return redirect('index')  # Adjust path if needed
                # If API call, return JSON
                return Response({
                    'success': True, 
                    'message': 'Login successful'
                }, status=status.HTTP_200_OK)
            else:
                # User account is deactivated
                error_msg = 'Your account has been deactivated. Please contact support.'
                if request.accepted_renderer.format == 'html':
                    return Response({
                        'error': error_msg,
                        'username': username
                    }, template_name=self.template_name, status=status.HTTP_401_UNAUTHORIZED)
                return Response({
                    'success': False, 
                    'message': error_msg
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Invalid credentials
            error_msg = 'Invalid username or password. Please try again.'
            if request.accepted_renderer.format == 'html':
                return Response({
                    'error': error_msg,
                    'username': username  # Preserve username so user doesn't have to retype
                }, template_name=self.template_name, status=status.HTTP_401_UNAUTHORIZED)
            # For API, return JSON error
            return Response({
                'success': False, 
                'message': error_msg
            }, status=status.HTTP_401_UNAUTHORIZED)


def logout_view(request):
    logout(request)
    return redirect('login-api')  # Redirect to login page after logout
    