import json
import os

import pdfplumber
import streamlit as st
from dotenv import load_dotenv
from google import genai


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI CV Analyzer",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# Environment and Gemini client
# --------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key is missing. "
        "Add GEMINI_API_KEY to the .env file."
    )
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# PDF extraction
# --------------------------------------------------

def extract_text_from_pdf(pdf_file):
    extracted_pages = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_pages.append(page_text)

    return "\n\n".join(extracted_pages).strip()


# --------------------------------------------------
# Gemini CV analysis
# --------------------------------------------------

def analyze_cv_with_gemini(cv_text, job_description=""):
    job_context = (
        job_description.strip()
        if job_description.strip()
        else "No target job description was provided."
    )

    prompt = f"""
You are an expert ATS and CV analysis assistant.

Analyze the CV against the target job description when one is provided.
Return only valid JSON.
Do not use Markdown or code fences.

Use exactly this JSON structure:
{{
  "ats_score": 0,
  "detected_skills": [],
  "missing_skills": [],
  "strengths": [],
  "weaknesses": [],
  "improvement_suggestions": [],
  "professional_summary": ""
}}

Rules:
- ats_score must be an integer from 0 to 100.
- Keep every list concise and specific.
- Do not invent experience, education, certifications, or skills.
- If no job description is provided, evaluate general ATS readiness.
- Write the analysis in English.

TARGET JOB DESCRIPTION:
{job_context}

CV CONTENT:
{cv_text}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    raw_result = response.text.strip()

    if raw_result.startswith("```"):
        raw_result = raw_result.replace("```json", "", 1)
        raw_result = raw_result.replace("```", "").strip()

    analysis = json.loads(raw_result)

    analysis["ats_score"] = max(
        0,
        min(100, int(analysis.get("ats_score", 0))),
    )

    return analysis


# --------------------------------------------------
# Premium CSS
# --------------------------------------------------

st.markdown(
    """
<style>
#MainMenu,
footer,
header {
    visibility: hidden;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(91, 72, 255, 0.20),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 85%,
            rgba(0, 204, 255, 0.12),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #070a12 0%,
            #0b1020 50%,
            #080b14 100%
        );
    color: #f8fafc;
}

