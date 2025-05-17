from django.urls import path
from .views import (
    SignupView, LoginView, PlanListView,
    SubscribeView, UnsubscribeView,
    InvoiceListView, InvoiceDetailView, PayInvoiceView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('plans/', PlanListView.as_view(), name='plans'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('invoices/', InvoiceListView.as_view(), name='invoices'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<int:pk>/pay/', PayInvoiceView.as_view(), name='pay-invoice'),
]
