from django import forms
from django.core.exceptions import ValidationError
from .models import GeneratedResume

class PersonalDetailsForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    last_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    job_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = GeneratedResume
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'job_title', 
                 'city', 'country', 'pincode', 'linkdin_link', 'github_link', 'website_link']
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'linkdin_link': forms.URLInput(attrs={'class': 'form-control'}),
            'github_link': forms.URLInput(attrs={'class': 'form-control'}),
            'website_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'linkdin_link': 'LinkedIn Profile',
            'github_link': 'GitHub Profile',
            'website_link': 'Personal Website',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PersonalDetailsForm, self).__init__(*args, **kwargs)
        
        if user:
            # Prefill user details
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone_number'].initial = user.phone_number
            self.fields['job_title'].initial = user.job_title

class EducationForm(forms.ModelForm):
    class Meta:
        model = GeneratedResume
        fields = ['school_name', 'degree', 'field_of_study', 'graduation_date']
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ExperienceForm(forms.ModelForm):
    is_working_here = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = GeneratedResume
        fields = ['work_company_name', 'work_background_titel', 'work_start_date', 'work_end_date', 'work_job_description', 'is_working_here']
        widgets = {
            'work_company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'work_background_titel': forms.TextInput(attrs={'class': 'form-control'}),
            'work_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'work_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'work_job_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'work_background_titel': 'Job Title',
            'work_job_description': 'Job Description',
        }

class SkillsForm(forms.ModelForm):
    class Meta:
        model = GeneratedResume
        fields = ['skills', 'your_background']
        widgets = {
            'skills': forms.TextInput(attrs={'class': 'form-control'}),
            'your_background': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
        labels = {
            'your_background': 'Professional Summary',
        }