import json
import os
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.conf import settings

API_KEY = "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"
# 'API_KEY HAS BEEN REMOVED DUE TO GITHUB ERROR.!, GET OUR OWN API_KEY FROM THE Groqe'

def ResumeGenerator(user_details, user_name):
    prompt = f"""
You are a professional AI resume writer trained in building clean, grammatically correct, ATS-optimized resumes.

Your task:
- Return **ONLY** valid **JSON**.
- Fix all grammar/spelling mistakes (e.g., "deploma" → "diploma").
- Ensure content looks professional, uses proper punctuation, and keeps tone formal.

Use **exactly** this format:
{{
  "personal_info": {{
    "name": "...",
    "email": "...",
    "phone": "...",
    "location": "...",
    "links": {{
      "linkedin": "...",
      "github": "...",
      "portfolio": "..."
    }}
  }},
  "summary": "...",
  "skills": {{
    "technical": ["...", "..."]
  }},
  "education": [
    {{
      "institution": "...",
      "degree": "...",
      "field_of_study": "...",
      "end_date": "YYYY-MM-DD"
    }}
  ],
  "experience": [
    {{
      "company": "...",
      "position": "...",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD or Present",
      "current": true/false,
      "description": [
        "Bullet-pointed achievements or responsibilities.",
        "Each starts with an action verb."
      ]
    }}
  ]
}}

### Instructions:
- Return only valid JSON. No markdown, no extra commentary.
- Use clean formatting, formal tone.
- Improve spelling, grammar, and professional clarity.

USER NAME:
{user_name}

USER DETAILS:
{json.dumps(user_details, indent=2)}
"""

    try:
        client = Groq(api_key=API_KEY)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except json.JSONDecodeError as decode_err:
        raise Exception(f"LLM returned non-JSON data:\n\n{content}\n\nError: {decode_err}")
    except Exception as e:
        raise Exception(f"LLM analysis error: {str(e)}")


def generate_resume_pdf(resume_data, user_name):
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(name='ResumeHeader', fontSize=20, leading=22, textColor=colors.HexColor("#1F2937"), spaceAfter=14))
    styles.add(ParagraphStyle(name='SubHeader', fontSize=14, leading=16, textColor=colors.HexColor("#2563EB"), spaceAfter=6))
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=12, leading=14, textColor=colors.HexColor("#374151"), spaceAfter=4, spaceBefore=8, underlineWidth=1))
    styles.add(ParagraphStyle(name='BulletText', fontSize=10, leading=12, leftIndent=12, bulletIndent=0))

    story = []

    # Header: Name & Title
    pi = resume_data.get("personal_info", {})
    story.append(Paragraph(pi.get("name", ""), styles['ResumeHeader']))
    story.append(Paragraph(pi.get("job_title", ""), styles['SubHeader']))

    contact_line = f"{pi.get('email', '')} | {pi.get('phone', '')} | {pi.get('location', '')}"
    story.append(Paragraph(contact_line, styles['Normal']))

    links = pi.get("links", {})
    if links:
        links_str = " | ".join(f"{k.title()}: {v}" for k, v in links.items() if v)
        story.append(Paragraph(links_str, styles['Normal']))

    story.append(Spacer(1, 0.2 * inch))

    # Summary
    if resume_data.get("summary"):
        story.append(Paragraph("Professional Summary", styles['SectionTitle']))
        story.append(Paragraph(resume_data['summary'], styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

    # Skills
    skills = resume_data.get("skills", {})
    if skills:
        story.append(Paragraph("Skills", styles['SectionTitle']))
        for category, items in skills.items():
            if items:
                story.append(Paragraph(f"<b>{category.title()}</b>: {', '.join(items)}", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

    # Experience
    experience = resume_data.get("experience", [])
    if experience:
        story.append(Paragraph("Professional Experience", styles['SectionTitle']))
        for exp in experience:
            title = f"{exp.get('position', '')} at {exp.get('company', '')}"
            dates = f"{exp.get('start_date', '')} - {exp.get('end_date', '') or 'Present'}"
            story.append(Paragraph(f"<b>{title}</b> ({dates})", styles['Normal']))
            achievements = exp.get("achievements", [])
            for bullet in achievements:
                story.append(Paragraph(f"• {bullet}", styles['BulletText']))
            story.append(Spacer(1, 0.1 * inch))

    # Education
    education = resume_data.get("education", [])
    if education:
        story.append(Paragraph("Education", styles['SectionTitle']))
        for edu in education:
            title = f"{edu.get('degree', '')} in {edu.get('field_of_study', '')}"
            institution = f"{edu.get('institution', '')} ({edu.get('end_date', '')})"
            story.append(Paragraph(f"<b>{title}</b> - {institution}", styles['Normal']))
            for bullet in edu.get("achievements", []):
                story.append(Paragraph(f"• {bullet}", styles['BulletText']))
            story.append(Spacer(1, 0.1 * inch))

    # Certifications
    certifications = resume_data.get("certifications", [])
    if certifications:
        story.append(Paragraph("Certifications", styles['SectionTitle']))
        for cert in certifications:
            cert_line = f"{cert.get('name', '')} - {cert.get('issuer', '')} ({cert.get('date', '')})"
            story.append(Paragraph(cert_line, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

    # Filename formatting
    safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_'))
    filename = f"{safe_name.replace(' ', '_')}_Resume.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # Create PDF
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    doc.build(story)

    return pdf_path
