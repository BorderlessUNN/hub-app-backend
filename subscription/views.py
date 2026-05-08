from django.shortcuts import render
from accounts.serializers import CustomUserSerializer
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from accounts.models import CustomUser
from django_filters.rest_framework import DjangoFilterBackend
from subscription.models import Subscription
from rest_framework.views import APIView
from django.db import transaction
from helpers.responses import CustomResponse, custom_post_schema
from payments.services import initiate_paystack_payment
from subscription.serializers import NonMemberSubscriptionSerializer
from accounts.permissions import AllowAnyButAdminIfAssigned
from accounts.permissions import IsAuthenticatedAndAdminIfAssigned
from subscription.serializers import MemberSubscriptionSerializer, SubscriptionResponseSerializer
from subscription.helpers import handle_admin_assigned_member_subscription, handle_non_member_is_admin_assigned_subscription
from drf_spectacular.utils import extend_schema, OpenApiResponse
# Create your views here.
class ActiveSubscriptionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ActiveSubscriptionView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ActiveSubscriptionPagination
    queryset = CustomUser.objects.filter(subscriptions__status=Subscription.SubscriptionStatus.ACTIVE)

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['email', 'phone_number']


class MemberSubscriptionView(APIView):
    serializer_class = MemberSubscriptionSerializer
    permission_classes = [IsAuthenticatedAndAdminIfAssigned]

    @custom_post_schema(MemberSubscriptionSerializer, SubscriptionResponseSerializer, status_code=201)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                installment_number = serializer.validated_data.get('installment_number')
                subscription = serializer.validated_data.get('subscription')
                user = serializer.validated_data.get('user')
                plan = serializer.validated_data.get('plan')
                admin_assigned = serializer.validated_data.get('is_admin_assigned')
                if subscription is None:
                    subscription = Subscription.objects.create(
                        user = user,
                        plan = plan,
                        admin_assigned = admin_assigned,
                    )
                if admin_assigned:
                    subscription.admin_assigned = True
                    subscription.save()
                    subscription = handle_admin_assigned_member_subscription(subscription, installment_number)
                    return CustomResponse(valid=True,
                        msg="Subscription created successfully",
                        data=SubscriptionResponseSerializer(subscription).data)
                    
                else:
                    paystack_response = initiate_paystack_payment(user, plan, subscription, installment_number)
                    if paystack_response.get('status') is True:
                        data = {
                        'authorization_url' : paystack_response.get('data').get('authorization_url'),
                        'reference' : paystack_response.get('data').get('reference'),
                        'subscription' : SubscriptionResponseSerializer(subscription).data,
                        }
                        return CustomResponse(valid=True,
                        msg="Payment initiated successfully",
                        data=data)
                    else:
                        return CustomResponse(valid=False,
                        msg="Payment failed",
                        data=paystack_response.get('message'))
        except Exception as e:
            return CustomResponse(valid=False,
             msg=str(e),
              data=None)

class NonMemberSubscriptionView(APIView):
    serializer_class = NonMemberSubscriptionSerializer
    permission_classes = [AllowAnyButAdminIfAssigned]

    @custom_post_schema(NonMemberSubscriptionSerializer, SubscriptionResponseSerializer, status_code=201)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try: 
            with transaction.atomic():
                
                admin_assigned = serializer.validated_data.get('is_admin_assigned')
                if admin_assigned:
                    subscription = serializer.save()
                    subscription.admin_assigned = True
                    subscription.save()
                    subscription = handle_non_member_is_admin_assigned_subscription(subscription)
                    return CustomResponse(valid=True,
                        msg="Subscription created successfully",
                        data=SubscriptionResponseSerializer(subscription).data)
                    
                else:
                    subscription = serializer.save()
                    user = subscription.user
                    plan = subscription.plan
                    paystack_response = initiate_paystack_payment(user, plan, subscription)
                    print(paystack_response)
                    if paystack_response.get('status') is True:
                        data = {
                        'authorization_url' : paystack_response.get('data').get('authorization_url'),
                        'reference' : paystack_response.get('data').get('reference'),
                        'subscription' : SubscriptionResponseSerializer(subscription).data,
                        }
                        return CustomResponse(valid=True,
                        msg="Payment initiated successfully",
                        data=data)
                    else:
                        return CustomResponse(valid=False,
                        msg="Payment initiation failed",
                        data=paystack_response.get('message'))
        except Exception as e:
            return CustomResponse(valid=False,
             msg=str(e),
              data=None)

class SubscriptionView(APIView):
    serializer_class = SubscriptionResponseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()

    @extend_schema(
        responses={200: OpenApiResponse(response=SubscriptionResponseSerializer(many=True))},
    )
    def get(self, request):
        subscriptions = Subscription.objects.all()
        return CustomResponse(
            valid=True,
            msg="Subscriptions fetched successfully",
            data=SubscriptionResponseSerializer(subscriptions, many=True).data,
        )