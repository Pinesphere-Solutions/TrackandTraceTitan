from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render

# Create your views here.
class Nickel_Audit__MainTable(APIView):
    def get(self, request):
        return render(request, 'Nickel_Audit/Nickel_Audit_Main.html')

class Nickel_Audit__CompleteTable(APIView):
    def get(self, request):
        return render(request, 'Nickel_Audit/NA_Complete.html')