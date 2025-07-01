from django.shortcuts import render


from django.views.generic import TemplateView

# Inprocess Inspection Main Table
class InprocessInspectionView(TemplateView):
    template_name = "Inprocess_Inspection/Inprocess_Inspection.html"

# Inprocess Inspection Complete Table    
class InprocessInspectionCompleteView(TemplateView):
        template_name = "Inprocess_Inspection/Inprocess_Inspection_Completed.html"
