from apps.context.models import Context
from django.contrib import admin
from django.contrib.admin import AdminSite

AdminSite.site_title = "ExternR Admin"
AdminSite.site_header = "ExternR Admin"
AdminSite.index_title = "ExternR Admin"


class ContextAdmin(admin.ModelAdmin):
    ...


admin.site.register(Context, ContextAdmin)
