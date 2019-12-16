from django import forms

from .models import Product


class ProductForm(forms.ModelForm):

    # def clean_url(self):
    #     url = self.cleaned_data['url']

    class Meta:
        model = Product
        fields = (
            'title',
            'price',
            'currency',
            'url',
            'published_date',
        )
        widgets = {
            'title': forms.TextInput,
            'currency': forms.TextInput,
        }
