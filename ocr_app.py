import os
import re
from io import BytesIO

import streamlit as st
import pytesseract
import pymupdf
from PIL import Image
from dotenv import load_dotenv

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)


# ============================================================
# CONFIGURATION
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\anuma\AppData\Local\Tesseract-OCR\tesseract.exe"
)

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📄 AI Resume Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Analyze your resume against a job description 🚀</div>',
    unsafe_allow_html=True
)


# ============================================================
# COMMON TECHNICAL SKILLS
# ============================================================

SKILL_DATABASE = [
    "python",
    "java",
    "c++",
    "c",
    "javascript",
    "typescript",
    "html",
    "css",
    "sql",
    "mysql",
    "mongodb",
    "postgresql",
    "oracle",
    "react",
    "node.js",
    "nodejs",
    "express",
    "django",
    "flask",
    "git",
    "github",
    "linux",
    "windows",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "machine learning",
    "artificial intelligence",
    "ai",
    "data analysis",
    "data analytics",
    "pandas",
    "numpy",
    "matplotlib",
    "power bi",
    "tableau",
    "excel",
    "data structures",
    "algorithms",
    "dsa",
    "oop",
    "oops",
    "object oriented programming",
    "dbms",
    "operating systems",
    "computer networks",
    "cybersecurity",
    "network security",
    "ethical hacking",
    "cloud computing",
    "rest api",
    "api",
    "problem solving",
    "communication",
    "teamwork",
    "leadership",
    "debugging",
    "testing",
]


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text_from_pdf(file_bytes):

    text = ""

    try:

        pdf = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        for page in pdf:

            page_text = page.get_text()

            if page_text:
                text += page_text + "\n"

        pdf.close()

    except Exception as error:

        st.warning(
            f"PDF text extraction issue: {error}"
        )

    # OCR fallback for scanned PDFs

    if len(text.strip()) < 100:

        st.info(
            "🔍 This looks like a scanned PDF. Using OCR..."
        )

        try:

            pdf = pymupdf.open(
                stream=file_bytes,
                filetype="pdf"
            )

            ocr_text = ""

            for page in pdf:

                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(1.5, 1.5)
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                ocr_text += (
                    pytesseract.image_to_string(image)
                    + "\n"
                )

            pdf.close()

            text = ocr_text

        except Exception as error:

            st.error(
                f"❌ OCR failed: {error}"
            )

    return text


# ============================================================
# IMAGE EXTRACTION
# ============================================================

def extract_text_from_image(file_bytes):

    try:

        image = Image.open(
            BytesIO(file_bytes)
        )

        return pytesseract.image_to_string(
            image
        )

    except Exception as error:

        st.error(
            f"❌ Image OCR failed: {error}"
        )

        return ""


# ============================================================
# FIND SKILLS
# ============================================================

def find_skills(text):

    text_lower = text.lower()

    found = []

    for skill in SKILL_DATABASE:

        if skill.lower() in text_lower:

            if skill not in found:
                found.append(skill)

    return found


# ============================================================
# LOCAL RESUME ANALYSIS
# ============================================================

