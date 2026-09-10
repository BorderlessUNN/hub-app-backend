from django.contrib import admin

from payments.models import Plans, Payment


@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'hours', 'is_member_only', 'is_paid_in_installment', 'installment_price')
    list_filter = ('is_member_only', 'is_paid_in_installment')
    search_fields = ('name', 'slug')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_type', 'payment_status', 'installment_number', 'paystack_reference', 'created_at')
    list_filter = ('payment_type', 'payment_status', 'installment_number')
    search_fields = ('user__email', 'user__phone_number', 'paystack_reference')
    raw_id_fields = ('user', 'subscription')
