from django.conf import settings

def google_settings(request):
    # Expose the Google Client ID to templates
    return {"GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID}