from rest_framework import serializers
from check_in.models import CheckIn
from accounts.models import CustomUser
from django.utils import timezone
from subscription.models import Subscription

class CheckInSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
    
        subscription = None
        if user.is_member:
            subscription = Subscription.objects.filter(user=user, status=Subscription.SubscriptionStatus.ACTIVE).first()
            
            if not subscription:
                raise serializers.ValidationError("User does not have an active subscription")

            already_checked_in = CheckIn.objects.filter(subscription=subscription,created_at__date = timezone.now().date()).first()
            if already_checked_in:
                raise serializers.ValidationError("User is already checked in")

        elif not user.is_member:
            subscription = Subscription.objects.filter(user=user, status=Subscription.SubscriptionStatus.ACTIVE).first() 
            print(subscription)
            if not subscription:
                raise serializers.ValidationError("User does not have an active subscription")
            
            already_checked_in = CheckIn.objects.filter(subscription=subscription,).first()
            if already_checked_in:
                raise serializers.ValidationError("This pass as already being used")
        
        attrs['user'] = user
        attrs['subscription'] = subscription
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        subscription = validated_data.get('subscription')
        if user.is_member:
            checkin = CheckIn.objects.create(
                subscription=subscription,
                start_time=timezone.now(),
            )
        elif not user.is_member:
            subscription.status = Subscription.SubscriptionStatus.ACTIVE
            subscription.expires_at = timezone.now() + timezone.timedelta(hours=subscription.plan.hours)
            subscription.save()
            checkin = CheckIn.objects.create(
                subscription=subscription,
                start_time=timezone.now(),
                expiry_date_time=subscription.expires_at
                )
        
        return checkin

class NonMemberCheckOutSerializer(serializers.Serializer):
    checkin_id = serializers.UUIDField()

    def validate(self, attrs):
        checkin_id = attrs.get('checkin_id')
        check_in = None
        try:
            check_in = CheckIn.objects.get(id=checkin_id)
        except CheckIn.DoesNotExist:
            raise serializers.ValidationError("Invalid check-in id")

        if check_in.subscription.user.is_member:
            raise serializers.ValidationError("Member cannot be checked out")

        if check_in.subscription.status == Subscription.SubscriptionStatus.EXPIRED:
            raise serializers.ValidationError("Session has already been checked out and expired.")

        attrs['check_in'] = check_in
        return attrs

    def create(self,validated_data):
        check_in = validated_data.get('check_in')
        subscription = check_in.subscription
        subscription.status = Subscription.SubscriptionStatus.EXPIRED
        subscription.save()
        check_in.end_time = timezone.now()
        check_in.save()
        return check_in

   
class CheckInResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = ['id', 'subscription', 'start_time', 'end_time', 'expiry_date_time']