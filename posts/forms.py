from django import forms
from .models import Category, Post
from django_ckeditor_5.widgets import CKEditor5Widget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'alias', 'description', 'kind', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category'}),
            'alias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter alias'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
            'kind': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price', 'id': 'id_price', 'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get('kind')
        price = cleaned_data.get('price')

        if kind == 'premium' and not price:
            self.add_error('price', 'Price is required for premium categories.')

        return cleaned_data

class CategoryEditForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'alias', 'description', 'kind', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category'}),
            'alias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter alias'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
            'kind': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price', 'id': 'id_price', 'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get('kind')
        price = cleaned_data.get('price')

        if kind == 'premium' and not price:
            self.add_error('price', 'Price is required for premium categories.')

        return cleaned_data
    
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'author', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title tag'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter summary'}),
            'body': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="comment"),
        }

class EditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title tag'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter summary'}),
            'body': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="comment"),
        }