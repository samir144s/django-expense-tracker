from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Expense, Category


class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense

        fields = [
            'title',
            'amount',
            'category',
            'date',
            'description'
        ]

        widgets = {

            'title': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Lunch'
                }
            ),

            'amount': forms.NumberInput(
                attrs={
                    'placeholder': 'e.g. 500',
                    'step': '0.01'
                }
            ),

            'date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Optional description',
                    'rows': 4
                }
            ),
        }