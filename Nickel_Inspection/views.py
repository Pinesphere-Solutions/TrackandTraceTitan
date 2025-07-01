from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

class Nickel_Inspection(TemplateView):
    template_name = "Nickel_Inspection/Nickel_Inspection.html"

class NI_Completed(TemplateView):
    template_name = "Nickel_Inspection/NI_Completed.html"

class NI_Rejected(TemplateView):
    template_name = "Nickel_Inspection/NI_Rejectedtable.html"