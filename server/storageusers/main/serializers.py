from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import MyUser

class RegistrationSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if not data['username'].isalnum():
            raise serializers.ValidationError("Username incorrect")
        return data
    
    password = serializers.CharField(
        max_length=12,
        min_length=6,
        write_only=True,
    )

    username = serializers.CharField(
        max_length=30,
        min_length=4,
        write_only=True,
    )
    
    name = serializers.CharField(
        max_length=30,
        min_length=4,
        write_only=True,
    )

    isTeacher = serializers.BooleanField()

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = MyUser
        fields = ('username', 'password', 'token', 'name', 'isTeacher')

    def create(self, validated_data):
        return MyUser.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=30,write_only=True)
    password = serializers.CharField(max_length=12, write_only=True)

    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        username = data.get('username', None)
        password = data.get('password', None)

        if username is None:
            raise serializers.ValidationError(
                'An username is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this username and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }

# class ViewUserSerializer(serializers.Serializer):
#     id = serializers.IntegerField( read_only=True)
#     username = serializers.CharField(max_length=30, read_only=True)
#     name = serializers.CharField(max_length=30, read_only=True)
#     isTeacher = serializers.BooleanField(read_only=True)