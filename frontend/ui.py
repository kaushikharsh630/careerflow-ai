import streamlit as st
import requests
import time

# --- CONFIG ---
BASE_URL = "http://127.0.0.1:8000"
st.set_page_config(
    page_title="CareerFlow AI", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ADVANCED DARK MODE CSS ---
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* GLOBAL THEME VARIABLES (DARK MODE) */
    :root {
        --primary-color: #6366F1;   /* Neon Indigo */
        --secondary-color: #A855F7; /* Purple */
        --bg-color: #0F172A;        /* Deep Navy Blue (Background) */
        --card-bg: #1E293B;         /* Lighter Navy (Cards) */
        --text-color: #F8FAFC;      /* White Text */
        --accent-color: #10B981;    /* Green */
    }

    /* FORCE DARK BACKGROUND */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }

    /* HERO SECTION */
    .hero-container {
        background: linear-gradient(135deg, #4F46E5 0%, #9333EA 100%);
        padding: 4rem 2rem;
        border-radius: 0 0 2rem 2rem;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px -10px rgba(124, 58, 237, 0.5);
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.8;
        max-width: 600px;
        margin: 0 auto;
    }

    /* STEP CARDS */
    .step-card {
        background-color: var(--card-bg);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #334155; /* Subtle border */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    
    /* TEXT OVERRIDES FOR STREAMLIT WIDGETS */
    .stMarkdown, .stText, h1, h2, h3 {
        color: var(--text-color) !important;
    }
    
    /* SCORE CARD */
    .score-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: #1E293B;
        border-radius: 1rem;
        border: 1px solid #334155;
    }
    .big-score {
        font-size: 5rem;
        font-weight: 800;
        line-height: 1;
        background: -webkit-linear-gradient(45deg, #818CF8, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* CUSTOM BUTTONS */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #6366F1, #8B5CF6);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        border: none;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }

    /* TABS Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E293B;
        color: #94A3B8;
        border-radius: 8px 8px 0 0;
        border: 1px solid #334155;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366F1 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">⚡ CareerFlow AI</div>
    <div class="hero-subtitle">Optimize your resume, write cover letters, and master interviews.<br>Powered by Gemini 1.5 Flash.</div>
</div>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'analysis_data' not in st.session_state: st.session_state.analysis_data = None
if 'resume_text' not in st.session_state: st.session_state.resume_text = ""
if 'jd_text' not in st.session_state: st.session_state.jd_text = ""

# --- PROGRESS BAR ---
st.progress(st.session_state.step / 3)

# =========================================================
# STEP 1: INPUT
# =========================================================
if st.session_state.step == 1:
    col_spacer, col_main, col_spacer2 = st.columns([1, 4, 1])
    
    with col_main:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 📂 Upload Your Documents")
        st.info("We'll analyze your resume against the job description to find gaps.")
        
        uploaded_file = st.file_uploader("Drop your Resume (PDF/Docx)", type=["pdf", "docx"])
        jd_input = st.text_area("Paste Job Description", height=200, placeholder="Copy paste the JD here...")
        
        st.write("")
        if st.button("🚀 Analyze Match Score", type="primary"):
            if uploaded_file and jd_input:
                with st.status("🧠 Processing...", expanded=True):
                    files = {"resume_file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    data = {"job_description": jd_input}
                    
                    try:
                        res = requests.post(f"{BASE_URL}/analyze-match", files=files, data=data)
                        result = res.json()
                        st.session_state.analysis_data = result['analysis']
                        st.session_state.resume_text = result['extracted_resume_text']
                        st.session_state.jd_text = jd_input
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
            else:
                st.warning("⚠️ Please upload both files first!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# STEP 2: DASHBOARD
# =========================================================
elif st.session_state.step == 2:
    data = st.session_state.analysis_data
    score = data['match_score']
    
    c1, c2 = st.columns([1, 2], gap="large")
    
    with c1:
        st.markdown('<div class="step-card score-container">', unsafe_allow_html=True)
        st.markdown('<div style="color: #94A3B8;">ATS MATCH SCORE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="big-score">{score}</div>', unsafe_allow_html=True)
        
        if score > 75:
            st.success("🔥 Excellent Match!")
        elif score > 50:
            st.warning("⚠️ Good, but needs work.")
        else:
            st.error("🚨 Low Match.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.subheader("💡 Analysis")
        st.write(data['reasoning'])
        
        st.markdown("---")
        col_pro, col_con = st.columns(2)
        with col_pro:
            st.markdown("##### ✅ Strengths")
            for item in data['pros'][:3]: st.markdown(f"🟢 {item}")
        with col_con:
            st.markdown("##### 🚨 Gaps")
            for item in data['cons'][:3]: st.markdown(f"🔻 {item}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🛠️ Configure Application Kit")
    with st.form("config_form"):
        col_opts1, col_opts2, col_opts3 = st.columns(3)
        with col_opts1:
            tone_sel = st.selectbox("Writing Tone", ["Professional", "Confident", "Academic"])
        with col_opts2:
            q_count = st.number_input("Interview Qs", 3, 10, 5)
        with col_opts3:
            audio_opt = st.toggle("Generate Audio Coach", value=True)
            
        st.write("")
        if st.form_submit_button("✨ Generate Optimized Assets"):
            with st.spinner("Writing content..."):
                payload = {
                    "resume_text": st.session_state.resume_text,
                    "job_description": st.session_state.jd_text,
                    "tone": tone_sel,
                    "q_count": q_count,
                    "generate_audio": audio_opt
                }
                try:
                    gen_res = requests.post(f"{BASE_URL}/generate-kit", data=payload)
                    st.session_state.final_results = gen_res.json()
                    st.session_state.step = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# =========================================================
# STEP 3: RESULTS
# =========================================================
elif st.session_state.step == 3:
    st.balloons()
    res = st.session_state.final_results
    
    col_head, col_reset = st.columns([4, 1])
    with col_head: st.title("🎉 Your Kit is Ready!")
    with col_reset: 
        if st.button("🔄 Start New"):
            st.session_state.step = 1
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["📄 Resume Code", "✉️ Cover Letter", "🎧 Audio Coach"])
    
    with tab1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info("Copy into Overleaf.com")
        st.code(res['latex_resume'], language='latex')
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.text_area("Content", res['cover_letter_text'], height=400)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab3:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        if res.get('audio_path'):
            st.audio(f"{BASE_URL}/get-audio?filename=interview.mp3")
        st.text_area("Script", res['interview_qa'], height=300)
        st.markdown('</div>', unsafe_allow_html=True)