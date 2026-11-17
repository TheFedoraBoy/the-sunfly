from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article, Contributor


class ReaderPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.writer = Contributor.objects.create(name="Test Writer", title="Editor", bio="Bio.")
        today = timezone.localdate()
        cls.live = Article.objects.create(
            title="Live essay", body="Hello *world*.", author=cls.writer,
            publish_date=today, status=Article.Status.PUBLISHED)
        cls.old = Article.objects.create(
            title="Old essay", body="Older.", author=cls.writer,
            publish_date=today - timedelta(days=1), status=Article.Status.PUBLISHED)
        cls.draft = Article.objects.create(
            title="Draft essay", body="Not yet.", author=cls.writer, publish_date=today)
        cls.scheduled = Article.objects.create(
            title="Tomorrow essay", body="Soon.", author=cls.writer,
            publish_date=today + timedelta(days=1), status=Article.Status.PUBLISHED)

    def test_pages_load(self):
        for name in ("home", "archive", "contributors", "about", "feed", "healthz"):
            self.assertEqual(self.client.get(reverse(f"paper:{name}")).status_code, 200, name)
        self.assertEqual(self.client.get(self.writer.get_absolute_url()).status_code, 200)

    def test_home_leads_with_todays_essay(self):
        response = self.client.get(reverse("paper:home"))
        self.assertEqual(response.context["lead"], self.live)
        self.assertEqual(list(response.context["earlier"]), [self.old])

    def test_drafts_and_scheduled_essays_are_hidden_from_readers(self):
        for essay in (self.draft, self.scheduled):
            self.assertEqual(self.client.get(essay.get_absolute_url()).status_code, 404)
        archive = self.client.get(reverse("paper:archive")).content.decode()
        self.assertNotIn("Draft essay", archive)
        self.assertNotIn("Tomorrow essay", archive)

    def test_staff_can_preview_a_draft(self):
        user = get_user_model().objects.create_superuser("ed", password="pw-for-tests")
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 200)

    def test_markdown_renders(self):
        self.assertContains(self.client.get(self.live.get_absolute_url()), "<em>world</em>")

    def test_slugs_are_unique(self):
        twin = Article.objects.create(title="Live essay", body="x", author=self.writer)
        self.assertEqual(twin.slug, "live-essay-2")

    def test_empty_site_renders(self):
        Article.objects.all().delete()
        Contributor.objects.all().delete()
        for name in ("home", "archive", "contributors", "about"):
            self.assertEqual(self.client.get(reverse(f"paper:{name}")).status_code, 200, name)


class AvatarTests(TestCase):
    def test_avatar_replaces_photo_for_readers(self):
        person = Contributor.objects.create(name="Bug Person", avatar="moth", photo="contributors/x.jpg")
        html = self.client.get(person.get_absolute_url()).content.decode()
        self.assertIn("paper/avatars/moth", html)
        self.assertNotIn("contributors/x.jpg", html)

    def test_every_avatar_choice_has_a_file(self):
        from django.contrib.staticfiles import finders
        from .models import AVATAR_CHOICES
        for value, _label in AVATAR_CHOICES:
            if value:
                self.assertTrue(finders.find(f"paper/avatars/{value}.svg"), value)

    def test_admin_form_shows_picker(self):
        user = get_user_model().objects.create_superuser("ed2", password="pw-for-tests")
        self.client.force_login(user)
        html = self.client.get(reverse("admin:paper_contributor_add")).content.decode()
        self.assertIn("paper/avatars/ladybug.svg", html)
        self.assertIn('value="ladybug"', html)
