from django.contrib import admin
from django.utils.translation import gettext_lazy as _

SITE_DOMAIN = "TelegramNotify"


class CustomAdminSite(admin.AdminSite):
    site_header = SITE_DOMAIN
    site_title = _(f"Административный сайт {SITE_DOMAIN}")
