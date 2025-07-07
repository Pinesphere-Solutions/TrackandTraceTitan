from django.urls import path
from .views import *
from .views import AdminPanelView, UserListCreateAPIView, UserDetailAPIView
from .views import DepartmentListCreateAPIView, RoleListCreateAPIView


urlpatterns = [
    path('index/',IndexView.as_view(),name="index"),
    path('adminPanel/', AdminPanelView.as_view(), name='adminPanel'),
    path("api/users/", UserListCreateAPIView.as_view(), name="user-create"),
    path("api/departments/", DepartmentListCreateAPIView.as_view(), name="departments"),
    path("api/roles/", RoleListCreateAPIView.as_view(), name="roles"),

]