from rest_framework import serializers
from .models import Users, Profile, ResetPasswordToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['username', 'email', 'phone_number', 'password', 'is_verified']
        extra_kwargs = {'password': {'write_only': True}, 'is_verified': {'read_only': True}}

    def create(self, validated_data):
        # Extract `is_verified` separately to ensure it defaults correctly
        is_verified = validated_data.pop('is_verified', False)  # Default to False if not provided

        user = Users.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            is_verified=is_verified
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'phone_number', 'name']

