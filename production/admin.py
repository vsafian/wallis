from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from production.models import Worker, Workplace, Order, Material, Printer, PrintQueue


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        'phone_number', 'workplace'
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Work info", {
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
            "Personal info", {
            'fields': ('first_name', 'last_name')
            }
        ),
        (
            "Contacts", {
            'fields': ('phone_number', )
            }
        ),
        (
            "Work info", {
                'fields': ('workplace', )
            }
        )
    )

admin.site.register(Workplace)
admin.site.register(Material)
admin.site.register(Printer)
admin.site.register(PrintQueue)
admin.site.register(Order)
