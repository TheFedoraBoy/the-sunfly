import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdown(text):
    """Render Markdown to HTML.

    Only people with admin access can write this text, so it is trusted and
    not sanitised. If you ever accept text from the public, sanitise it.
    """
    html = md.markdown(text or "", extensions=["extra", "smarty", "sane_lists"])
    return mark_safe(html)
