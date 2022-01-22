from django.urls import path
from rest_framework_simplejwt import views as jwt_views

# import views  # ModuleNotFoundError: No module named 'views'
# from api import views  # absolute imports
# import api.views as views # absolute imports
# from api.views import CategorieListView  # absolute imports
from . import views  # relative imports
# from .views import CategorieListView  # relative imports
# import .views  # err: Relative imports cannot be used with "import .a" form; use "from . import a" instead

app_name = 'Api'

'''
base_url: api/
'''

urlpatterns = [
    path('categories/', views.CategorieListView.as_view()),
    path('categories/<int:pk>/', views.CategoriesVideosView.as_view()),
    path('categories-videos/', views.CategoriesAndVideosView),
    path('videos/query/<str:query>/', views.VideosBySearchQueryView.as_view()),
    path('videos/<int:pk>/', views.VideoDetailsView.as_view()),
    path('create-client/', views.ClientCreateView.as_view()),
    path('get-client/', views.ClientView.as_view()),
    path('get-plans/', views.get_plans),  # subscription plans
    path('get-subscription-checkout-session/',
         views.CheckoutSubscriptionSessionView.as_view()),
    path('get-payment-checkout-session/',
         views.CheckoutPaymentSessionView.as_view()),
    path('get-customer-portal/', views.CustomerPortalView.as_view()),

    # webhooks
    path('checkout-session-completed/',
         views.CheckoutSessionCompletedView.as_view()),
    path('invoice-paid/',
         views.InvoicePaidView.as_view()),
    path('invoice-payment-failed/',
         views.InvoicePaymentFailedView.as_view()),
    path('handle-customer-subscription/',
         views.HandleSubscriptionView.as_view()),
    path('payment-intent-succeded/',
         views.PaymentIntentSucceededView.as_view()),
    path('paypal-succeded-payment/',
         views.PaypalPaymentSucceededView.as_view()),
    path('moncash-auth-token/',
         views.GetMonCashAuthToken),
    path('moncash-create-payment/',
         views.MonCashCreatePayment),
    path('moncash-success-payment/',
         views.MonCashPaymentSucceeded),
]
