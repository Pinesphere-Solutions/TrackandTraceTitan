from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render

# Create your views here.

class BrassPickTableView(APIView):
    def get(self, request):
        return render(request, 'Brass_Qc/Brass_PickTable.html')
    
class BrassCompletedView(APIView):
    def get(self, request):
        return render(request, 'Brass_Qc/Brass_Completed.html')
    
class IqfPickTableView(APIView):
    def get(self, request):
        return render(request, 'IQF/Iqf_PickTable.html')

class IqfCompletedTableView(APIView):
    def get(self, request):
        return render(request, 'IQF/Iqf_Completed.html')
    
class IqpRejectTableView(APIView):
    def get(self, request):
        return render(request, 'IQF/Iqp_RejectTable.html')
    
# Recovery views for Brass and IQF tables    
class R_BrassPickTableView(APIView):
    def get(self, request):
        return render(request, 'Recovery_BQ/Recovery_BQ_PickTable.html')
    
class R_BrassCompletedView(APIView):
    def get(self, request):
        return render(request, 'Recovery_BQ/Recovery_BQ_Completed.html')
    
class R_IqfPickTableView(APIView):
    def get(self, request):
        return render(request, 'Recovery_IQF/Recovery_Iqf_PickTable.html')
    
class R_IqfCompletedTableView(APIView):
    def get(self, request):
        return render(request, 'Recovery_IQF/Recovery_Iqf_Completed.html')
    
class R_IqpRejectTableView(APIView):
    def get(self, request):
        return render(request, 'Recovery_IQF/Recovery_Iqp_RejectTable.html')