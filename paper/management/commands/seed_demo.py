from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from paper.models import Article, Contributor, SiteSettings

FILLER = """This is a placeholder essay so you can see how the page looks with real length. Delete it in the newsroom once you have published your own.

A longform essay needs room. The column is set narrow on purpose, about sixty-five characters wide, because that is the width at which the eye finds the start of the next line without effort. The first letter drops in orange, the way an old feature page would open.

## A section heading looks like this

Start a line with two pound signs to break an essay into sections. Leave a blank line between paragraphs. Wrap a phrase in single asterisks for *italics* and double asterisks for **bold**. Links are written as [the words you want linked](https://example.com).

> Start a line with a greater-than sign and it becomes a pull quote, set large with an orange bar beside it.

After the quote, the essay carries on as before. Three dashes on their own line make a dotted divider, which is handy before a closing thought.

---

Everything a reader sees here was typed into one text box in the newsroom. There is no layout work to do: write, choose the contributor, pick the date, and publish.
"""

PEOPLE = [
    ("Sample Writer One", "Editor", "A placeholder profile. Replace the name, title, photo and biography in the newsroom."),
    ("Sample Writer Two", "Contributing writer", "Another placeholder profile, here so the Contributors page has more than one card."),
    ("Sample Writer Three", "Columnist", "A third placeholder. Profiles without a photo show the Sunfly bug instead."),
]

TITLES = [
    ("A placeholder headline long enough to wrap onto two lines", "The subheading sits here in italics and says, in a sentence, what the essay argues."),
    ("Yesterday's sample essay", "Each day's essay moves into the sidebar and the archive when the next one is published."),
    ("An essay from two days ago", "Subheadings are optional."),
    ("Another sample from earlier in the week", ""),
    ("The oldest sample essay", "Delete all of these once the real ones exist."),
]


class Command(BaseCommand):
    help = "Fill an EMPTY local database with placeholder content. Refuses to run if essays exist."

    def handle(self, *args, **options):
        if Article.objects.exists() or Contributor.objects.exists():
            self.stderr.write("Content already exists; not adding placeholders.")
            return
        people = [Contributor.objects.create(name=n, title=t, bio=b, sort_order=i * 10)
                  for i, (n, t, b) in enumerate(PEOPLE, start=1)]
        today = timezone.localdate()
        for i, (title, dek) in enumerate(TITLES):
            Article.objects.create(title=title, dek=dek, body=FILLER, author=people[i % len(people)],
                                   publish_date=today - timedelta(days=i),
                                   status=Article.Status.PUBLISHED)
        site = SiteSettings.load()
        if not site.about:
            site.about = ("The Sunfly publishes one longform political essay a day.\n\n"
                          "This text is a placeholder. Edit it in the newsroom under Site settings.")
            site.save()
        self.stdout.write(self.style.SUCCESS("Added placeholder contributors and essays."))
