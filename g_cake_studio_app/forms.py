from django import forms
from .models import Review, Order


class ReviewForm(forms.ModelForm):
    """Класс формы отзыва"""

    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class OrderForm(forms.ModelForm):
    """Класс формы заказа"""

    class Meta:
        model = Order
        fields = ['name', 'phone', 'email', 'address', 'delivery_time', 'comments']
        widgets = {
            'delivery_time': forms.TextInput(attrs={'placeholder': 'Например, с 10:00 до 12:00'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
