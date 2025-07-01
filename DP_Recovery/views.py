from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

class RecoveryView(TemplateView):
    template_name = "DP_Recovery/Recovery.html"

class Recovery_BulkUpload(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Recovery_DP/Recovery_DP_BulkUpload.html'

    def get(self, request, format=None):
        context = {}
        return Response(context)

class Recovery_DPPickTableView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Recovery_DP/Recovery_DP_PickTable.html'

    def get(self, request, format=None):
        context = {}
        return Response(context)

class Recovery_DPCompletedTableView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Recovery_DP/Recovery_DP_Completed_Table.html'

    def get(self, request, format=None):
        context = {}
        return Response(context)