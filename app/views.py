from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponse
from .models import UserDetails, GeneratedResume
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
import json
from .utils import ResumeGenerator, generate_resume_pdf
import os
from django.conf import settings


def create_profile(request):
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['name', 'email', 'jobTitle', 'phone', 'password']
            if not all(request.POST.get(field) for field in required_fields):
                raise ValueError("All fields are required")
            
            # Split full name into first and last names
            full_name = request.POST['name'].strip()
            name_parts = full_name.split(' ')
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # Validate email format
            email = request.POST['email'].strip()
            if not '@' in email:
                raise ValidationError("Please enter a valid email address")
            
            # Create user with hashed password
            user = UserDetails.objects.create(
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=request.POST['phone'].strip(),
                password=make_password(request.POST['password']),  # Proper password hashing
                job_title=request.POST['jobTitle'].strip(),
                is_created=True
            )

            # Set session for logged-in user
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            messages.success(request, 'Profile created successfully! Proceed to build your resume.')
            return redirect('home')

        except IntegrityError:
            messages.error(request, 'This email is already registered. Please use a different email.')
            return redirect('create_profile')
            
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('create_profile')
            
        except Exception as e:
            messages.error(request, 'An error occurred while creating your profile. Please try again.')
            print(f"Error creating profile: {e}")
            return redirect('create_profile')

    return render(request, 'app/create_profile.html')

def home(request):
    user_id = request.session.get('user_id')
    user = UserDetails.objects.get(id=user_id)
    context = {"user": user}
    return render(request, 'app/index.html', context)

def features(request):
    return render(request, 'app/features.html')

def contact_us(request):
    return render(request, 'app/contact.html')  # Consider creating a separate contact page

