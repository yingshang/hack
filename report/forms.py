from django import forms

class search(forms.Form):
    key = forms.CharField(max_length=50)