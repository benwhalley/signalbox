from django.conf import settings

def globals(request):
   return {
        'BRAND_NAME': settings.BRAND_NAME,
        'GOOGLE_TRACKING_ID': settings.GOOGLE_TRACKING_ID,
   }
