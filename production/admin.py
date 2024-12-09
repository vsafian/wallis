from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from production.models import Worker, Workplace


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('phone_number', )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Work information", {
                "fields": ('workplace', )
            }

        ),

        (
            "Contacts", {
                'fields': ('phone_number', )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Personal Information", {
            'fields': ('first_name', 'last_name')
            }
        ),
        (
            "Contacts", {
            'fields': ('phone_number', )
            }
        ),
        (
            "Work information", {
                'fields': ('workplace', )
            }
        )
    )

admin.site.register(Workplace)