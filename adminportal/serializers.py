from rest_framework import serializers
from modelmasterapp.models import *
from django.utils import timezone

class PolishFinishTypeSerializer(serializers.ModelSerializer):
    polish_finish = serializers.CharField(
        error_messages={
            'unique': "A polish finish with this name already exists. Please enter a unique name."
        }
    )
    polish_internal = serializers.CharField(
        error_messages={
            'unique': "A polish internal ID with this value already exists. Please enter a unique internal ID."
        }
    )

    class Meta:
        model = PolishFinishType
        fields = '__all__'
    
    def validate_polish_finish(self, value):
        if not value.strip():
            raise serializers.ValidationError("Polish finish name cannot be empty.")
        return value.strip()

    def validate(self, data):
        polish_finish = data.get('polish_finish', '').strip()
        polish_internal = data.get('polish_internal', '').strip()
        qs = PolishFinishType.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if polish_finish and qs.filter(polish_finish__iexact=polish_finish).exists():
            raise serializers.ValidationError({
                'polish_finish': "A polish finish with this name already exists. Please enter a unique name."
            })
        if polish_internal and qs.filter(polish_internal__iexact=polish_internal).exists():
            raise serializers.ValidationError({
                'polish_internal': "A polish internal ID with this value already exists. Please enter a unique internal ID."
            })
        return data

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)

class PlatingColorSerializer(serializers.ModelSerializer):
    plating_color = serializers.CharField(
        error_messages={
            'unique': "A plating color with this name already exists. Please enter a unique name."
        }
    )

    class Meta:
        model = Plating_Color
        fields = '__all__'
    
    def validate_plating_color(self, value):
        if not value.strip():
            raise serializers.ValidationError("Plating color name cannot be empty.")
        return value.strip()

    def validate(self, data):
        plating_color = data.get('plating_color', '').strip()
        qs = Plating_Color.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if plating_color and qs.filter(plating_color__iexact=plating_color).exists():
            raise serializers.ValidationError({
                'plating_color': "A plating color with this name already exists. Please enter a unique name."
            })
        return data

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)

class TrayTypeSerializer(serializers.ModelSerializer):
    tray_type = serializers.CharField(
        error_messages={
            'unique': "A tray type with this name already exists. Please enter a unique name."
        }
    )

    class Meta:
        model = TrayType
        fields = '__all__'
    
    def validate_tray_type(self, value):
        if not value.strip():
            raise serializers.ValidationError("Tray type name cannot be empty.")
        return value.strip()
    
    def validate_tray_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tray capacity must be greater than 0.")
        return value

    def validate(self, data):
        tray_type = data.get('tray_type', '').strip()
        qs = TrayType.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if tray_type and qs.filter(tray_type__iexact=tray_type).exists():
            raise serializers.ValidationError({
                'tray_type': "A tray type with this name already exists. Please enter a unique name."
            })
        return data

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)

class ModelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelImage
        fields = '__all__'

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)

class ModelMasterSerializer(serializers.ModelSerializer):
    model_no = serializers.CharField(
        error_messages={
            'unique': "A model with this number already exists. Please enter a unique model number."
        }
    )

    class Meta:
        model = ModelMaster
        fields = '__all__'
    
    def validate_model_no(self, value):
        if not value.strip():
            raise serializers.ValidationError("Model number cannot be empty.")
        return value.strip()

    def validate(self, data):
        model_no = data.get('model_no', '').strip()
        qs = ModelMaster.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if model_no and qs.filter(model_no__iexact=model_no).exists():
            raise serializers.ValidationError({
                'model_no': f"A model with number '{model_no}' already exists. Please enter a unique model number."
            })
        return data

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)

class LocationSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(
        error_messages={
            'unique': "A location with this name already exists. Please enter a unique name."
        }
    )

    class Meta:
        model = Location
        fields = '__all__'

    def validate_location_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Location name cannot be empty.")
        return value.strip()

    def validate(self, data):
        location_name = data.get('location_name', '').strip()
        qs = Location.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if location_name and qs.filter(location_name__iexact=location_name).exists():
            raise serializers.ValidationError({
                'location_name': "A location with this name already exists. Please enter a unique name."
            })
        return data

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)

class TrayIdSerializer(serializers.ModelSerializer):
    tray_type = serializers.PrimaryKeyRelatedField(queryset=TrayType.objects.all(), required=True)
    tray_id = serializers.CharField(
        error_messages={
            'unique': "A tray ID with this value already exists. Please enter a unique tray ID."
        }
    )

    class Meta:
        model = TrayId
        fields = '__all__'

    def validate_tray_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("Tray ID cannot be empty.")
        return value.strip()

    def validate(self, data):
        tray_id = data.get('tray_id', '').strip()
        tray_type = data.get('tray_type')
        tray_capacity = data.get('tray_capacity')
        
        # Check for duplicate tray_id
        qs = TrayId.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if tray_id and qs.filter(tray_id__iexact=tray_id).exists():
            raise serializers.ValidationError({
                'tray_id': f"A tray ID '{tray_id}' already exists. Please enter a unique tray ID."
            })
        
        # Validate tray capacity matches tray type
        if tray_type and tray_capacity is not None:
            if tray_type.tray_capacity != tray_capacity:
                raise serializers.ValidationError({
                    'tray_capacity': f"Tray capacity must match the selected tray type's capacity ({tray_type.tray_capacity})."
                })
        
        return data

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)

class CategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        error_messages={
            'unique': "A category with this name already exists. Please enter a unique name."
        }
    )

    class Meta:
        model = Category
        fields = '__all__'

    def validate_category_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        return value.strip()

    def validate(self, data):
        category_name = data.get('category_name', '').strip()
        qs = Category.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if category_name and qs.filter(category_name__iexact=category_name).exists():
            raise serializers.ValidationError({
                'category_name': "A category with this name already exists. Please enter a unique name."
            })
        return data

    def create(self, validated_data):
        # Ensure date_time is set to current time when creating
        validated_data['date_time'] = timezone.now()
        return super().create(validated_data)
    
class IPRejectionSerializer(serializers.ModelSerializer):
    rejection_reason = serializers.CharField(
        error_messages={
            'unique': "A rejection reason with this text already exists. Please enter a unique reason."
        }
    )

    class Meta:
        model = IP_Rejection_Table
        fields = '__all__'

    def validate_rejection_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError("Rejection reason cannot be empty.")
        return value.strip()

    def validate(self, data):
        rejection_reason = data.get('rejection_reason', '').strip()
        qs = IP_Rejection_Table.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if rejection_reason and qs.filter(rejection_reason__iexact=rejection_reason).exists():
            raise serializers.ValidationError({
                'rejection_reason': "A rejection reason with this text already exists. Please enter a unique reason."
            })
        return data

    def create(self, validated_data):
        # Optionally set fields like date_time if needed
        return super().create(validated_data)