@require_http_methods(["GET", "POST"])
def select_resume(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload':
            return redirect('GenerateResume', "upload")  # Make sure this URL name exists in urls.py
        elif action == 'form':
            return redirect('GenerateResume', 'form')  # Also ensure this URL name exists
        else:
            # Optional fallback for invalid action
            messages.error(request, 'Invalid option selected, Select atlest one option.')
            return redirect('select_resume')

    return render(request, 'app/select_resume.html')

def GenerateResume(request, action):
    show_form = False

    if action == 'upload':
        if request.method == 'POST':
            # Get the uploaded file from FILES, not POST
            uploaded_file = request.FILES.get('fileUpload')
            if uploaded_file:
                # Process the file here
                print(f"Uploaded file: {uploaded_file.name}")
                # TODO: Add your file processing logic
                messages.success(request, 'File uploaded successfully!')
                return redirect('home')  # Redirect to a success view
            else:
                messages.error(request, 'No file was uploaded')
                return redirect('GenerateResume', action='upload')
    
    elif action == 'form':
        # if request.method == 'POST':
        #     try:
        #         name = request.POST.get('name', '').strip()
        #         email = request.POST.get('email', '').strip()
        #         phone = request.POST.get('phone', '').strip()
        #         job_title = request.POST.get('job_title', '').strip()
        #         experience = request.POST.get('experiance', '').strip()
        #         github = request.POST.get('github', '').strip()
        #         portfolio = request.POST.get('portfolio', '').strip()
        #         prompt = request.POST.get('prompt', '').strip()

        #         # Validate required fields
        #         if not all([name, email, phone, job_title, experience]):
        #             messages.error(request, 'Please fill all required fields')
        #             return redirect('GenerateResume', action='form')

        #         # Print or process the received data
        #         print(f"Name: {name}")
        #         print(f"Email: {email}")
        #         print(f"Phone: {phone}")
        #         print(f"Job Title: {job_title}")
        #         print(f"Experience: {experience}")
        #         print(f"GitHub: {github or 'Not provided'}")
        #         print(f"Portfolio: {portfolio or 'Not provided'}")
        #         print(f"Prompt: {prompt or 'Not provided'}")

        #         # TODO: Call your AI resume generation logic here
        #         # For now, redirect to a success page
        #         messages.success(request, 'Resume generated successfully!')
        #         return redirect('home')  # Change to your actual success view

        #     except Exception as e:
        #         print("Error processing resume form:", e)
        #         messages.error(request, "Something went wrong. Please try again.")
        #         return redirect('GenerateResume', action='form')

        # # Show form for GET requests
        # show_form = True
        messages.info(request, 'Plese Fill all the Details Carefully to create perfect Resume.')
        return redirect('resume_section')
    else:
        return HttpResponse("Invalid action.", status=400)

    context = {
        'show_form': show_form,
        'user': request.user  # Make sure user is passed to template
    }
    return render(request, 'app/generate_resume.html', context)

def resume_section(request):
    # Check authentication
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login first')
        return redirect('create_profile')
    
    try:
        user = UserDetails.objects.get(id=user_id)
    except UserDetails.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('create_profile')

    # Handle form submission
    if request.method == 'POST':
        try:
            # Get and validate form data
            required_fields = {
                'name': request.POST.get('name', '').strip(),
                'email': request.POST.get('email', '').strip(),
                'phone': request.POST.get('phone', '').strip(),
                'job_title': request.POST.get('job_title', '').strip(),
                'experiance': request.POST.get('experiance', '').strip()
            }
            
            if not all(required_fields.values()):
                messages.error(request, 'Please fill all required fields')
                return redirect('resume_section')

            # Update user details
            user.full_name = required_fields['name']
            user.email = required_fields['email']
            user.phone_number = required_fields['phone']
            user.job_title = required_fields['job_title']
            user.save()

            # Get or create resume
            resume, created = GeneratedResume.objects.update_or_create(
                user=user,
                defaults={
                    'experiance': required_fields['experiance'],
                    'city': request.POST.get('city', '').strip(),
                    'country': request.POST.get('country', '').strip(),
                    'pincode': request.POST.get('pincode', '').strip(),
                    'linkdin_link': request.POST.get('linkdin', '').strip(),
                    'github_link': request.POST.get('github', '').strip(),
                    'website_link': request.POST.get('portfolio', '').strip(),
                    'your_background': request.POST.get('prompt', '').strip(),
                }
            )

            messages.success(request, 'Personal details saved successfully!')
            return redirect('resume_section_education', resume_id=resume.id)

        except Exception as e:
            messages.error(request, f'Error saving data: {str(e)}')
            return redirect('resume_section')

    # GET request - check for existing resume data
    try:
        resume = GeneratedResume.objects.get(user=user)
        initial_data = {
            'name': user.full_name,
            'email': user.email,
            'phone': user.phone_number,
            'job_title': user.job_title,
            'experiance': resume.experiance,
            'city': resume.city,
            'country': resume.country,
            'pincode': resume.pincode,
            'linkdin': resume.linkdin_link,
            'github': resume.github_link,
            'portfolio': resume.website_link,
            'prompt': resume.your_background
        }
    except GeneratedResume.DoesNotExist:
        initial_data = {
            'name': user.full_name,
            'email': user.email,
            'phone': user.phone_number,
            'job_title': user.job_title
        }

    return render(request, 'app/resume_section.html', {
        'user': user,
        'initial_data': initial_data
    })

def resume_section_education(request, resume_id):
    # Check authentication
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login first')
        return redirect('create_profile')
    
    resume = get_object_or_404(GeneratedResume, id=resume_id, user__id=user_id)

    if request.method == 'POST':
        try:
            # Validate education data
            required_fields = {
                'school': request.POST.get('school', '').strip(),
                'school_year': request.POST.get('school_year', '').strip(),
                'collage': request.POST.get('collage', '').strip(),
                'degree': request.POST.get('degree', '').strip(),
                'field': request.POST.get('field', '').strip(),
                'graduation': request.POST.get('graduation', '').strip()
            }

            if not all(required_fields.values()):
                messages.error(request, 'Please fill all required education fields')
                return redirect('resume_section_education', resume_id=resume_id)

            # Update education data
            resume.school_name = required_fields['school']
            resume.school_passing = required_fields['school_year']
            resume.collage_name = required_fields['collage']
            resume.degree = required_fields['degree']
            resume.field_of_study = required_fields['field']
            resume.graduation_date = request.POST.get('graduation')
            resume.save()

            messages.success(request, 'Education details saved successfully!')
            return redirect('resume_section_experience', resume_id=resume.id)

        except Exception as e:
            messages.error(request, f'Error saving education data: {str(e)}')
            return redirect('resume_section_education', resume_id=resume.id)

    # GET request - prepopulate form if data exists
    education_data = {
        'school_name': resume.school_name,
        'degree': resume.degree,
        'field_of_study': resume.field_of_study,
        'graduation_date': resume.graduation_date.strftime('%Y-%m-%d') if resume.graduation_date else ''
    }

    return render(request, 'app/education.html', {
        'resume_id': resume.id,
        'education_data': education_data
    })

def resume_section_experience(request, resume_id):
    # Check authentication
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login first')
        return redirect('create_profile')
    
    resume = get_object_or_404(GeneratedResume, id=resume_id, user__id=user_id)

    if request.method == 'POST':
        try:
            # Validate experience data
            required_fields = {
                'work_company_name': request.POST.get('work_company_name', '').strip(),
                'work_background_titel': request.POST.get('work_background_titel', '').strip(),
                'work_start_date': request.POST.get('work_start_date', '').strip()
            }
            
            if not all(required_fields.values()):
                messages.error(request, 'Please fill company name, job title and start date')
                return redirect('resume_section_experience', resume_id=resume.id)

            # Update experience data
            resume.work_company_name = required_fields['work_company_name']
            resume.work_background_title = required_fields['work_background_titel']
            resume.work_start_date = required_fields['work_start_date']
            resume.work_end_date = request.POST.get('work_end_date', '').strip()
            resume.work_job_description = request.POST.get('work_job_description', '').strip()
            resume.is_working_here = 'is_working_here' in request.POST
            resume.save()

            messages.success(request, 'Work experience saved successfully!')
            return redirect('resume_section_skills', resume_id=resume.id)

        except Exception as e:
            messages.error(request, f'Error saving experience: {str(e)}')
            return redirect('resume_section_experience', resume_id=resume.id)

    # GET request - prepopulate form
    experience_data = {
        'work_company_name': resume.work_company_name,
        'work_background_titel': resume.work_background_title,
        'work_start_date': resume.work_start_date.strftime('%Y-%m-%d') if resume.work_start_date else '',
        'work_end_date': resume.work_end_date.strftime('%Y-%m-%d') if resume.work_end_date else '',
        'work_job_description': resume.work_job_description,
        'is_working_here': resume.is_working_here
    }

    return render(request, 'app/experience.html', {
        'resume_id': resume.id,
        'experience_data': experience_data
    })

def resume_section_skills(request, resume_id):
    # Check authentication
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login first')
        return redirect('create_profile')
    
    resume = get_object_or_404(GeneratedResume, id=resume_id, user__id=user_id)

    if request.method == 'POST':
        try:
            # Validate skills data
            skills = request.POST.get('skills', '').strip()
            your_background = request.POST.get('your_background', '').strip()
            
            if not skills:
                messages.error(request, 'Please enter at least one skill')
                return redirect('resume_section_skills', resume_id=resume.id)

            # Update skills data (final step)
            resume.skills = skills
            resume.your_background = your_background
            resume.save()
            
            return redirect('resume_preview', resume_id=resume.id)

        except Exception as e:
            messages.error(request, f'Error generating resume: {str(e)}')
            return redirect('resume_section_skills', resume_id=resume.id)

    # GET request - prepopulate form
    skills_data = {
        'skills': resume.skills,
        'your_background': resume.your_background
    }

    return render(request, 'app/skills.html', {
        'resume_id': resume.id,
        'skills_data': skills_data
    })


def resume_preview(request, resume_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login first')
        return redirect('create_profile')

    try:
        resume = get_object_or_404(GeneratedResume, id=resume_id, user__id=user_id)

        # Safe skill parsing
        skills_input = resume.skills
        technical_skills = (
            skills_input if isinstance(skills_input, list)
            else [skill.strip() for skill in skills_input.split(',')] if skills_input else []
        )

        # Build resume data
        User_Resume_data = {
            "personal_info": {
                "name": resume.user.full_name,
                "email": resume.user.email,
                "phone": resume.user.phone_number,
                "job_title": resume.user.job_title,
                "location": f"{resume.city}, {resume.country}",
                "links": {
                    "linkedin": resume.linkdin_link,
                    "github": resume.github_link,
                    "portfolio": resume.website_link
                },
                "experience_years": resume.experiance
            },
            "education": [
                {
                    "institution": resume.school_name,
                    "degree": "High School",
                    "field_of_study": "",
                    "end_date": str(resume.school_passing) if resume.school_passing else None,
                    "achievements": []
                },
                {
                    "institution": resume.collage_name,
                    "degree": resume.degree,
                    "field_of_study": resume.field_of_study,
                    "end_date": str(resume.graduation_date) if resume.graduation_date else None,
                    "achievements": []
                }
            ],
            "experience": [
                {
                    "company": resume.work_company_name,
                    "position": resume.work_background_title,
                    "start_date": str(resume.work_start_date) if resume.work_start_date else None,
                    "end_date": str(resume.work_end_date) if resume.work_end_date else None,
                    "current": resume.is_working_here,
                    "description": resume.work_job_description
                }
            ],
            "skills": {
                "technical": technical_skills,
                "summary": resume.your_background
            }
        }

        # Call LLM and generate PDF
        OutPut_Data = ResumeGenerator(User_Resume_data, resume.user.full_name)
        pdf_path = generate_resume_pdf(OutPut_Data, resume.user.full_name)

        # Return media-safe URL
        relative_pdf_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
        pdf_url = f"{settings.MEDIA_URL}{relative_pdf_path}"
        print("PDF URL:", pdf_url)

        context = {
            'resume': resume,
            'resume_data': json.dumps(OutPut_Data, indent=2),
            'pdf_url': pdf_url
        }

        return render(request, 'app/resume_preview.html', context)

    except Exception as e:
        messages.error(request, f"Error generating resume: {str(e)}")
        return redirect('resume_section_skills', resume_id=resume_id)


