from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):
    default_site = "telegramnotify.contrib.admin.CustomAdminSite"
