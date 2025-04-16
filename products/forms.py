from django import forms
from django.core.exceptions import ValidationError
from .models import Comment, Product, Variant

class ReplyForm(forms.ModelForm):
    """
    Admin comment reply form.
    """
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 50})

