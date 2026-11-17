from django import forms


class AvatarPicker(forms.RadioSelect):
    """Radio buttons that show each bug avatar as a picture."""

    template_name = "paper/widgets/avatar_picker.html"