.block-container {
    max-width: 1550px;
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

h1,
h2,
h3,
p,
label {
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.premium-header {
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 24px;
    background: rgba(13, 18, 32, 0.78);
    box-shadow:
        0 24px 70px rgba(0, 0, 0, 0.32),
        inset 0 1px 0 rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(18px);
}

.brand-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.brand-group {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 58px;
    height: 58px;
    border-radius: 18px;
    font-size: 30px;
    background:
        linear-gradient(
            135deg,
            rgba(124, 92, 255, 1),
            rgba(31, 198, 255, 1)
        );
    box-shadow: 0 14px 35px rgba(91, 72, 255, 0.35);
}

.brand-title {
    margin: 0;
    font-size: 1.7rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #ffffff;
}

.brand-subtitle {
    margin: 0.25rem 0 0;
    color: #94a3b8;
    font-size: 0.94rem;
}

.status-pill {
    padding: 0.55rem 0.9rem;
    border: 1px solid rgba(74, 222, 128, 0.25);
    border-radius: 999px;
    color: #86efac;
    background: rgba(34, 197, 94, 0.10);
    font-size: 0.82rem;
    font-weight: 700;
    white-space: nowrap;
}

div[data-testid="stFileUploader"] {
    padding: 0.7rem;
    border: 1px dashed rgba(129, 140, 248, 0.55);
    border-radius: 18px;
    background: rgba(15, 23, 42, 0.62);
}

div[data-baseweb="textarea"] textarea,
div[data-baseweb="input"] input {
    color: #f8fafc;
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.72);
}

div.stButton > button {
    min-height: 3.1rem;
    border: 0;
    border-radius: 14px;
    color: white;
    font-weight: 800;
    background:
        linear-gradient(
            90deg,
            #7357ff 0%,
            #4776ff 48%,
            #20bff3 100%
        );
    box-shadow: 0 14px 30px rgba(71, 118, 255, 0.28);
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 38px rgba(71, 118, 255, 0.36);
}

div[data-testid="stMetric"] {
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.50);
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .brand-row {
        align-items: flex-start;
        flex-direction: column;
    }

    .status-pill {
        margin-left: 74px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Premium header
# --------------------------------------------------

st.markdown(
    """
<div class="premium-header">
<div class="brand-row">
<div class="brand-group">
<div class="brand-icon">👔</div>
<div>
<h1 class="brand-title">AI CV Analyzer</h1>
<p class="brand-subtitle">
Intelligent ATS analysis powered by AI
</p>
</div>
</div>
<div class="status-pill">● AI Engine Ready</div>
</div>
</div>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Main layout
# --------------------------------------------------

left_panel, right_panel = st.columns(
    [0.9, 1.1],
    gap="large",
)


# --------------------------------------------------
# Left panel
# --------------------------------------------------

with left_panel:
    st.markdown("### 📄 CV Analysis Studio")

    st.caption(
        "Upload your CV and optionally add a job description "
        "for a more accurate ATS analysis."
    )

    uploaded_cv = st.file_uploader(
        "Upload your CV",
        type=["pdf"],
        help="Only PDF files are supported.",
    )

    job_description = st.text_area(
        "Target Job Description",
        placeholder=(
            "Paste the job description here to detect matching "
            "and missing skills..."
        ),
        height=140,
    )

    analyze_button = st.button(
        "✨ Analyze My CV",
        use_container_width=True,
        type="primary",
    )

    if analyze_button:
        if uploaded_cv is None:
            st.warning(
                "Please upload your CV before starting the analysis.",
                icon="⚠️",
            )

        else:
            try:
                cv_text = extract_text_from_pdf(uploaded_cv)

            except Exception as error:
                st.error(
                    f"Unable to read the PDF: {error}",
                    icon="❌",
                )

            else:
                if not cv_text:
                    st.error(
                        "No readable text was found in this PDF. "
                        "The CV may be scanned or image-based.",
                        icon="📄",
                    )

                else:
                    st.session_state["cv_text"] = cv_text

                    try:
                        with st.spinner(
                            "AI is analyzing your CV..."
                        ):
                            analysis_result = (
                                analyze_cv_with_gemini(
                                    cv_text,
                                    job_description,
                                )
                            )

                    except json.JSONDecodeError:
                        st.error(
                            "Gemini returned an invalid analysis format. "
                            "Please try again.",
                            icon="❌",
                        )

                    except Exception as error:
                        st.error(
                            f"Unable to analyze the CV: {error}",
                            icon="❌",
                        )

                    else:
                        st.session_state[
                            "analysis_result"
                        ] = analysis_result

                        st.success(
                            "CV analyzed successfully.",
                            icon="✅",
                        )

                        st.caption(
                            f"Successfully extracted "
                            f"{len(cv_text):,} characters."
                        )


# --------------------------------------------------
# Right panel
# --------------------------------------------------

with right_panel:
    analysis_result = st.session_state.get(
        "analysis_result"
    )

    st.markdown("### 📊 Analysis Dashboard")

    st.caption(
        "Your ATS score and personalized insights "
        "will appear here."
    )

    if not analysis_result:
        st.info(
            "Upload a CV and click **Analyze My CV** "
            "to start the AI-powered assessment.",
            icon="💡",
        )

    metric_1, metric_2, metric_3 = st.columns(3)

    if analysis_result:
        ats_score = analysis_result.get(
            "ats_score",
            0,
        )

        detected_skills = analysis_result.get(
            "detected_skills",
            [],
        )

        missing_skills = analysis_result.get(
            "missing_skills",
            [],
        )

        with metric_1:
            st.metric(
                "ATS Score",
                f"{ats_score}/100",
            )

        with metric_2:
            st.metric(
                "Detected Skills",
                len(detected_skills),
            )

        with metric_3:
            st.metric(
                "Missing Skills",
                len(missing_skills),
            )

        st.markdown("---")

        professional_summary = analysis_result.get(
            "professional_summary",
            "",
        )

        if professional_summary:
            st.markdown("#### 🧠 Professional Summary")
            st.write(professional_summary)
            st.markdown("---")
        
        skills_left, skills_right = st.columns(2)

        with skills_left:
            st.markdown("#### ✅ Detected Skills")

            if detected_skills:
                for skill in detected_skills:
                    st.markdown(f"- {skill}")
            else:
                st.caption("No skills detected.")

        with skills_right:
            st.markdown("#### ⚠️ Missing Skills")

            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f"- {skill}")
            else:
                st.caption(
                    "No missing skills identified."
                )

            strengths = analysis_result.get(
                    "strengths",
                    [],
                )
        
            weaknesses = analysis_result.get(
                    "weaknesses",
                    [],
                )
        
            st.markdown("---")
        
            strengths_left, weaknesses_right = st.columns(2)
        
            with strengths_left:
                    st.markdown("#### 💪 Strengths")
        
                    if strengths:
                        for strength in strengths:
                            st.markdown(f"- {strength}")
                    else:
                        st.caption("No strengths identified.")
        
            with weaknesses_right:
                    st.markdown("#### 🔍 Weaknesses")
        
                    if weaknesses:
                        for weakness in weaknesses:
                            st.markdown(f"- {weakness}")
                    else:
                        st.caption("No weaknesses identified.")


        improvement_suggestions = analysis_result.get(
            "improvement_suggestions",
            [],
        )

        st.markdown("---")
        st.markdown("#### 🚀 Improvement Suggestions")

        if improvement_suggestions:
            for index, suggestion in enumerate(
                improvement_suggestions,
                start=1,
            ):
                st.markdown(
                    f"**{index}.** {suggestion}"
                )
        else:
            st.caption(
                "No improvement suggestions available."
            )
            
    else:
        with metric_1:
            st.metric("ATS Score", "--")

        with metric_2:
            st.metric("Detected Skills", "--")

        with metric_3:
            st.metric("Missing Skills", "--")


# --------------------------------------------------
# ATS disclaimer
# --------------------------------------------------

st.caption(
    "ATS scores are AI-generated guidance and do not represent "
    "an official employer ATS result."
)
