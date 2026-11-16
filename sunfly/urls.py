from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

admin.site.site_header = "The Sunfly newsroom"
admin.site.site_title = "The Sunfly newsroom"
admin.site.index_title = "Publish essays and manage contributors"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Uploaded images are served by Django itself. That is fine at this
    # site's scale; move to object storage (S3/R2) if traffic ever demands it.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("", include("paper.urls")),
]
