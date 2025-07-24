import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import pandas as pd
import altair as alt

# -------------------- LOAD CSS --------------------
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styling.css")

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="Resume Application Tracker")
st.title("Resume Application Tracker")

# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type="pdf")

if uploaded_file:
    st.success("Resume uploaded successfully!")
    st.markdown(f"**File Name:** {uploaded_file.name}")

    # Correct sequence
    uploaded_file_bytes = uploaded_file.getvalue()
    doc = fitz.open(stream=uploaded_file_bytes, filetype="pdf")

    # NOW it's safe to use `doc`
    full_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        full_text += page.get_text().lower()


    # (Continue with the rest of your code here...)


    # -------------------- RESUME PREVIEW --------------------
    st.subheader("Resume Preview")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        st.image(img, caption=f"Page {page_num + 1}", use_container_width=True)

    # -------------------- TECH SKILLS DETECTION --------------------
    tech_keywords = ["python", "java", "c", "mysql", "html", "css", "javascript", "sql", "r", "excel"]
    skills_found = sum([1 for skill in tech_keywords if skill in full_text])

    # -------------------- SECTION-WISE CHART --------------------
    sections = [
        {"section": "Objective", "score": 10 if "career objective" in full_text or "objective" in full_text else 0},
        {"section": "Education", "score": 10 if "education" in full_text or "btech" in full_text else 0},
        {"section": "Experience", "score": 10 if "intern" in full_text or "experience" in full_text else 0},
        {"section": "Projects", "score": 10 if "project" in full_text else 0},
        {"section": "Skills", "score": 15 if skills_found >= 5 else (10 if 2 <= skills_found < 5 else 0)},
        {"section": "LinkedIn", "score": 10 if "linkedin.com/in" in full_text else 0},
        {"section": "Academics", "score": 10 if "%" in full_text or "cgpa" in full_text else 0},
        {"section": "Certifications", "score": 10 if "certification" in full_text or "certificate" in full_text else 0},
        {"section": "Contact Info", "score": 5 if "@" in full_text and any(num in full_text for num in "0123456789") else 0},
        {"section": "GitHub/Portfolio", "score": 10 if "github.com" in full_text else 0}
    ]

    df = pd.DataFrame(sections)

    # -------------------- SCORE + CHART --------------------
    total_score = sum([section["score"] for section in sections])

    st.subheader("Resume Score")
    st.markdown(f"**Score:** {total_score}/100")

    progress_color = "green" if total_score >= 70 else "orange" if total_score >= 50 else "red"
    progress_html = f"""
    <div style='background-color: #eee; border-radius: 10px; height: 30px; width: 100%; margin-bottom:10px'>
      <div style='width: {total_score}%; background-color: {progress_color}; height: 100%;
                  border-radius: 10px; text-align: center; color: white; font-weight: bold;'>
        {total_score}%
      </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

    st.subheader("Section-wise Resume Strength")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('section', sort='-y', title='Resume Section'),
        y=alt.Y('score', title='Score'),
        color=alt.Color('score', scale=alt.Scale(scheme='blues')),
        tooltip=['section', 'score']
    ).properties(width=700, height=400)

    st.altair_chart(chart, use_container_width=True)

    # -------------------- FEEDBACK --------------------
    st.subheader("Suggestions to Improve")
    feedback = []

    if "objective" not in full_text:
        feedback.append("- Career Objective section is missing.")
    if "education" not in full_text and "btech" not in full_text:
        feedback.append("- Education details are missing.")
    if "intern" not in full_text and "experience" not in full_text:
        feedback.append("- Work or internship experience not found.")
    if "project" not in full_text:
        feedback.append("- Project section is not mentioned.")
    if skills_found < 3:
        feedback.append("- Add more technical skills for better visibility.")
    if "linkedin.com/in" not in full_text:
        feedback.append("- Add a professional LinkedIn profile link.")
    if "%" not in full_text and "cgpa" not in full_text:
        feedback.append("- Academic scores are missing.")
    if "certification" not in full_text and "certificate" not in full_text:
        feedback.append("- Include at least one relevant certification.")
    if "@" not in full_text or not any(num in full_text for num in "0123456789"):
        feedback.append("- Contact details (email or phone) missing.")
    if "github.com" not in full_text:
        feedback.append("- Add your GitHub or portfolio link.")

    if feedback:
        for tip in feedback:
            st.markdown(
                f"<div style='color: white; background-color: #4a4a4a; padding: 10px; border-radius: 5px; margin-bottom: 8px;'>{tip}</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<div style='background-color: #198754; padding: 10px; color: white; border-radius: 5px;'>"
            " Your resume includes all essential sections."
            "</div>",
            unsafe_allow_html=True
        )
    # -------------------- DOWNLOAD BUTTON --------------------
    st.download_button(
        label="Download Resume PDF",
       data=uploaded_file_bytes,
        file_name="your_resume.pdf",
        mime="application/pdf",
        key="download_resume"
    )