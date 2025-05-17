from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import CustomUser, Plan, Subscription, Invoice
from django.utils import timezone

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        Token.objects.create(user=user)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return {'token': token.key}
        raise serializers.ValidationError("Invalid username or password")

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['user', 'start_date', 'end_date', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        plan = validated_data['plan']

        # Check if user already has an active subscription
        if Subscription.objects.filter(user=user, status='active').exists():
            raise serializers.ValidationError("You already have an active subscription.")

        start_date = timezone.now().date()
        if plan.billing_interval == 'monthly':
            end_date = start_date + timezone.timedelta(days=30)
        else:
            end_date = start_date + timezone.timedelta(days=365)

        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        return subscription

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
