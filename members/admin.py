from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import MemberRegisterForm, MemberEditForm
from .models import Member


class MemberAdmin(UserAdmin):
    add_form = MemberRegisterForm
    form = MemberEditForm
    model = Member
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password", "pfp")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions", "pfp"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(Member, MemberAdmin)