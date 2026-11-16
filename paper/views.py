from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Article, Contributor


def home(request):
    published = Article.objects.published().select_related("author")
    lead = published.first()
    earlier = published[1:6] if lead else []
    return render(request, "paper/home.html", {"lead": lead, "earlier": earlier})


def archive(request):
    published = Article.objects.published().select_related("author")
    page = Paginator(published, 30).get_page(request.GET.get("page"))
    return render(request, "paper/archive.html", {"page": page})


def article(request, slug):
    essay = get_object_or_404(Article.objects.select_related("author"), slug=slug)
    # Drafts and scheduled essays can be previewed by logged-in staff only.
    if not essay.is_live and not request.user.is_staff:
        raise Http404
    published = Article.objects.published()
    newer = published.filter(publish_date__gt=essay.publish_date).order_by("publish_date").first()
    older = published.filter(publish_date__lt=essay.publish_date).first()
    return render(request, "paper/article.html",
                  {"essay": essay, "newer": newer, "older": older})


def contributors(request):
    people = Contributor.objects.filter(is_active=True)
    return render(request, "paper/contributors.html", {"people": people})


def contributor(request, slug):
    person = get_object_or_404(Contributor, slug=slug)
    essays = Article.objects.published().filter(author=person)
    return render(request, "paper/contributor.html", {"person": person, "essays": essays})


def about(request):
    return render(request, "paper/about.html")


def healthz(request):
    """Used by Railway to confirm the app has started."""
    return HttpResponse("ok", content_type="text/plain")
