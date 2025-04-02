from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'phone_number', 'user_type', 
                  'date_of_birth', 'id_number', 'is_profile_completed')
        read_only_fields = ('id', 'is_profile_completed')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'phone_number', 
                  'date_of_birth', 'id_number', 'is_profile_completed')
        read_only_fields = ('id', 'is_profile_completed', 'user_type')

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'phone_number', 
                  'company_name', 'address', 'date_of_birth', 
                  'id_number', 'is_profile_completed')
        read_only_fields = ('id', 'is_profile_completed', 'user_type')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, label='Confirm password')
    
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password', 'password2', 'user_type')
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords must match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['phone_number'],
            phone_number=validated_data['phone_number'],
            user_type=validated_data['user_type'],
            password=validated_data['password']
        )
        return user

class ProfileCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('date_of_birth', 'id_number')
        
    def update(self, instance, validated_data):
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.id_number = validated_data.get('id_number', instance.id_number)
        instance.is_profile_completed = True
        instance.save()
        return instance

