from django.contrib.auth.models import User 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework.permissions import AllowAny

from modelmasterapp.models import UserProfile, Department, Role
from .serializers import UserSerializer, DepartmentSerializer, RoleSerializer


def generate_custom_user_id():
    last_profile = UserProfile.objects.order_by('-created_at').first()
    if not last_profile or not last_profile.custom_user_id:
        return 'T01'
    last_number = int(last_profile.custom_user_id[1:])
    return f'T{last_number + 1:02d}'


class IndexView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'

    def get(self, request, format=None):
        return Response({'user': request.user})


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

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Create user manually
            user = User.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                email=serializer.validated_data['email'],
                username=serializer.validated_data['email']  # or another unique value
            )

            profile_data = serializer.validated_data['profile']
            custom_user_id = generate_custom_user_id()

            UserProfile.objects.create(
                user=user,
                custom_user_id=custom_user_id,
                department=profile_data['department'],
                role=profile_data['role'],
                manager=profile_data.get('manager', ''),
                employment_status=profile_data['employment_status']
            )

            print("[POST USER SUCCESS]", serializer.data)
            return Response({
                'message': 'User created successfully',
                'custom_user_id': custom_user_id
            }, status=status.HTTP_201_CREATED)

        print("[POST USER ERROR]", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
