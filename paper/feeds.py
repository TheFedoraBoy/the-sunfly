from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Article


class LatestEssaysFeed(Feed):
    title = "The Sunfly"
    description = "One political essay a day."

    def link(self):
        return reverse("paper:home")

    def items(self):
        return Article.objects.published().select_related("author")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.dek

    def item_author_name(self, item):
        return item.author.name
