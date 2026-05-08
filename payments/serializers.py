from rest_framework import serializers
from django.utils import timezone

from accounts.models import CustomUser
from payments.models import Plans, Payment
from helpers.exceptions import CustomValidationException


class ConfirmPaymentSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    plan_id = serializers.UUIDField()

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        plan_id = attrs.get('plan_id')
        
        try:
            self.user = CustomUser.objects.get(id=user_id)
            self.plan = Plans.objects.get(id=plan_id)
            user_payment = Payment.objects.filter(user=self.user).first()
            if user_payment and not user_payment.is_expired:
                raise CustomValidationException("User already has an active payment", code=409)
        except CustomUser.DoesNotExist:
            raise CustomValidationException("User does not exist", code=404)
        except Plans.DoesNotExist:
            raise CustomValidationException("Plan does not exist", code=404)
        return attrs
    
    def confirm_payment(self):
        return self.user.payments.create(
            plan=self.plan,
            expires_at=timezone.now() + timezone.timedelta(hours=self.plan.hours)
        )

class PaymentResponseSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id')
    subscription_id = serializers.UUIDField(source='subscription.id')
    class Meta:
        model = Payment
        fields = ['id', 'user_id','subscription_id', 'amount', 'payment_type', 'payment_status', 'paystack_reference', 'installment_number', 'created_at', 'updated_at']


class PaymentPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = ['id', 'name', 'price', 'hours', 'slug', 'is_member_only', 'is_paid_in_installment', 'installment_price']
        read_only_fields = ['slug', 'id']
        
    def create(self, validated_data):
        plan = Plans.objects.create(**validated_data)
        return plan

class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField()