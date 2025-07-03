from django.db import models
from django.contrib.auth.models import User

class UserDetails(models.Model): 
    full_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    is_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class GeneratedResume(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    experiance = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=7, null=True, blank=True)
    linkdin_link = models.CharField(max_length=300, null=True, blank=True)
    github_link = models.CharField(max_length=300, null=True, blank=True)
    website_link = models.CharField(max_length=300, null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    your_background = models.TextField(null=True, blank=True)

    school_name = models.CharField(max_length=100, null=True, blank=True)
    school_passing = models.DateField(null=True, blank=True)
    collage_name = models.CharField(max_length=100, null=True, blank=True)
    degree = models.CharField(max_length=100, null=True, blank=True)
    field_of_study = models.CharField(max_length=200, null=True, blank=True)
    graduation_date = models.DateField(null=True, blank=True)

    work_company_name = models.CharField(max_length=100, null=True, blank=True)
    work_background_title = models.CharField(max_length=200, null=True, blank=True)
    work_start_date = models.DateField(null=True, blank=True)
    work_end_date = models.DateField(null=True, blank=True)
    work_job_description = models.TextField(null=True, blank=True)
    is_working_here = models.BooleanField(default=False)

    skills = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.user.full_name}'s Resume ({self.user.job_title})"