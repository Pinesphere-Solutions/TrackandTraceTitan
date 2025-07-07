from modelmasterapp.models import Department, Role, UserProfile
from django.contrib.auth.models import User
from rest_framework import serializers

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'custom_user_id',
            'department',  # now a string
            'role',        # now a string
            'manager',
            'employment_status'
        ]



    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        department = profile_data.pop('department', None)
        role = profile_data.pop('role', None)
        user = User.objects.create(**validated_data)
        UserProfile.objects.create(
            user=user,
            department=department,
            role=role,
            **profile_data
        )
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.profile
            department = profile_data.pop('department', None)
            role = profile_data.pop('role', None)
            department_id = profile_data.pop('department_id', None)
            role_id = profile_data.pop('role_id', None)
            if department or department_id:
                profile.department = department or department_id
            if role or role_id:
                profile.role = role or role_id
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'profile'
        ]