"""
URL configuration for watchcase_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    
    path('',include('modelmasterapp.urls')),
    path('dashboard/', TemplateView.as_view(template_name="index.html"), name="root"),
    path('home/', TemplateView.as_view(template_name="index.html"), name="home"),
    path('admin/', admin.site.urls),
    path('adminportal/',include('adminportal.urls')),
    path('dayplanning/',include('DayPlanning.urls')),
    path('recovery/', include('DP_Recovery.urls')),
    path('jigloading/', include('JigLoading.urls')),
    path('inprocessinspection/', include('Inprocess_Inspection.urls')),
    path('jigunloading/', include('Jig_Unloading.urls')),
    path('nickelaudit/', include('Nickel_Audit.urls')),
    path('spiderspindle/', include('Spider_Spindle.urls')),
    path('brass_qc/',include('Brass_Qc.urls')),
    path('inputscreening/',include('InputScreening.urls')),
    
    path('nickel_inspection/', include('Nickel_Inspection.urls')),
    path('iqf/', include('IQF.urls')),
    path('adminportal/',include('adminportal.urls')),
    path('modelmaster/', TemplateView.as_view(template_name="modelmaster.html"), name='modelmaster'),
    path('viewmasters/', TemplateView.as_view(template_name="viewmasters.html"), name='viewmasters'),
    path('visualaid/', TemplateView.as_view(template_name="VisualAid.html"), name='VisualAid'),
    path('recovery_dp/',include('Recovery_DP.urls')),
    
 




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
