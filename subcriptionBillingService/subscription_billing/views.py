from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Plan, Subscription, Invoice
from .serializers import (
    UserSignupSerializer,
    UserLoginSerializer,
    PlanSerializer,
    SubscriptionSerializer,
    InvoiceSerializer
)
from django.utils import timezone

class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]

class SubscribeView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UnsubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sub = Subscription.objects.filter(user=request.user, status='active').first()
        if not sub:
            return Response({"detail": "No active subscription."}, status=status.HTTP_400_BAD_REQUEST)

        sub.status = 'cancelled'
        sub.end_date = timezone.now().date()
        sub.save()
        return Response({"detail": "Subscription cancelled."})

class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(subscription__user=self.request.user)

class InvoiceDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(subscription__user=self.request.user)

class PayInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            invoice = Invoice.objects.get(pk=pk, subscription__user=request.user)
        except Invoice.DoesNotExist:
            return Response({"detail": "Invoice not found."}, status=404)

        if invoice.status == 'paid':
            return Response({"detail": "Invoice already paid."})

        invoice.status = 'paid'
        invoice.save()
        return Response({"detail": "Invoice paid successfully."})
