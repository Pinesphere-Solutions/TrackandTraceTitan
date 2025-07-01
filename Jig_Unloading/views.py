from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render


# Create your views here.
class Jig_Unloading_MainTable(APIView):
    def get(self, request):
        return render(request, 'Jig_Unloading/Jig_Unloading_Main.html')

class JigUnloading_Completedtable(APIView):
    def get(self, request):
        return render(request, 'Jig_Unloading/JigUnloading_Completedtable.html')