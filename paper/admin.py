from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from .models import Article, Contributor, SiteSettings


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "title", "essay_count", "sort_order", "is_active")
    list_display_links = ("thumb", "name")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "title", "bio")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("photo_preview",)
    fields = ("name", "title", "photo", "photo_preview", "bio", "slug", "sort_order", "is_active")

    @admin.display(description="")
    def thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:50%">',
                obj.photo.url)
        return ""

    @admin.display(description="Current photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" alt="" style="width:160px;height:160px;object-fit:cover">', obj.photo.url)
        return "No photo yet. Readers see the Sunfly bug instead."

    @admin.display(description="Essays")
    def essay_count(self, obj):
        return obj.articles.count()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publish_date", "status", "live", "view_link")
    list_filter = ("status", "author")
    search_fields = ("title", "dek", "body")
    date_hierarchy = "publish_date"
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author",)
    save_on_top = True
    actions = ("publish_selected", "unpublish_selected")
    fieldsets = (
        (None, {"fields": ("title", "dek", "author", "body")}),
        ("Picture (optional)", {"fields": ("image", "image_caption")}),
        ("Publishing", {"fields": ("status", "publish_date", "slug")}),
    )

    @admin.display(boolean=True, description="Live now")
    def live(self, obj):
        return obj.is_live

    @admin.display(description="")
    def view_link(self, obj):
        label = "View" if obj.is_live else "Preview"
        return format_html('<a href="{}" target="_blank">{}</a>', obj.get_absolute_url(), label)

    @admin.action(description="Publish selected essays")
    def publish_selected(self, request, queryset):
        n = queryset.update(status=Article.Status.PUBLISHED)
        self.message_user(request, f"Published {n} essay(s).")

    @admin.action(description="Move selected essays back to draft")
    def unpublish_selected(self, request, queryset):
        n = queryset.update(status=Article.Status.DRAFT)
        self.message_user(request, f"Moved {n} essay(s) back to draft.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status != Article.Status.PUBLISHED:
            return
        clash = (Article.objects.filter(status=Article.Status.PUBLISHED,
                                        publish_date=obj.publish_date)
                 .exclude(pk=obj.pk).first())
        if clash:
            messages.warning(
                request,
                f'"{clash.title}" is also published for {obj.publish_date:%B} {obj.publish_date.day}. '
                "The home page shows only the most recently created of the two.")
        elif obj.publish_date > timezone.localdate():
            messages.info(
                request, f"Scheduled. This goes live on {obj.publish_date:%A, %B} {obj.publish_date.day}.")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # There is only one row, so skip the list and open it directly.
        from django.shortcuts import redirect
        obj = SiteSettings.load()
        return redirect("admin:paper_sitesettings_change", obj.pk)
