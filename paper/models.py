from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def unique_slug(instance, source, max_length=80):
    """Slugify `source`, adding -2, -3... if another row already uses it."""
    base = slugify(source)[:max_length] or "untitled"
    slug, n = base, 2
    Model = type(instance)
    while Model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f"-{n}"
        slug = base[: max_length - len(suffix)] + suffix
        n += 1
    return slug


class Contributor(models.Model):
    """A writer shown to readers. Not a login account."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=80, unique=True, blank=True,
                            help_text="Used in the web address. Leave blank to generate from the name.")
    title = models.CharField(max_length=160, blank=True,
                             help_text='Shown under the name, e.g. "Editor" or "Contributing writer".')
    photo = models.ImageField(upload_to="contributors/", blank=True,
                              help_text="A square photo works best. The site crops to a square either way.")
    bio = models.TextField(blank=True, help_text="Markdown is supported.")
    sort_order = models.PositiveIntegerField(
        default=100, help_text="Lower numbers appear first on the Contributors page.")
    is_active = models.BooleanField(
        default=True, help_text="Untick to hide from the Contributors page. Their essays stay up.")

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("paper:contributor", args=[self.slug])


class ArticleQuerySet(models.QuerySet):
    def published(self):
        """Published and not dated in the future."""
        return self.filter(status=Article.Status.PUBLISHED,
                           publish_date__lte=timezone.localdate())


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True, blank=True,
                            help_text="Used in the web address. Leave blank to generate from the headline.")
    dek = models.CharField("subheading", max_length=300, blank=True,
                           help_text="One or two sentences under the headline.")
    author = models.ForeignKey(Contributor, on_delete=models.PROTECT, related_name="articles")
    body = models.TextField(help_text="Markdown: blank line between paragraphs, ## for a section "
                                      "heading, > for a pull quote, *italic*, **bold**, [text](link).")
    image = models.ImageField(upload_to="articles/", blank=True,
                              help_text="Optional picture shown above the essay.")
    image_caption = models.CharField(max_length=300, blank=True)
    publish_date = models.DateField(
        default=timezone.localdate,
        help_text="The day this runs. A future date keeps a published essay hidden until then.")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT,
                              help_text="Drafts are visible only to you while logged in.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-publish_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("paper:article", args=[self.slug])

    @property
    def is_live(self):
        return (self.status == self.Status.PUBLISHED
                and self.publish_date <= timezone.localdate())

    @property
    def reading_minutes(self):
        return max(1, round(len(self.body.split()) / 230))


class SiteSettings(models.Model):
    """One row holding the text an editor may want to change without a deploy."""

    tagline = models.CharField(max_length=160, default="One political essay a day.")
    about = models.TextField(
        blank=True, help_text="The About page. Markdown is supported.")

    class Meta:
        verbose_name = "site settings"
        verbose_name_plural = "site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # only ever one row
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
