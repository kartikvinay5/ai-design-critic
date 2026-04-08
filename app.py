import streamlit as st
import time
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from image_analysis import basic_image_heuristics
import json
import base64

# --- Custom CSS for Premium UI ---
st.set_page_config(page_title="AI Design Critic", layout="wide", initial_sidebar_state="collapsed")

custom_css = """
<style>
/* Base Theme & Typography */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, p, span, div, label, button, input {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* App Background with Detail Grid */
.stApp {
    background-color: #09090B !important;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
    background-position: center top !important;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(24, 24, 27, 0.85);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 24px 48px -12px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.15);
}

/* Hero Title - Made 3x Bigger and extremely prominent */
.hero-title {
    font-size: 6rem !important;
    font-weight: 800 !important;
    color: #FAFAFA !important;
    margin-bottom: 1rem;
    letter-spacing: -0.05em;
    line-height: 1.1;
    text-shadow: 0 10px 30px rgba(0,0,0,0.8);
}
.hero-subtitle {
    font-size: 1.5rem !important;
    color: #A1A1AA !important;
    font-weight: 300 !important;
    margin-bottom: 3rem !important;
    max-width: 800px;
    line-height: 1.5;
}

/* Section Headers */
h2, h3 {
    font-weight: 600 !important;
    color: #FAFAFA !important;
    font-size: 1.5rem !important;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem !important;
}

/* Stats / Scores */
.score-badge {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: conic-gradient(#FAFAFA 0% var(--score), #27272A var(--score) 100%);
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.08);
}

.score-badge-inner {
    position: absolute;
    width: 120px;
    height: 120px;
    background: #18181B;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    font-weight: 700;
    color: #FAFAFA;
}

/* List Items / Feedback blocks */
.feedback-item {
    border-left: 4px solid #71717A;
    margin-bottom: 24px;
    background: rgba(250, 250, 250, 0.02);
    padding: 24px;
    border-radius: 0 12px 12px 0;
}

.feedback-title {
    font-weight: 600;
    color: #FAFAFA;
    font-size: 1.15rem;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.feedback-reason {
    font-size: 1.05rem;
    color: #A1A1AA;
    margin-bottom: 16px;
    line-height: 1.7;
}

.feedback-suggestion {
    font-size: 1.05rem;
    color: #FAFAFA;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.05);
    padding: 12px 16px;
    border-radius: 8px;
}

/* Upload Area specific override */
[data-testid="stFileUploadDropzone"] {
    background-color: rgba(39, 39, 42, 0.5) !important;
    border: 2px dashed rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #FAFAFA !important;
    background-color: rgba(63, 63, 70, 0.5) !important;
}

/* Color palettes */
.color-swatch-container {
    display: flex;
    gap: 12px;
    margin-top: 16px;
}
.color-swatch {
    width: 44px;
    height: 44px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def get_api_keys():
    keys = {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "").strip(),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "").strip()
    }
    if not keys["GEMINI_API_KEY"] and not keys["OPENAI_API_KEY"]:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        k, v = line.strip().split('=', 1)
                        if k in keys:
                            keys[k] = v.strip('"').strip("'").strip()
                            os.environ[k] = keys[k]
    return keys["GEMINI_API_KEY"], keys["OPENAI_API_KEY"]

def get_mock_response() -> dict: return { "overall_score": 78, "color_feedback": [{"issue": "Contrast ratio warnings", "reason": "The subtitle text uses a light gray against a white background, which fails WCAG AA guidelines.", "suggestion": "Darken the subtitle text to improve readability."}], "layout_feedback": [{"issue": "Overcrowded navigation", "reason": "The top navigation bar has too many elements.", "suggestion": "Move secondary links into a hidden dropdown."}], "accessibility_issues": [{"issue": "Button visibility", "reason": "The Cancel button is entirely text-based makes it hard to identify as interactive.", "suggestion": "Add a subtle background hover state."}], "ux_suggestions": [{"issue": "Call-to-action clarity", "reason": "The main CTA does not stand out.", "suggestion": "Increase the visual weight."}]}

def get_ai_feedback(image_bytes: bytes) -> dict:
    gemini_key, openai_key = get_api_keys()
    if not gemini_key and not openai_key: return get_mock_response()
    
    prompt = '''Analyze this UI design image and provide feedback in the following strict JSON format:
{
    "overall_score": 85,
    "color_feedback": [
        {"issue": "Low contrast", "reason": "Gray text on white background is hard to read.", "suggestion": "Darken the text to #333"}
    ],
    "layout_feedback": [
        {"issue": "Overcrowded header", "reason": "Too many icons in the top right.", "suggestion": "Move some actions to a dropdown menu."}
    ],
    "accessibility_issues": [
        {"issue": "Missing focus states", "reason": "Can't tell which element is selected.", "suggestion": "Add a visible focus ring."}
    ],
    "ux_suggestions": [
        {"issue": "Unclear primary action", "reason": "Both buttons have the same visual weight.", "suggestion": "Make the primary button a solid color."}
    ]
}
Be specific, practical, and actionable. Base your analysis on REAL layout laws and accessibility standards. ONLY RETURN THE RAW JSON OBJECT. No markdown code blocks, no other text.'''

    if gemini_key:
        import google.generativeai as genai
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content([prompt, Image.open(io.BytesIO(image_bytes))])
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")
            
    elif openai_key:
        from openai import OpenAI
        try:
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"}}] }],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")
    
    return get_mock_response()

# --- App Header Section ---
gemini_key, openai_key = get_api_keys()

if not gemini_key and not openai_key:
    st.error("⚠️ **System Admin Warning**: No API keys found in `.env`. The application is currently running in a static offline Demo Mode for visitors! Please add a `GEMINI_API_KEY` or `OPENAI_API_KEY` to the `.env` file to activate dynamic AI.")

hero_col1, hero_col2 = st.columns([3, 1])

with hero_col1:
    st.markdown("<div class='hero-title'>AI Design<br>Critic</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Upload your UI design and let AI analyze it for layout, accessibility, and UX improvements with formal precision.</div>", unsafe_allow_html=True)

with hero_col2:
    # Adding the generated abstract art sticker/detailing
    art_path = r"C:\\Users\\karti\\.gemini\\antigravity\\brain\\d9e2b9e2-752e-4652-955c-7880862c4366\\abstract_hero_art_1775661830890.png"
    if os.path.exists(art_path):
        st.image(art_path, use_container_width=True)

# --- File Uploader ---
uploaded_file = st.file_uploader("Drag and drop your UI design (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Read image
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Original Design</h3>", unsafe_allow_html=True)
        st.image(image, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        # We use a button to trigger analysis to give user control
        if st.button("Analyze Design", use_container_width=True, type="primary"):
            st.session_state.pop('analysis_done', None)
            with st.spinner("Analyzing design..."):
                try:
                    # 1. Run OpenCV deterministic heuristics
                    heuristics = basic_image_heuristics(image_bytes)
                    
                    # 2. Run LLM API analysis
                    ai_report = get_ai_feedback(image_bytes)
                    
                    st.session_state['analysis_done'] = True
                    st.session_state['heuristics'] = heuristics
                    st.session_state['ai_report'] = ai_report
                    st.rerun() # Refresh to show results below
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Quota" in error_msg:
                        st.warning("⏳ **AI Model Cooling Down**: You have hit the Free Tier limit of 5 requests per minute! Please grab a sip of water, wait about 30 seconds, and click Analyze again.")
                    else:
                        st.error(f"An error occurred during analysis: {error_msg}")
        else:
            if not st.session_state.get('analysis_done'):
                st.info("Ready to analyze. Click the button above when you're ready.")
                
        st.markdown("</div>", unsafe_allow_html=True)

# --- Results Area ---
if st.session_state.get('analysis_done'):
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 3rem 0;'>", unsafe_allow_html=True)
    
    heuristics = st.session_state['heuristics']
    ai_report = st.session_state['ai_report']
    score = ai_report.get('overall_score', 0)
    
    col_score, col_heuristics = st.columns([1, 2])
    
    with col_score:
        st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h3>Overall Score</h3>", unsafe_allow_html=True)
        # Using a conic gradient for a dynamic ring chart
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 30px 0;">
            <div class="score-badge" style="--score: {score}%;">
                <div class="score-badge-inner">{score}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_heuristics:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Extracted Properties (OpenCV)</h3>", unsafe_allow_html=True)
        
        # Display swatches for dominant colors
        colors = heuristics.get('dominant_colors', [])
        swatches_html = "".join([f"<div class='color-swatch' style='background-color: {c};' title='{c}'></div>" for c in colors])
        
        st.markdown(f"""
        <p><strong>Dimensions:</strong> {heuristics.get('dimensions')}</p>
        <p><strong>Theme Estimation:</strong> {heuristics.get('theme_estimation')}</p>
        <p><strong>Dominant Palette:</strong></p>
        <div class="color-swatch-container">{swatches_html}</div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Feedback Sections
    def render_feedback_section(title, items):
        if not items:
            return
        st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
        for item in items:
            st.markdown(f"""
            <div class="feedback-item">
                <div class="feedback-title">{item.get('issue', 'Issue')}</div>
                <div class="feedback-reason">{item.get('reason', '')}</div>
                <div class="feedback-suggestion">Suggestion: {item.get('suggestion', '')}</div>
            </div>
            """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_feedback_section("Color Feedback", ai_report.get('color_feedback', []))
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_feedback_section("Layout & Spacing", ai_report.get('layout_feedback', []))
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_feedback_section("Accessibility", ai_report.get('accessibility_issues', []))
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        render_feedback_section("UX Suggestions", ai_report.get('ux_suggestions', []))
        st.markdown("</div>", unsafe_allow_html=True)
