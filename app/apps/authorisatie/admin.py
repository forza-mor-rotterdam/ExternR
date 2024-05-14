from django.contrib import admin
from django.contrib.auth.models import Permission


class PermissionAdmin(admin.ModelAdmin):
    ...


admin.site.register(Permission, PermissionAdmin)
