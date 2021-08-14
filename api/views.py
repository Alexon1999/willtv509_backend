import requests
import stripe
import json
import pprint
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .serializers import *
from .models import *

# Create your views here.
# generics.ListAPIView: Concrete view for listing a queryset. #+ (GET)
# generics.RetrieveAPIView: Concrete view for retrieving a model instance. #+ (GET)
# generics.CreateAPIView: Concrete view for creating a model instance. #+ (POST)
# generics.ListCreateAPIView: Concrete view for listing a queryset or creating a model instance. #+ (GET, POST)
# generics.RetrieveUpdateDestroyAPIView: Concrete view for retrieving, updating or deleting a model instance #+ (GET,POST,DELETE)
# APIVIEW: all methods can be defined, only what we define will work

# permissions.IsAuthenticated: we should pass an Autorization header, the type is Bearer token

stripe.api_key = "sk_test_51J8GK0C1J1Je91FHFE4X3KOaCxzW3rO7BbYeftt7ovj0Zm5o6BMxAiKdbtRedi2gEYDCqTVmW33um8IH7LoAKZAD00WHkMF9XF"


# subscription
@api_view(['GET'])
def get_plans(request):
    # return JsonResponse(stripe.Price.list(expand=['data.product', 'data.tiers'], active=True))
    return Response(stripe.Price.list(expand=['data.product', 'data.tiers'], active=True))


class CheckoutSubscriptionSessionView(APIView):
    def post(self, request, *args, **kwargs):
        price_id = request.data.get('price_id')
        customer = request.data.get("customer")
        session = stripe.checkout.Session.create(
            # success_url=request.data.get(
            #     'origin') + '?session_id={CHECKOUT_SESSION_ID}',
            success_url=request.data.get(
                'success_url'),
            cancel_url=request.data.get('cancel_url'),
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': price_id,
                # For metered billing, do not pass quantity
                'quantity': 1
            }],
            customer=customer.get("monAbonnement").get("stripeCustomerID"),
            customer_update={"name": "auto"},
        )

        # return checkout session
        return Response(session, status=201)


class CheckoutPaymentSessionView(APIView):
    def post(self, request, *args, **kwargs):
        product = request.data.get('product')
        item = {
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product.get('title'),
                    "images": [
                        product.get('image_url'),
                    ],
                },
                "unit_amount": product.get('prix') * 100,
            },
            "quantity": 1,
        }

        session = stripe.checkout.Session.create(
            payment_method_types=[
                'card',
            ],
            line_items=[
                item
            ],
            mode='payment',
            success_url=request.data.get('success_url'),
            cancel_url=request.data.get('cancel_url'),
            customer=request.data.get('customer').get(
                "monAbonnement").get("stripeCustomerID"),
            customer_update={"name": "auto"},
            payment_intent_data={"receipt_email": request.data.get('customer').get(
                "email"), "metadata": {"product_id": product.get('id')}},

            # Shipping details
            # shipping_address_collection={
            #     'allowed_countries': ['US', 'CA'],
            # },
        )

        # return checkout session
        return Response(session, status=201)

# The customer portal is a secure, Stripe-hosted page that lets your customers manage their subscriptions and billing details.


class CustomerPortalView(APIView):
    def post(self, request, *args, **kwargs):
        session = stripe.billing_portal.Session.create(
            customer=request.data.get("customer").get(
                "monAbonnement").get("stripeCustomerID"),
            return_url=request.data.get("origin"),
        )

        # return billing_portal session object
        return Response(session, status=201)

# webhook: checkout.session.completed


class CheckoutSessionCompletedView(APIView):
    def post(self, request, *args, **kwargs):
        # pprint.pprint(request.data)
        return JsonResponse({'response': "ok"})


# webhook: invoice.paid
# Sent each billing interval when a payment succeeds.


