from django import forms
from .models import Profile , Post
from django_ckeditor_5.widgets import CKEditor5Widget
class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['name','bio']



class PostForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditor5Widget(config_name='default')
    )
    class Meta:
        model = Post
        fields = ['title', 'slug', 'description','tag', 'post_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'tag': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 5  # optional: shows 5 items at once
            }),
            'post_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }        