from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from modelmasterapp.models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_custom_user_id',)

    def get_custom_user_id(self, obj):
        return obj.profile.custom_user_id if hasattr(obj, 'profile') else '-'
    get_custom_user_id.short_description = 'User ID'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
