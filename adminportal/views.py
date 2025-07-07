from django.contrib.auth.models import User 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.db import IntegrityError
from django.utils.crypto import get_random_string

from modelmasterapp.models import UserProfile, Department, Role
from .serializers import UserSerializer, DepartmentSerializer, RoleSerializer


# Function to generate a custom user ID
# This function generates a custom user ID in the format 'T01', 'T02', etc.
# It checks the last used custom user ID in the UserProfile model and increments it.
def generate_custom_user_id():
    last_profile = UserProfile.objects.order_by('-id').first()
    if last_profile and last_profile.custom_user_id and last_profile.custom_user_id[1:].isdigit():
        next_id = int(last_profile.custom_user_id[1:]) + 1
    else:
        next_id = 1
    return f'T{next_id:02d}'


# View to render the index page
# This view uses TemplateHTMLRenderer to render the index.html template.
class IndexView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'

    def get(self, request, format=None):
        return Response({'user': request.user})


# View to render the admin panel
# This view uses TemplateHTMLRenderer to render the adminPortal.html template.
class AdminPanelView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'AdminPortal/adminPortal.html'

    def get(self, request):
        next_user_id = generate_custom_user_id()
        return Response({
            'user': request.user,
            'next_user_id': next_user_id
        })


class UserListCreateAPIView(APIView):
    def get(self, request):
        users = User.objects.filter(is_superuser=False)
        serializer = UserSerializer(users, many=True)
        print("[GET USERS]", serializer.data)
        return Response(serializer.data)

    def post(self, request):  # <-- Indent this method!
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                email = serializer.validated_data['email'].lower().strip()

                # ✅ Check for duplicate email before user creation
                if User.objects.filter(email=email).exists():
                    return Response(
                        {"error": "A user with this email already exists. Please use a different email."},
                        status=400
                    )

                # ✅ Create User
                user = User.objects.create(
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    email=email,
                    username=f"{serializer.validated_data['first_name']}{serializer.validated_data['last_name']}"
                )

                # ✅ Extract profile data and get department/role names
                profile_data = serializer.validated_data.get('profile', {})
                department_name = profile_data.get('department')
                role_name = profile_data.get('role')

                if not department_name or not role_name:
                    return Response({"error": "Department and Role are required."}, status=400)

                # ✅ Get actual department instance
                try:
                    department = Department.objects.get(name__iexact=department_name)
                except Department.DoesNotExist:
                    return Response({"error": f"Department '{department_name}' not found."}, status=400)

                # ✅ Get actual role instance
                try:
                    role = Role.objects.get(name__iexact=role_name)
                except Role.DoesNotExist:
                    return Response({"error": f"Role '{role_name}' not found."}, status=400)

                # ✅ Create UserProfile
                profile = UserProfile.objects.create(
                    user=user,
                    custom_user_id=generate_custom_user_id(),
                    department=department,
                    role=role,
                    manager=profile_data.get('manager', ''),
                    employment_status=profile_data.get('employment_status', 'On-role')
                )

                new_user = User.objects.get(pk=user.pk)
                return Response(UserSerializer(new_user).data, status=status.HTTP_201_CREATED)

            except IntegrityError as e:
                print("[POST USER INTEGRITY ERROR]", str(e))
                return Response(
                    {"error": "Integrity error. Possibly duplicate or invalid data."},
                    status=400
                )

            except Exception as e:
                print("[POST USER ERROR]", str(e))
                return Response(
                    {"error": f"Unexpected error: {str(e)}"},
                    status=400
                )

        print("[POST USER ERROR]", serializer.errors)
        return Response(serializer.errors, status=400)


class UserDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"error": "User not found"}, status=404)
        serializer = UserSerializer(user)
        print("[GET USER]", serializer.data)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"error": "User not found"}, status=404)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("[PUT USER SUCCESS]", serializer.data)
            return Response(serializer.data)
        print("[PUT USER ERROR]", serializer.errors)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"error": "User not found"}, status=404)
        user.is_active = False
        user.save()
        print(f"[DELETE USER] Soft-deleted {user.email}")
        return Response({"status": "User deactivated"}, status=204)


class DepartmentListCreateAPIView(APIView):
    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleListCreateAPIView(APIView):
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
