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

class PaymentResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_id = serializers.UUIDField(source='user.id')
    plan_id = serializers.UUIDField(source='plan.id')
    plan_name = serializers.CharField(source='plan.name')
    expires_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    is_expired = serializers.BooleanField()


class PaymentPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = ['id', 'name', 'price', 'hours', 'slug']