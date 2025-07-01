from django.urls import path
from . import views

urlpatterns = [
    path('composition/', views.JigCompositionView.as_view(), name='jig_composition'),
    path('JigView/', views.JigView.as_view(), name='JigView'),
    path('JigCompletedTable/', views.JigCompletedTable.as_view(), name='JigCompletedTable'),
]