class InvoicePaidView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # pprint.pprint(request.data)
        try:
            if data['data']['object']['subscription']:
                subscription_id = data['data']['object']['subscription']
                subscription = stripe.Subscription.retrieve(subscription_id)
                # pprint.pprint(subscription)

                client = Client.objects.get(
                    monAbonnement__stripeCustomerID=data['data']['object']['customer'])
                client.monAbonnement.status = subscription.get('status')
                client.monAbonnement.product_id = subscription.get(
                    'plan').get('product')
                client.monAbonnement.subscription_id = subscription_id
                client.monAbonnement.save(
                    update_fields=['status', 'product_id', 'subscription_id'])

            return JsonResponse({'response': "ok"})
        except:
            return JsonResponse({'response': "no"})


# webhook: invoice.payment_failed
# Sent each billing interval if there is an issue with your customer’s payment method.
class InvoicePaymentFailedView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # pprint.pprint(request.data)

        try:
            if data['data']['object']['subscription']:
                subscription_id = data['data']['object']['subscription']
                subscription = stripe.Subscription.retrieve(subscription_id)
                # pprint.pprint(subscription)

                client = Client.objects.get(
                    monAbonnement__stripeCustomerID=data['data']['object']['customer'])

                # on the frontend check if status is past_due , Notify your customer and send them to the customer portal to update their payment information
                # The subscription becomes past_due
                client.monAbonnement.status = subscription.get('status')

                client.monAbonnement.product_id = subscription.get(
                    'plan').get('product')
                client.monAbonnement.subscription_id = subscription_id

                client.monAbonnement.save(
                    update_fields=['status', 'product_id', 'subscription_id'])

            return JsonResponse({'response': "ok"})
        except:
            return JsonResponse({'response': "no"})


# webhook: customer.subscription.created, customer.subscription.updated, and customer.subscription.deleted
# deleted Occurs whenever a customer's subscription ends (with the immediat or in the end of current month) or customer canceled it


class HandleSubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # pprint.pprint(data)

        subscription = data['data']['object']
        customer = subscription['customer']

        try:
            client = Client.objects.get(
                monAbonnement__stripeCustomerID=customer)
            if data['type'] == 'customer.subscription.deleted':
                client.monAbonnement.status = None
                client.monAbonnement.product_id = None
                client.monAbonnement.subscription_id = None
            else:
                client.monAbonnement.status = subscription.get('status')

                client.monAbonnement.product_id = subscription.get(
                    'plan').get('product')
                client.monAbonnement.subscription_id = subscription['id']

            client.monAbonnement.save(
                update_fields=['status', 'product_id', 'subscription_id'])

            return JsonResponse({'response': "ok"})
        except:
            return JsonResponse({'response': "no"})


# webhook: payment_intent.succeeded
# a payment is succeded
class PaymentIntentSucceededView(APIView):
    def post(self, request, *args, **kwargs):
        # pprint.pprint(request.data)
        payment_intent = request.data['data']['object']

        try:
            if payment_intent['status'] == 'succeeded':
                client = Client.objects.get(
                    monAbonnement__stripeCustomerID=payment_intent.get('customer'))
                video = Video.objects.get(
                    id=payment_intent.get("metadata").get("product_id"))
                mon_video = MonVideo.objects.create(
                    payment_intent_id=payment_intent['id'], video=video, payer=True, mode='stripe')
                client.mesVideos.add(mon_video)

            return JsonResponse({'response': "ok"})
        except:
            return JsonResponse({'response': "no"})


# a payment via paypal is succeded
class PaypalPaymentSucceededView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(
                id=request.data.get('customer').get('id'))
            video = Video.objects.get(
                id=request.data.get("product").get('id'))
            mon_video = MonVideo.objects.create(
                payment_intent_id=request.data.get('transaction_id'), video=video, payer=True, mode='paypal')
            client.mesVideos.add(mon_video)

            return JsonResponse({'response': "ok"})
        except:
            return JsonResponse({'response': "no"})


# doc: https://gist.github.com/tichif/2a045112f863e19c05f526b022dfad9a

