from django.contrib import admin
from twiliobox.models import TwilioNumber


class TwilioNumberAdmin(admin.ModelAdmin):
    list_editable = ['is_default_account']
    list_display = ['phone_number', 'is_default_account']
    save_on_top = True

admin.site.register(TwilioNumber,TwilioNumberAdmin)
