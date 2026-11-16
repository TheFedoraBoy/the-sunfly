from django.urls import path

from . import views
from .feeds import LatestEssaysFeed

app_name = "paper"

urlpatterns = [
    path("", views.home, name="home"),
    path("archive/", views.archive, name="archive"),
    path("essays/<slug:slug>/", views.article, name="article"),
    path("contributors/", views.contributors, name="contributors"),
    path("contributors/<slug:slug>/", views.contributor, name="contributor"),
    path("about/", views.about, name="about"),
    path("healthz/", views.healthz, name="healthz"),
    path("feed/", LatestEssaysFeed(), name="feed"),
]
