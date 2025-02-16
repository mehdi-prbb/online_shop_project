from django import forms
from .models import Comment

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

