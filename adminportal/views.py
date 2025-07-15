from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from modelmasterapp.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone  # Added timezone import
import json
from .serializers import *
import datetime

@method_decorator(login_required(login_url='login-api'), name='dispatch')
class IndexView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'

    def get(self, request, format=None):
        # Get current date and format it
        
        context = { 
            'user': request.user,
        }
        response = Response(context)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        return response
    
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class Visual_AidView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'ModelMaster/VisualAid.html'

    def get(self, request, format=None):
        context = {
            'user': request.user,
            # Add more context if needed
        }
        return Response(context)
    
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class DP_ViewmasterView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'ModelMaster/viewmasters.html'

    def get(self, request, format=None):
        # Fetch all ModelMaster and related master tables
        model_masters = ModelMaster.objects.all()
        polish_finishes = PolishFinishType.objects.all()
        plating_colors = Plating_Color.objects.all()
        tray_types = TrayType.objects.all()
        locations = Location.objects.all()
        model_images = ModelImage.objects.all()
        tray_ids = TrayId.objects.all()
        categories = Category.objects.all()
        ip_rejections = IP_Rejection_Table.objects.all()  # <-- Add this line
        
        context = {
            'model_masters': model_masters,
            'polish_finishes': polish_finishes,
            'plating_colors': plating_colors,
            'tray_types': tray_types,
            'locations': locations,
            'model_images': model_images,
            'tray_ids': tray_ids,
            'categories': categories,
            'ip_rejections': ip_rejections,  # <-- Add this line
        }
        return Response(context)

    def post(self, request, format=None):
        """Handle deletion of selected items"""
        try:
            action = request.POST.get('action')
            if action != 'delete':
                return JsonResponse({'success': False, 'error': 'Invalid action'})

            tab_name = request.POST.get('tab_name')
            selected_ids = request.POST.getlist('selected_ids')

            if not selected_ids:
                return JsonResponse({'success': False, 'error': 'No items selected'})

            # Map tab names to models
            model_mapping = {
                'model': ModelMaster,
                'polish': PolishFinishType,
                'plating': Plating_Color,
                'tray': TrayType,
                'vendor': Location,
                'images': ModelImage,
                'trayid': TrayId,
                'category': Category,
                'iprejection': IP_Rejection_Table,  # <-- Add this line
            }

            if tab_name not in model_mapping:
                return JsonResponse({'success': False, 'error': 'Invalid tab name'})

            model_class = model_mapping[tab_name]
            
            # Delete selected items
            deleted_count = 0
            for item_id in selected_ids:
                try:
                    item = get_object_or_404(model_class, id=item_id)
                    item.delete()
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting item {item_id}: {str(e)}")
                    continue

            return JsonResponse({
                'success': True, 
                'deleted_count': deleted_count,
                'message': f'Successfully deleted {deleted_count} item(s)'
            })

        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })


@method_decorator(login_required(login_url='login-api'), name='dispatch')
class DP_ModelmasterView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'ModelMaster/dp_modelmaster.html'

    def get(self, request, format=None):
        # Get all data for dropdowns and existing records
        context = {
            'polish_finishes': PolishFinishType.objects.all(),
            'plating_colors': Plating_Color.objects.all(),
            'tray_types': TrayType.objects.all(),
            'vendors': Vendor.objects.all(),
            'model_images': ModelImage.objects.all(),
            'model_masters': ModelMaster.objects.all(),
            'versions': Version.objects.all(),
            # Add categories for dropdown
            'categories': Category.objects.all(),
        }
        return Response(context)

    def post(self, request, format=None):
        # Handle Category form submission
        if 'category_name' in request.data:
            # Add current datetime to the request data
            data = request.data.copy()
            data['date_time'] = timezone.now()
            
            serializer = CategorySerializer(data=data)
            if serializer.is_valid():
                category = serializer.save()
                # Redirect to same page with category_name in query params
                from django.shortcuts import redirect
                return redirect(f"/adminportal/dp_modelmaster/?category_name={category.category_name}")
            else:
                # Re-render page with errors
                context = {
                    'polish_finishes': PolishFinishType.objects.all(),
                    'plating_colors': Plating_Color.objects.all(),
                    'tray_types': TrayType.objects.all(),
                    'vendors': Vendor.objects.all(),
                    'model_images': ModelImage.objects.all(),
                    'model_masters': ModelMaster.objects.all(),
                    'versions': Version.objects.all(),
                    'categories': Category.objects.all(),
                    'category_form_errors': serializer.errors,
                }
                return Response(context)
        # ...handle other forms if needed...
        # ...existing code...


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class PolishFinishAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Polish Finish types"""
        polish_finishes = PolishFinishType.objects.all()
        serializer = PolishFinishTypeSerializer(polish_finishes, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Polish Finish type"""
        try:
            # Add current datetime to the request data
            data = request.data.copy()
            data['date_time'] = timezone.now()
            
            serializer = PolishFinishTypeSerializer(data=data)
            if serializer.is_valid():
                polish_finish = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Polish finish created successfully!',
                    'data': PolishFinishTypeSerializer(polish_finish).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating polish finish: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update Polish Finish type"""
        try:
            polish_finish = get_object_or_404(PolishFinishType, pk=pk)
            serializer = PolishFinishTypeSerializer(polish_finish, data=request.data)
            if serializer.is_valid():
                updated_polish_finish = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Polish finish updated successfully!',
                    'data': PolishFinishTypeSerializer(updated_polish_finish).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating polish finish: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete Polish Finish type"""
        try:
            polish_finish = get_object_or_404(PolishFinishType, pk=pk)
            polish_finish.delete()
            return Response({
                'success': True,
                'message': 'Polish finish deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting polish finish: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class PlatingColorAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Plating Colors"""
        plating_colors = Plating_Color.objects.all()
        serializer = PlatingColorSerializer(plating_colors, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Plating Color"""
        try:
            # Add current datetime to the request data
            data = request.data.copy()
            data['date_time'] = timezone.now()
            
            serializer = PlatingColorSerializer(data=data)
            if serializer.is_valid():
                plating_color = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Plating color created successfully!',
                    'data': PlatingColorSerializer(plating_color).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating plating color: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update Plating Color"""
        try:
            plating_color = get_object_or_404(Plating_Color, pk=pk)
            serializer = PlatingColorSerializer(plating_color, data=request.data)
            if serializer.is_valid():
                updated_plating_color = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Plating color updated successfully!',
                    'data': PlatingColorSerializer(updated_plating_color).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating plating color: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete Plating Color"""
        try:
            plating_color = get_object_or_404(Plating_Color, pk=pk)
            plating_color.delete()
            return Response({
                'success': True,
                'message': 'Plating color deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting plating color: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class TrayTypeAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Tray Types"""
        tray_types = TrayType.objects.all()
        serializer = TrayTypeSerializer(tray_types, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Tray Type"""
        try:
            # Add current datetime to the request data
            data = request.data.copy()
            data['date_time'] = timezone.now()
            
            serializer = TrayTypeSerializer(data=data)
            if serializer.is_valid():
                tray_type = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Tray type created successfully!',
                    'data': TrayTypeSerializer(tray_type).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating tray type: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update Tray Type"""
        try:
            tray_type = get_object_or_404(TrayType, pk=pk)
            serializer = TrayTypeSerializer(tray_type, data=request.data)
            if serializer.is_valid():
                updated_tray_type = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Tray type updated successfully!',
                    'data': TrayTypeSerializer(updated_tray_type).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating tray type: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete Tray Type"""
        try:
            tray_type = get_object_or_404(TrayType, pk=pk)
            tray_type.delete()
            return Response({
                'success': True,
                'message': 'Tray type deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting tray type: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class ModelImageAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Model Images"""
        model_images = ModelImage.objects.all()
        serializer = ModelImageSerializer(model_images, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Upload new Model Images"""
        try:
            # Handle multiple image uploads
            uploaded_images = []
            
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image in images:
                    image_data = {
                        'master_image': image,
                        'date_time': timezone.now()  # Add datetime for each image
                    }
                    serializer = ModelImageSerializer(data=image_data)
                    if serializer.is_valid():
                        model_image = serializer.save()
                        uploaded_images.append(ModelImageSerializer(model_image).data)
                    else:
                        return Response({
                            'success': False,
                            'message': 'Invalid image file',
                            'errors': serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    'success': True,
                    'message': f'{len(uploaded_images)} image(s) uploaded successfully!',
                    'data': uploaded_images
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'No images provided'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error uploading images: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete Model Image"""
        try:
            model_image = get_object_or_404(ModelImage, pk=pk)
            # Delete the actual file
            if model_image.master_image:
                model_image.master_image.delete()
            model_image.delete()
            return Response({
                'success': True,
                'message': 'Model image deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting model image: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class ModelMasterAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Model Masters"""
        model_masters = ModelMaster.objects.all()
        serializer = ModelMasterSerializer(model_masters, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Model Master"""
        try:
            # Add current datetime to the request data
            data = request.data.copy()
            data['date_time'] = timezone.now()
            
            serializer = ModelMasterSerializer(data=data)
            if serializer.is_valid():
                model_master = serializer.save()
                
                # Handle many-to-many relationship for images
                if 'images' in request.data:
                    image_ids = request.data.getlist('images') if hasattr(request.data, 'getlist') else request.data.get('images', [])
                    if image_ids:
                        model_master.images.set(image_ids)
                
                return Response({
                    'success': True,
                    'message': 'Model master created successfully!',
                    'data': ModelMasterSerializer(model_master).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating model master: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update Model Master"""
        try:
            model_master = get_object_or_404(ModelMaster, pk=pk)
            serializer = ModelMasterSerializer(model_master, data=request.data)
            if serializer.is_valid():
                updated_model_master = serializer.save()
                
                # Handle many-to-many relationship for images
                if 'images' in request.data:
                    image_ids = request.data.getlist('images') if hasattr(request.data, 'getlist') else request.data.get('images', [])
                    updated_model_master.images.set(image_ids)
                
                return Response({
                    'success': True,
                    'message': 'Model master updated successfully!',
                    'data': ModelMasterSerializer(updated_model_master).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating model master: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete Model Master"""
        try:
            model_master = get_object_or_404(ModelMaster, pk=pk)
            model_master.delete()
            return Response({
                'success': True,
                'message': 'Model master deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting model master: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class LocationAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Locations"""
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Location"""
        try:
            # Add current datetime to the request data
            data = request.data.copy()
            data['date_time'] = timezone.now()
            
            serializer = LocationSerializer(data=data)
            if serializer.is_valid():
                location = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Location created successfully!',
                    'data': LocationSerializer(location).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating location: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update Location"""
        try:
            location = get_object_or_404(Location, pk=pk)
            serializer = LocationSerializer(location, data=request.data)
            if serializer.is_valid():
                updated_location = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Location updated successfully!',
                    'data': LocationSerializer(updated_location).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating location: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete Location"""
        try:
            location = get_object_or_404(Location, pk=pk)
            location.delete()
            return Response({
                'success': True,
                'message': 'Location deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting location: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class TrayIdAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Tray IDs"""
        tray_ids = TrayId.objects.all()
        serializer = TrayIdSerializer(tray_ids, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Tray ID"""
        try:
            # Convert tray_type to pk if needed (from string to int)
            data = request.data.copy()
            data['date_time'] = timezone.now()  # Add datetime
            
            if isinstance(data.get('tray_type'), str) and data.get('tray_type').isdigit():
                data['tray_type'] = int(data['tray_type'])
            serializer = TrayIdSerializer(data=data)
            if serializer.is_valid():
                tray_id = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Tray ID created successfully!',
                    'data': TrayIdSerializer(tray_id).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating tray id: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update Tray ID"""
        try:
            tray_id_obj = get_object_or_404(TrayId, pk=pk)
            data = request.data.copy()
            if isinstance(data.get('tray_type'), str) and data.get('tray_type').isdigit():
                data['tray_type'] = int(data['tray_type'])
            serializer = TrayIdSerializer(tray_id_obj, data=data)
            if serializer.is_valid():
                updated_tray_id = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Tray ID updated successfully!',
                    'data': TrayIdSerializer(updated_tray_id).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating tray id: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class CategoryAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all Categories"""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new Category"""
        try:
            # Add current datetime to the request data
            data = request.data.copy()
            data['date_time'] = timezone.now()
            
            serializer = CategorySerializer(data=data)
            if serializer.is_valid():
                category = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Category created successfully!',
                    'data': CategorySerializer(category).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating category: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update Category"""
        try:
            category = get_object_or_404(Category, pk=pk)
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                updated_category = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Category updated successfully!',
                    'data': CategorySerializer(updated_category).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating category: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete Category"""
        try:
            category = get_object_or_404(Category, pk=pk)
            category.delete()
            return Response({
                'success': True,
                'message': 'Category deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting category: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class IPRejectionAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """Get all IP Rejection Reasons"""
        rejections = IP_Rejection_Table.objects.all()
        serializer = IPRejectionSerializer(rejections, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create new IP Rejection Reason"""
        try:
            data = request.data.copy()
            data['date_time'] = timezone.now()
 
            serializer = IPRejectionSerializer(data=data)
            if serializer.is_valid():
                rejection = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Rejection reason created successfully!',
                    'data': IPRejectionSerializer(rejection).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating rejection reason: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """Update IP Rejection Reason"""
        try:
            rejection = get_object_or_404(IP_Rejection_Table, pk=pk)
            serializer = IPRejectionSerializer(rejection, data=request.data)
            if serializer.is_valid():
                updated_rejection = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Rejection reason updated successfully!',
                    'data': IPRejectionSerializer(updated_rejection).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error updating rejection reason: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete IP Rejection Reason"""
        try:
            rejection = get_object_or_404(IP_Rejection_Table, pk=pk)
            rejection.delete()
            return Response({
                'success': True,
                'message': 'Rejection reason deleted successfully!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error deleting rejection reason: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Utility view to get dropdown data
@method_decorator(login_required(login_url='login-api'), name='dispatch')
class ModelMasterDropdownDataAPIView(APIView):
    renderer_classes = [JSONRenderer]
    
    def get(self, request):
        """Get all dropdown data for Model Master form"""
        try:
            data = {
                'polish_finishes': list(PolishFinishType.objects.values('id', 'polish_finish')),
                'plating_colors': list(Plating_Color.objects.values('id', 'plating_color')),
                'tray_types': list(TrayType.objects.values('id', 'tray_type', 'tray_capacity')),
                'vendors': list(Vendor.objects.values('id', 'vendor_name')),
                'model_images': list(ModelImage.objects.values('id', 'master_image')),
                'versions': list(Version.objects.values('id', 'version_name')),
                'locations': list(Location.objects.values('id', 'location_name')),
                'tray_ids': list(TrayId.objects.values('id', 'tray_id', 'tray_type', 'tray_capacity')),
                'categories': list(Category.objects.values('id', 'category_name')),
            }
            return Response({
                'success': True,
                'data': data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error fetching dropdown data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)