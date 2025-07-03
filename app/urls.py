from django.urls import path
from .views import (
    home,
    features,
    contact_us,
    create_profile,
    select_resume,
    GenerateResume,
    resume_section,
    resume_section_education,
    resume_section_experience,
    resume_section_skills,
    resume_preview
    # download_resume  # New view for resume downloads
)

urlpatterns = [
    # Core pages
    path('', home, name='home'),
    path('features/', features, name='features'),
    path('contact/', contact_us, name='contact_us'),  # Changed to shorter URL
    
    # Resume generation flow
    path('profile/create/', create_profile, name='create_profile'),  # More RESTful URL
    path('resume/select-resume/', select_resume, name='select_resume'),
    path('resume/generate-resume/<str:action>', GenerateResume, name='GenerateResume'),
    path('resume/section/', resume_section, name='resume_section'),
    path('resume/section/education/<str:resume_id>', resume_section_education, name='resume_section_education'),
    path('resume/section/experiance/<str:resume_id>', resume_section_experience, name='resume_section_experience'),
    path('resume/section/skills/<str:resume_id>', resume_section_skills, name='resume_section_skills'),
    path('resume/section/resume_preview/<str:resume_id>', resume_preview, name='resume_preview'),
    # path('resume/download/<int:resume_id>/', download_resume, name='download_resume'),  # New endpoint
    
]