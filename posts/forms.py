from django import forms
from .models import Category

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