# get mon cash auth token
@api_view(['GET'])
def GetMonCashAuthToken(request):
    url = "https://98a04fbd9338bf35dce7dcc9bf38575f:AVTrkyMH2aQb2OWJ2dkj7XZS3XvxeEb4mujHIHvNpvyY6k6bwRnxez4HUXdy2pMN@sandbox.moncashbutton.digicelgroup.com/Api/oauth/token"

    payload = {'scope': 'read,write',
               'grant_type': 'client_credentials'}
    headers = {}

    response = requests.request(
        "POST", url, headers=headers, data=payload)

    return Response(response.json())


# mon cash create payment
@api_view(['POST'])
def MonCashCreatePayment(request):
    url = "https://sandbox.moncashbutton.digicelgroup.com/Api/v1/CreatePayment"
    exchange_rate_api = 'https://v6.exchangerate-api.com/v6/f443214be2016f623d80d133/latest/USD'

    # Haiti
    HTG = requests.get(exchange_rate_api).json()['conversion_rates']['HTG']

    payload = {'amount': request.data.get('amount') * HTG,
               'orderId': request.data.get('orderId')}

    headers = {
        'Authorization': request.data.get('token'),
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload))

    client = Client.objects.get(
        id=request.data.get('customer').get('id'))
    video = Video.objects.get(
        id=request.data.get("product").get('id'))

    # enregistrer mon video que si'il n'existe pas déjà dans la bdd
    if client.mesVideos.filter(video=video).count() == 0:
        mon_video = MonVideo.objects.create(
            video=video, payer=False, mode='moncash')
        client.mesVideos.add(mon_video)

    return Response(response.json())


# mon cash payment succeded
@api_view(['POST'])
def MonCashPaymentSucceeded(request):
    url = "https://sandbox.moncashbutton.digicelgroup.com/Api/v1/RetrieveTransactionPayment"

    payload = {'transactionId': request.data.get('transaction_id')}

    headers = {
        'Authorization': request.data.get('token'),
        'Content-Type': 'application/json'
    }
    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload))
    data = response.json()

    # print(data)

    if response.ok and data.get('payment'):
        if data.get('payment').get('message') == 'successful':
            client = Client.objects.get(
                id=request.data.get('customer_id'))
            mon_video = client.mesVideos.get(
                video__id=request.data.get('product_id'))
            mon_video.payer = True
            mon_video.payment_intent_id = data.get(
                'payment').get('transaction_id')
            mon_video.save(update_fields=['payer', 'payment_intent_id'])

            return Response({'payment': "success"})

    return Response({'payment': "failed"})


class CategorieListView(generics.ListAPIView):
    serializer_class = CategorieSerializer
    queryset = Categorie.objects.all()


class ClientCreateView(generics.CreateAPIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            customer = stripe.Customer.create(
                email=request.data.get('email')
            )

            monAbonnement = MonAbonnement.objects.create(
                stripeCustomerID=customer.id)

            client = Client.objects.create(email=request.data.get(
                'email'), username=request.data.get('username'), monAbonnement=monAbonnement)

            return Response(ClientSerializer(client).data, status=201)
        except:
            return Response({"error": "user not created"}, status=406)


class ClientView(APIView):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(email=request.data.get(
                'email'), username=request.data.get('username'))

            return Response(ClientSerializer(client).data, status=201)
        except:
            return Response({"error": "user not found"}, status=404)


class CategoriesVideosView(APIView):
    serializer_class = CategorieSerializer
    queryset = Categorie.objects.all()

    def get(self, request, *args, **kwargs):
        videos = Video.objects.filter(categorie=kwargs["pk"])
        return Response(VideoSerializer(videos, many=True).data)


@api_view(['GET'])
def CategoriesAndVideosView(request):
    return Response(CategorieVideosSerializer(Categorie.objects.all(), many=True).data)


class VideoDetailsView(generics.RetrieveAPIView):
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
