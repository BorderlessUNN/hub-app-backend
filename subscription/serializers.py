from rest_framework import serializers
from subscription.models import Subscription
from accounts.models import CustomUser
from accounts.utils import normalize_phone_number
from payments.models import Plans
from payments.models import Payment
class MemberSubscriptionSerializer(serializers.Serializer):
    """
    Despite the name, this also handles an *already-registered* non-member
    (looked up by user_id) purchasing/being granted an hourly pass - e.g.
    when an admin records an offline payment for a walk-in whose details
    were already captured. A brand-new/unregistered non-member instead goes
    through NonMemberSubscriptionSerializer, which creates the user record.
    """
    user_id = serializers.UUIDField()
    plan_id = serializers.UUIDField()
    is_admin_assigned = serializers.BooleanField(default=False)
    installment_number = serializers.ChoiceField(choices=Payment.InstallmentNumber.choices, allow_null=True, required=False)
    hours = serializers.IntegerField(required=False, min_value=1)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        plan_id = attrs.get('plan_id')
        installment_number = attrs.get('installment_number')
        hours = attrs.get('hours')
        plan = None
        user = None
        subscription = None
        try:
            user = CustomUser.objects.get(id=user_id)
            plan = Plans.objects.get(id=plan_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        except Plans.DoesNotExist:
            raise serializers.ValidationError("Plan does not exist")
        if plan.is_member_only and not user.is_member:
            raise serializers.ValidationError("This plan is only for members")
        if not plan.is_member_only and user.is_member:
            raise serializers.ValidationError("This plan is only for non-members")
        if not plan.is_member_only and not hours:
            raise serializers.ValidationError("Hours is required for a non-member plan")
        if plan.is_paid_in_installment:
            if not installment_number:
                raise serializers.ValidationError("Installment number is required")
            if installment_number == Payment.InstallmentNumber.TWO:
                try:
                    subscription = Subscription.objects.get(user=user, plan=plan, status=Subscription.SubscriptionStatus.PARTIAL_ACTIVE)
                except Subscription.DoesNotExist:
                    raise serializers.ValidationError("This user doesn't have a partial active subscription")

                payment = Payment.objects.filter(subscription=subscription, installment_number=Payment.InstallmentNumber.TWO, payment_status=Payment.PaymentStatus.SUCCESS).exists()
                if payment:
                        raise serializers.ValidationError("Second installment already paid")

            elif installment_number == Payment.InstallmentNumber.ONE:
                try:
                    subscription = Subscription.objects.get(user=user, plan=plan, status=Subscription.SubscriptionStatus.PARTIAL_ACTIVE)
                    payment = Payment.objects.filter(subscription=subscription, installment_number=Payment.InstallmentNumber.ONE, payment_status=Payment.PaymentStatus.SUCCESS).exists()
                    if payment:
                        raise serializers.ValidationError("First installment already paid")
                except Subscription.DoesNotExist:
                    pass
        else:
            if installment_number:
                raise serializers.ValidationError("This plan is not paid in installment")

        if subscription is None:
            # About to create a brand-new Subscription row (full-pay, or a
            # fresh installment-1 start). A user may only have one
            # open (pending/partial/active) subscription at a time - once a
            # subscription hits Expired/Expired Partial/Failed it no longer
            # blocks a restart.
            has_open_subscription = Subscription.objects.filter(
                user=user, status__in=Subscription.OPEN_STATUSES
            ).exists()
            if has_open_subscription:
                raise serializers.ValidationError(
                    "This user already has an active or pending subscription. "
                    "It must expire or be completed before starting a new one."
                )

        attrs['installment_number'] = installment_number
        attrs['user'] = user
        attrs['plan'] = plan
        attrs['subscription'] = subscription
        return attrs

class NonMemberSubscriptionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    plan_id = serializers.UUIDField(required=True)
    is_admin_assigned = serializers.BooleanField(default=False)
    email = serializers.EmailField(required=True)
    hours = serializers.IntegerField(required=True, min_value=1)

    def validate(self, attrs):
        plan_id = attrs.get('plan_id')
        plan = None
        try:
            plan = Plans.objects.get(id=plan_id)
        except Plans.DoesNotExist:
            raise serializers.ValidationError("Plan does not exist")
        if plan.is_member_only:
            raise serializers.ValidationError("This plan is only for members")
        attrs['plan'] = plan
        attrs['phone_number'] = normalize_phone_number(attrs.get('phone_number'))
        return attrs

    def create(self, validated_data):
        plan = validated_data.get('plan')
        email = validated_data.get('email')
        admin_assigned = validated_data.get('is_admin_assigned')
        user_name = validated_data.get('name')
        phone_number = validated_data.get('phone_number')
        hours = validated_data.get('hours')
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={'user_name': user_name, 'phone_number': phone_number, 'is_member': False})

        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            admin_assigned=admin_assigned,
            hours=hours,
        )
        return subscription

class SubscriptionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'admin_assigned', 'status', 'expires_at', 'partial_expires_at', 'hours', 'created_at', 'updated_at']
