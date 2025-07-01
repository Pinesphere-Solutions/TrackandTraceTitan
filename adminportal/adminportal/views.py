from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from datetime import datetime

@method_decorator(login_required(login_url='login-api'), name='dispatch')
class IndexView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'

    def get(self, request, format=None):
        # Get current date and format it
        current_date = datetime.now()
        formatted_date = current_date.strftime("%d %b %Y")  # Format: 13 Jun 2025
        
        context = {
            'user': request.user,
            'current_date': formatted_date,
            'current_date_full': current_date  # In case you need the full datetime object
        }
        response = Response(context)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        return response