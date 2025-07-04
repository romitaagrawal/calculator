from django import forms

class MyForm(forms.Form):
    my_post_param = forms.CharField(label='My POST Parameter', max_length=100)