def local_resume_analysis(
    resume_text,
    job_description
):

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    # --------------------------------------------------------
    # Skills in resume
    # --------------------------------------------------------

    resume_skills = find_skills(
        resume_text
    )

    # --------------------------------------------------------
    # Skills in job description
    # --------------------------------------------------------

    job_skills = find_skills(
        job_description
    )

    # --------------------------------------------------------
    # Matching skills
    # --------------------------------------------------------

    matching_skills = []

    for skill in job_skills:

        if skill.lower() in resume_lower:

            matching_skills.append(skill)

    # --------------------------------------------------------
    # Skills to develop
    # --------------------------------------------------------

    skills_to_develop = []

    for skill in job_skills:

        if skill.lower() not in resume_lower:

            skills_to_develop.append(skill)

    # --------------------------------------------------------
    # Match score
    # --------------------------------------------------------

    if len(job_skills) > 0:

        score = int(
            (len(matching_skills) / len(job_skills))
            * 100
        )

    else:

        # Basic keyword comparison if no known
        # technical skills were detected.

        job_words = set(
            re.findall(
                r"[a-zA-Z]{4,}",
                job_lower
            )
        )

        resume_words = set(
            re.findall(
                r"[a-zA-Z]{4,}",
                resume_lower
            )
        )

        common_words = job_words.intersection(
            resume_words
        )

        if len(job_words) > 0:

            score = int(
                min(
                    100,
                    (len(common_words) / len(job_words))
                    * 100
                )
            )

        else:

            score = 0

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if score >= 75:

        summary = (
            "The resume shows a strong alignment with "
            "the provided job description. The candidate "
            "has several relevant skills and should "
            "highlight these strengths during applications "
            "and interviews."
        )

    elif score >= 50:

        summary = (
            "The resume shows a moderate match with "
            "the job description. The candidate has "
            "some relevant skills but can improve the "
            "match by developing the missing skills."
        )

    else:

        summary = (
            "The resume currently has a limited match "
            "with the job description. The candidate "
            "should focus on developing the missing "
            "technical skills and improving the resume "
            "to better target this role."
        )

    # --------------------------------------------------------
    # Suggestions
    # --------------------------------------------------------

    suggestions = []

    if skills_to_develop:

        suggestions.append(
            "Develop the missing skills: "
            + ", ".join(skills_to_develop[:8])
            + "."
        )

    if matching_skills:

        suggestions.append(
            "Highlight these matching skills clearly "
            "in the resume: "
            + ", ".join(matching_skills[:8])
            + "."
        )

    suggestions.append(
        "Add measurable achievements and project "
        "details wherever possible."
    )

    suggestions.append(
        "Keep the resume concise, professional, "
        "and relevant to the target job."
    )

    suggestions_text = "\n".join(
        "• " + item
        for item in suggestions
    )

    # --------------------------------------------------------
    # Interview preparation
    # --------------------------------------------------------

    interview_questions = [
        "Tell me about yourself.",
        "Explain your main academic or personal project.",
        "What are your strongest technical skills?",
        "Explain a problem you solved while developing a project.",
        "What is the difference between your strongest programming languages?",
        "How do you debug a program?",
        "Why are you interested in this role?",
    ]

    if job_skills:

        interview_questions.append(
            "Be prepared for technical questions about: "
            + ", ".join(job_skills[:8])
            + "."
        )

    interview_text = "\n".join(
        "• " + question
        for question in interview_questions
    )

    # --------------------------------------------------------
    # Detailed analysis
    # --------------------------------------------------------

    detailed_analysis = (
        f"The resume contains {len(resume_skills)} "
        f"identified skills. The job description contains "
        f"{len(job_skills)} recognized skills. "
        f"{len(matching_skills)} skills match between "
        f"the resume and the job description."
    )

    if skills_to_develop:

        detailed_analysis += (
            " The main development areas are: "
            + ", ".join(skills_to_develop[:10])
            + "."
        )

    else:

        detailed_analysis += (
            " No major missing skills were identified "
            "from the recognized skill list."
        )

    return {
        "score": score,
        "summary": summary,
        "skills": resume_skills,
        "matching_skills": matching_skills,
        "skills_to_develop": skills_to_develop,
        "suggestions": suggestions_text,
        "interview": interview_text,
        "detailed": detailed_analysis
    }


# ============================================================
# PDF REPORT
# ============================================================

