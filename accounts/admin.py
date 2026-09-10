from django.contrib import admin

from accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email', 'phone_number', 'is_member', 'is_superuser', 'admin_role', 'is_active')
    list_filter = ('is_member', 'is_superuser', 'admin_role', 'is_active')
    search_fields = ('user_name', 'email', 'phone_number')
    ordering = ('user_name',)
