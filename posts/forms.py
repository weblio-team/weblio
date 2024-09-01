from django import forms
from .models import Category, Post, Post
from django_ckeditor_5.widgets import CKEditor5Widget

# forms for categories views
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
    
# forms for authors views
class MyPostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'category', 'status', 'keywords']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title tag'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter summary'}),
            'body': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="comment"),
            'status': forms.HiddenInput(),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your tags'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(MyPostEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.status != 'draft':
            for field in self.fields.values():
                field.widget.attrs['disabled'] = 'disabled'
        
class ToEditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'category', 'author', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title tag'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter summary'}),
            'body': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="comment"),
            'author': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }

class MyPostAddForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'title_tag', 'summary', 'body', 'author', 'category', 'keywords']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'author': forms.HiddenInput(),
            'title_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title tag'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter summary'}),
            'body': CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="comment"),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your tags'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MyPostAddForm, self).__init__(*args, **kwargs)
        print(user)
        if user:
            self.fields['author'].initial = user

    def save(self, commit=True):
        instance = super(MyPostAddForm, self).save(commit=False)
        if self.initial.get('author'):
            instance.author = self.initial['author']
            print(instance.author)
        if commit:
            instance.save()
        return instance