def create_pdf_report(
    score,
    summary,
    skills,
    matching_skills,
    skills_to_develop,
    suggestions,
    interview,
    detailed
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14
    )

    story = []

    story.append(
        Paragraph(
            "AI Resume Analysis Report",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Resume Match Score: {score}%</b>",
            normal_style
        )
    )

    story.append(Spacer(1, 15))

    # Summary

    story.append(
        Paragraph(
            "Resume Summary",
            heading_style
        )

    )

    story.append(
        Paragraph(
            summary,
            normal_style
        )
    )

    # Skills

    story.append(
        Paragraph(
            "Skills Identified",
            heading_style
        )
    )

    for skill in skills:

        story.append(
            Paragraph(
                f"• {skill}",
                normal_style
            )
        )

    # Matching

    story.append(
        Paragraph(
            "Matching Skills",
            heading_style
        )
    )

    for skill in matching_skills:

        story.append(
            Paragraph(
                f"• {skill}",
                normal_style
            )
        )

    # Development

    story.append(
        Paragraph(
            "Skills to Develop",
            heading_style
        )
    )

    for skill in skills_to_develop:

        story.append(
            Paragraph(
                f"• {skill}",
                normal_style
            )
        )

    # Suggestions

    story.append(
        Paragraph(
            "Improvement Suggestions",
            heading_style
        )
    )

    for line in suggestions.split("\n"):

        story.append(
            Paragraph(
                line,
                normal_style
            )
        )

    # Interview

    story.append(
        Paragraph(
            "Interview Preparation",
            heading_style
        )
    )

    for line in interview.split("\n"):

        story.append(
            Paragraph(
                line,
                normal_style
            )
        )

    # Detailed

    story.append(
        Paragraph(
            "Detailed Analysis",
            heading_style
        )
    )

    story.append(
        Paragraph(
            detailed,
            normal_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📤 Upload your Resume",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg"
    ]
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

job_description = st.text_area(
    "💼 Paste the Job Description",
    height=180,
    placeholder="Paste the job description here..."
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze_button = st.button(
    "🤖 Analyze Resume",
    use_container_width=True
)


# ============================================================
# MAIN ANALYSIS
# ============================================================

if analyze_button:

    if uploaded_file is None:

        st.warning(
            "⚠️ Please upload your resume first."
        )

        st.stop()

    if not job_description.strip():

        st.warning(
            "⚠️ Please enter the job description."
        )

        st.stop()

    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    st.info(
        "📖 Reading your resume..."
    )

    file_bytes = uploaded_file.read()

    if uploaded_file.name.lower().endswith(".pdf"):

        resume_text = extract_text_from_pdf(
            file_bytes
        )

    else:

        resume_text = extract_text_from_image(
            file_bytes
        )

    if not resume_text.strip():

        st.error(
            "❌ Could not extract text from the resume."
        )

        st.stop()

    # --------------------------------------------------------
    # Local analysis
    # --------------------------------------------------------

    with st.spinner(
        "🔍 Analyzing your resume..."
    ):

        result = local_resume_analysis(
            resume_text,
            job_description
        )

    # --------------------------------------------------------
    # Get results
    # --------------------------------------------------------

    score = result["score"]
    summary = result["summary"]
    skills = result["skills"]
    matching_skills = result["matching_skills"]
    skills_to_develop = result["skills_to_develop"]
    suggestions = result["suggestions"]
    interview = result["interview"]
    detailed = result["detailed"]

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    st.success(
        "✅ Resume analysis completed!"
    )

    st.divider()

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    st.subheader(
        "🎯 Resume Match Score"
    )

    st.metric(
        "Job Match",
        f"{score}%"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    st.subheader(
        "📋 Resume Summary"
    )

    st.write(
        summary
    )

    # --------------------------------------------------------
    # Skills Dashboard
    # --------------------------------------------------------

    st.subheader(
        "🧠 Skills Dashboard"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Skills Identified",
            len(skills)
        )

    with col2:

        st.metric(
            "Matching Skills",
            len(matching_skills)
        )

    with col3:

        st.metric(
            "Skills to Develop",
            len(skills_to_develop)
        )

    # --------------------------------------------------------
    # Skill lists
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "✅ Matching Skills"
        )

        if matching_skills:

            for skill in matching_skills:

                st.success(
                    skill
                )

        else:

            st.write(
                "No matching skills identified."
            )

    with col2:

        st.subheader(
            "📚 Skills to Develop"
        )

        if skills_to_develop:

            for skill in skills_to_develop:

                st.warning(
                    skill
                )

        else:

            st.write(
                "No additional skills identified."
            )

    # --------------------------------------------------------
    # Chart
    # --------------------------------------------------------

    st.subheader(
        "📊 Skills Comparison"
    )

    chart_data = {
        "Matching Skills": len(matching_skills),
        "Skills to Develop": len(skills_to_develop)
    }

    st.bar_chart(
        chart_data
    )

    # --------------------------------------------------------
    # Suggestions
    # --------------------------------------------------------

    st.subheader(
        "💡 Improvement Suggestions"
    )

    st.write(
        suggestions
    )

    # --------------------------------------------------------
    # Interview
    # --------------------------------------------------------

    st.subheader(
        "🎤 Interview Preparation"
    )

    st.write(
        interview
    )

    # --------------------------------------------------------
    # Detailed analysis
    # --------------------------------------------------------

    st.subheader(
        "🔎 Detailed Analysis"
    )

    st.write(
        detailed
    )

    # --------------------------------------------------------
    # TXT REPORT
    # --------------------------------------------------------

    text_report = f"""
AI RESUME ANALYZER REPORT

MATCH SCORE: {score}%

RESUME SUMMARY
{summary}

SKILLS
{", ".join(skills)}

MATCHING SKILLS
{", ".join(matching_skills)}

SKILLS TO DEVELOP
{", ".join(skills_to_develop)}

IMPROVEMENT SUGGESTIONS
{suggestions}

INTERVIEW PREPARATION
{interview}

DETAILED ANALYSIS
{detailed}
"""

    st.subheader(
        "📥 Download Reports"
    )

    st.download_button(
        label="⬇️ Download TXT Report",
        data=text_report,
        file_name="resume_analysis.txt",
        mime="text/plain",
        use_container_width=True
    )

    # --------------------------------------------------------
    # PDF REPORT
    # --------------------------------------------------------

    pdf_file = create_pdf_report(
        score,
        summary,
        skills,
        matching_skills,
        skills_to_develop,
        suggestions,
        interview,
        detailed
    )

    st.download_button(
        label="⬇️ Download Professional PDF Report",
        data=pdf_file,
        file_name="AI_Resume_Analysis_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # --------------------------------------------------------
    # Resume text
    # --------------------------------------------------------

    with st.expander(
        "📄 View Extracted Resume Text"
    ):

        st.text(
            resume_text
        )