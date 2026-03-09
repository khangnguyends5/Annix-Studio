import streamlit as st
from groq import Groq
import requests

# Load API keys from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

groq_client = Groq(api_key=GROQ_API_KEY)

def generate_script(idea, platform, tone, language, duration, mode, creator_info):
    language_instruction = {
        "English": "Write in English",
        "Vietnamese": "Viết bằng tiếng Việt",
        "French": "Écrivez en français",
        "Spanish": "Escriba en español",
        "Mandarin": "用普通话写"
    }.get(language, "Write in English")

    depth = "Simple, fun, and fast. Anyone can follow this — even someone making their first ever video." if mode == "Quick" else """Professional level:
- Exact camera angles and movements
- Specific text overlay suggestions
- Music genre and tempo recommendation
- 3 alternative hook options
- Platform-specific engagement tips"""

    creator_context = f"\nCreator context: {creator_info}" if creator_info else ""

    prompt = f"""You are Annix Studio — the world's most creative AI video director.
Your mission: turn ANY idea from ANY person into a video that gets watched.
You make videos for grandmothers, students, business owners, and everyone.

{language_instruction}
{depth}
{creator_context}

Create a complete video script for:
- Idea: {idea}
- Platform: {platform}
- Tone: {tone}
- Duration: {duration}

Be creative, specific, and human. Not a template — a real video.

Structure:

🎣 HOOK (first 3 seconds — stop the scroll)
Visual: [exactly what appears]
Text on screen: [overlay text]
Voiceover: [exact words]

🎬 MAIN CONTENT
Visual: [exactly what appears]
Text on screen: [overlay text]
Voiceover: [exact words]

📣 CALL TO ACTION
Visual: [exactly what appears]
Text on screen: [overlay text]
Voiceover: [exact words]

🎵 MUSIC: [specific genre, tempo, mood]
💡 PRO TIP: [one tip to make this perform better on {platform}]"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_voiceover(script):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[{"role": "user", "content": f"Extract ONLY the spoken voiceover words from this script. No directions, no headers. Just the clean spoken text:\n\n{script}"}]
    )
    return response.choices[0].message.content

def generate_voiceover(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text[:2500],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    return None

# PAGE CONFIG
st.set_page_config(
    page_title="Annix Studio",
    page_icon="🎬",
    layout="wide"
)

# HERO
st.markdown("""
<div style='text-align:center; padding:40px 0 20px 0;'>
    <div style='display:flex; align-items:center; justify-content:center; gap:16px; margin-bottom:16px;'>
        <svg width="52" height="64" viewBox="0 0 90 110" fill="none">
            <line x1="45" y1="50" x2="18" y2="94" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="45" y1="50" x2="72" y2="94" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="12" y1="94" x2="24" y2="94" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="66" y1="94" x2="78" y2="94" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M45 50 L16 18 L24 28 L45 50 Z" fill="#FF6B35"/>
            <path d="M45 50 L74 18 L66 28 L45 50 Z" fill="#FF6B35"/>
            <path d="M45 50 L74 82 L66 72 L45 50 Z" fill="#FF6B35" opacity="0.75"/>
            <path d="M45 50 L16 82 L24 72 L45 50 Z" fill="#FF6B35" opacity="0.75"/>
            <path d="M16 18 L45 50 L13 12 Z" fill="#FF6B35"/>
            <path d="M74 18 L45 50 L77 12 Z" fill="#FF6B35"/>
            <path d="M74 82 L45 50 L77 88 Z" fill="#FF6B35" opacity="0.75"/>
            <path d="M16 82 L45 50 L13 88 Z" fill="#FF6B35" opacity="0.75"/>
            <circle cx="45" cy="50" r="4.5" fill="#FF6B35"/>
            <circle cx="45" cy="50" r="2" fill="#0a0a0a"/>
        </svg>
        <div>
            <div style='font-size:11px; color:#FF6B35; letter-spacing:4px; text-transform:uppercase;'>ANNIX</div>
            <div style='font-size:36px; font-weight:900; color:white; letter-spacing:-1px; line-height:1;'>STUDIO</div>
        </div>
    </div>
    <h1 style='font-size:3em; font-weight:900; color:white; margin:0 0 10px 0;'>Grandma's on TikTok.</h1>
    <p style='font-size:1.2em; color:#FF6B35; margin:0 0 6px 0;'>Turn any idea into a complete professional video.</p>
    <p style='font-size:0.95em; color:#666; margin:0;'>Script. Voiceover. Any language. Any platform. No skills needed.</p>
</div>
""", unsafe_allow_html=True)

# EXAMPLES
ex1, ex2, ex3, ex4 = st.columns(4)
with ex1: st.info("👵 Grandma's pho recipe on TikTok")
with ex2: st.info("🍜 Restaurant daily specials")
with ex3: st.info("🎓 Student history project")
with ex4: st.info("💼 Freelancer portfolio showcase")

st.markdown("---")

# INPUTS
st.markdown("### Tell Annix Studio what you want")
col1, col2 = st.columns(2)

with col1:
    idea = st.text_area("What is your video about?",
        placeholder="e.g. My grandmother teaching her secret pho recipe for the first time on camera...",
        height=120)
    creator_info = st.text_input("About you (optional — makes the script more personal)",
        placeholder="e.g. I am a 68 year old Vietnamese woman sharing family recipes")
    platform = st.selectbox("Platform", ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube", "LinkedIn", "Facebook"])

with col2:
    mode = st.selectbox("Mode", ["Quick — simple and fast", "Pro — detailed and professional"])
    mode = "Quick" if "Quick" in mode else "Pro"
    tone = st.selectbox("Tone", ["Fun and energetic", "Warm and personal", "Professional", "Emotional and inspiring", "Educational", "Funny and entertaining"])
    language = st.selectbox("Language", ["English", "Vietnamese", "French", "Spanish", "Mandarin"])
    duration = st.selectbox("Duration", ["15 seconds", "30 seconds", "60 seconds", "2 minutes", "5 minutes", "10 minutes"])

include_voiceover = st.checkbox("Generate voiceover audio", value=True)

st.markdown("---")

if st.button("🎬 Create My Video", type="primary", use_container_width=True):
    if idea:
        with st.spinner("Annix Studio is creating your script..."):
            script = generate_script(idea, platform, tone, language, duration, mode, creator_info)

        st.markdown("## 📝 Your Video Script")
        st.markdown(script)

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button("📄 Download Script", data=script,
                file_name="Annix_Studio_Script.txt", mime="text/plain", use_container_width=True)

        if include_voiceover:
            st.markdown("---")
            st.markdown("## 🎙️ Voiceover")
            with st.spinner("Recording voiceover..."):
                voiceover_text = extract_voiceover(script)
                st.markdown(f"*{voiceover_text}*")
                audio = generate_voiceover(voiceover_text)
                if audio:
                    st.audio(audio, format="audio/mp3")
                    with col_b:
                        st.download_button("🎙️ Download Voiceover", data=audio,
                            file_name="Annix_Studio_Voiceover.mp3", mime="audio/mpeg", use_container_width=True)

        st.markdown("---")
        st.markdown("<div style='text-align:center; color:#444; font-size:0.85em;'>Annix Studio — Part of the Annix Platform | annix.ai</div>", unsafe_allow_html=True)
    else:
        st.warning("Tell Annix Studio what your video is about first.")

st.markdown("---")
st.markdown("<div style='text-align:center; color:#333; font-size:0.8em;'>© 2026 Annix Platform. Created by Khang Nguyen.</div>", unsafe_allow_html=True)
