from django.contrib import admin

from check_in.models import CheckIn


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'start_time', 'end_time', 'expiry_date_time')
    search_fields = ('subscription__user__email', 'subscription__user__phone_number')
    raw_id_fields = ('subscription',)
