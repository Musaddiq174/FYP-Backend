from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PasswordResetOTP
from django.core.mail import send_mail
import random
from rest_framework import serializers
from .models import SubjectiveQuestion


#otp send
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.get(email=email)
        otp = str(random.randint(100000, 999999))

        # Save OTP
        PasswordResetOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        # Send email
        send_mail(
            subject="Your OTP Code",
            message=f"Use this code to reset your password: {otp}",
            from_email="your_email@gmail.com",
            recipient_list=[email],
        )

        return {"message": "OTP sent to email."}

class ResetPasswordWithOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email']
        otp = data['otp']
        user = User.objects.get(email=email)

        try:
            record = PasswordResetOTP.objects.get(user=user, otp=otp)
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

        return data

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.set_password(validated_data['new_password'])
        user.save()

        # Delete OTP record
        PasswordResetOTP.objects.filter(user=user).delete()

        return {"message": "Password reset successful."}



#regestration

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['email'],  # use email as username
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



# serializers.py



class SubjectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectiveQuestion
        fields = ['id', 'question_text', 'marks']

# accounts/serializers.py
from rest_framework import serializers
from .models import ClassSessionData

class ClassSessionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSessionData
        fields = ['id', 'title', 'description', 'meet_link', 'scheduled_at']
