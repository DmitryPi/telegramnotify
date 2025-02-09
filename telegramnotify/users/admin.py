from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from telegramnotify.users.forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("tg_id", "username", "password")}),
        (None, {"fields": ("name", "email")}),
        (_("Сервисы"), {"fields": ("services", "words")}),
        (_("Кошелек"), {"fields": ("pay_rate", "wallet")}),
        (_("Премиум"), {"fields": ("premium_status", "premium_expire")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "tg_id",
        "username",
        "name",
        "pay_rate",
        "wallet",
        "premium_status",
        "is_superuser",
    ]
    filter_horizontal = ("services",)
    search_fields = ["name"]
