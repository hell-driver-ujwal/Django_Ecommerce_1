from django import forms 
from .models import Account, UserProfile
from django.forms import ValidationError

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class':'form-control'
    }))

    confirm_password = forms.CharField(widget = forms.PasswordInput(attrs={
            'placeholder':'Confirm Password',
            'class':'form-control'
        }))
    
    class Meta: 
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        self.confirm_password = cleaned_data.get('confirm_password')

        if password != self.confirm_password:
            raise forms.ValidationError(
                "The password doesnot match "
            )

class userForm(forms.ModelForm):
    class Meta:
        model = Account 
        fields = ['first_name', 'last_name', 'phone_number']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for field in self.fields.values():
                field.widget.attrs['class'] = 'form-control'

class userProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required= False, error_messages = {'invalid' : ("Images files only")}, widget = forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2' ,'profile_picture', 'city', 'state', 'country']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name == 'profile_picture':
                field.widget.attrs['class'] = 'form-control-file'
                field.widget.attrs['accept'] = 'image/*'
            else:
                field.widget.attrs['class'] = 'form-control'
