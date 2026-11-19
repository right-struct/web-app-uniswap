from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import ManagedUserForm
from .models import Item, UserProfile

class ManagedUserAdmin(UserAdmin):
    form = ManagedUserForm
    add_form = ManagedUserForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), ManagedUserAdmin)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'listing_type', 'owner', 'created_at', 'is_available')
    list_filter = ('category', 'listing_type', 'is_available')
    search_fields = ('title', 'description', 'contact')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at', 'updated_at')
    list_filter = ('role', 'user__is_active')
    search_fields = ('user__email', 'user__username', 'user__first_name', 'user__last_name')
