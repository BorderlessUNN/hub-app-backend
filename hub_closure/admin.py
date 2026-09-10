from django.contrib import admin

from hub_closure.models import HubClosureDate


@admin.register(HubClosureDate)
class HubClosureDateAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason', 'is_processed')
    list_filter = ('is_processed',)
    ordering = ('-date',)
