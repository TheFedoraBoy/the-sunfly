from django.utils import timezone

from .models import SiteSettings


def site(request):
    return {"site": SiteSettings.load(), "today": timezone.localdate()}
