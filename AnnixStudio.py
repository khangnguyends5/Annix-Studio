import streamlit as st
from groq import Groq
import requests
import time
import json

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
JSON2VIDEO_API_KEY = st.secrets["JSON2VIDEO_API_KEY"]

groq_client = Groq(api_key=GROQ_API_KEY)

def generate_script(idea, platform, tone, language, duration, mode, creator_info):
    language_instruction = {
        "English": "Write in English",
        "Vietnamese": "Viết bằng tiếng Việt",
        "French": "Écrivez en français",
        "Spanish": "Escriba en español",
        "Mandarin": "用普通话写"
    }.get(language, "Write in English")

    depth = "Simple, fun, and fast. Anyone can follow this." if mode == "Quick" else """Professional level:
- Exact camera angles
- Text overlay suggestions
- Music recommendation
- 3 alternative hooks
- Platform engagement tips"""

    creator_context = f"\nCreator: {creator_info}" if creator_info else ""

    prompt = f"""You are Annix Studio — creative AI video director.
{language_instruction}
{depth}
{creator_context}

Create complete video script:
- Idea: {idea}
- Platform: {platform}
- Tone: {tone}
- Duration: {duration}

Structure:
🎣 HOOK (3 seconds)
Visual: [what appears]
Text on screen: [overlay]
Voiceover: [exact words]

🎬 MAIN CONTENT
Visual: [what appears]
Text on screen: [overlay]
Voiceover: [exact words]

📣 CALL TO ACTION
Visual: [what appears]
Text on screen: [overlay]
Voiceover: [exact words]

🎵 MUSIC: [genre, tempo]
💡 PRO TIP: [one platform tip]"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_sections(script):
    prompt = f"""Extract from this script and return ONLY valid JSON no markdown:
{{
  "hook_text": "hook overlay text max 8 words",
  "main_text": "main content overlay text max 10 words",
  "cta_text": "call to action text max 8 words",
  "voiceover": "all spoken words clean and in order"
}}
Script: {script}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {
            "hook_text": "Watch this",
            "main_text": "Amazing content inside",
            "cta_text": "Try free link in bio",
            "voiceover": "Check out Annix Studio for free."
        }

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

def generate_video(hook_text, main_text, cta_text, platform):
    if platform in ["TikTok", "Instagram Reels", "YouTube Shorts"]:
        resolution = "portrait-hd"
        width, height = 720, 1280
    else:
        resolution = "full-hd"
        width, height = 1280, 720

    movie = {
    "comment": "Annix Studio generated video",
    "resolution": resolution,
    "quality": "high",
    "scenes": [
        {
            "comment": "Hook",
            "duration": 3,
            "transition": {"style": "fade", "duration": 0.5},
            "background-color": "#FF6B35",
            "elements": [
                {
                    "type": "text",
                    "text": hook_text,
                    "x": "center",
                    "y": "center",
                    "width": "80%",
                    "style": {
                        "fontFamily": "Montserrat",
                        "fontSize": 72,
                        "color": "#FFFFFF",
                        "fontWeight": "700",
                        "textAlign": "center"
                    }
                }
            ]
        },
        {
            "comment": "Main",
            "duration": 5,
            "transition": {"style": "slide-left", "duration": 0.5},
            "background-color": "#1A1A2E",
            "elements": [
                {
                    "type": "text",
                    "text": main_text,
                    "x": "center",
                    "y": "center",
                    "width": "80%",
                    "style": {
                        "fontFamily": "Montserrat",
                        "fontSize": 60,
                        "color": "#FFFFFF",
                        "fontWeight": "700",
                        "textAlign": "center"
                    }
                }
            ]
        },
        {
            "comment": "CTA",
            "duration": 3,
            "transition": {"style": "fade", "duration": 0.5},
            "background-color": "#0a0a0a",
            "elements": [
                {
                    "type": "text",
                    "text": cta_text,
                    "x": "center",
                    "y": "center",
                    "width": "80%",
                    "style": {
                        "fontFamily": "Montserrat",
                        "fontSize": 64,
                        "color": "#FF6B35",
                        "fontWeight": "700",
                        "textAlign": "center"
                    }
                }
            ]
        }
    ]
}

    headers = {
        "x-api-key": JSON2VIDEO_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.json2video.com/v2/movies",
        headers=headers,
        json=movie
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("project")
    return None

def check_video_status(project_id):
    headers = {"x-api-key": JSON2VIDEO_API_KEY}
    response = requests.get(
        f"https://api.json2video.com/v2/movies?project={project_id}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return None

# UI
st.set_page_config(page_title="Annix Studio", page_icon="🎬", layout="wide")

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
    <p style='font-size:0.95em; color:#666; margin:0;'>Script. Voiceover. Video. Any language. Any platform. Free forever.</p>
</div>
""", unsafe_allow_html=True)

ex1, ex2, ex3, ex4 = st.columns(4)
with ex1: st.info("👵 Grandma's pho recipe on TikTok")
with ex2: st.info("🍜 Restaurant daily specials")
with ex3: st.info("🎓 Student history project")
with ex4: st.info("💼 Freelancer portfolio showcase")

st.markdown("---")
st.markdown("### Tell Annix Studio what you want")

col1, col2 = st.columns(2)
with col1:
    idea = st.text_area("What is your video about?",
        placeholder="e.g. My grandmother teaching her secret pho recipe...",
        height=120)
    creator_info = st.text_input("About you (optional)",
        placeholder="e.g. I am a 68 year old Vietnamese woman sharing recipes")
    platform = st.selectbox("Platform", ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube", "LinkedIn", "Facebook"])

with col2:
    mode = st.selectbox("Mode", ["Quick — simple and fast", "Pro — detailed and professional"])
    mode = "Quick" if "Quick" in mode else "Pro"
    tone = st.selectbox("Tone", ["Fun and energetic", "Warm and personal", "Professional", "Emotional and inspiring", "Educational", "Funny and entertaining"])
    language = st.selectbox("Language", ["English", "Vietnamese", "French", "Spanish", "Mandarin"])
    duration = st.selectbox("Duration", ["15 seconds", "30 seconds", "60 seconds", "2 minutes", "5 minutes", "10 minutes"])

st.markdown("---")
col3, col4, col5 = st.columns(3)
with col3: include_voiceover = st.checkbox("Generate voiceover", value=True)
with col4: include_video = st.checkbox("Generate video", value=True)
with col5: st.caption("Powered by JSON2Video")

st.markdown("---")

if st.button("🎬 Create My Video", type="primary", use_container_width=True):
    if idea:
        with st.spinner("Writing your script..."):
            script = generate_script(idea, platform, tone, language, duration, mode, creator_info)

        st.markdown("## 📝 Your Video Script")
        st.markdown(script)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.download_button("📄 Download Script", data=script,
                file_name="Annix_Script.txt", mime="text/plain", use_container_width=True)

        sections = extract_sections(script)

        if include_voiceover:
            st.markdown("---")
            st.markdown("## 🎙️ Voiceover")
            with st.spinner("Recording voiceover..."):
                voiceover_text = sections.get("voiceover", "")
                st.markdown(f"*{voiceover_text}*")
                audio = generate_voiceover(voiceover_text)
                if audio:
                    st.audio(audio, format="audio/mp3")
                    with col_b:
                        st.download_button("🎙️ Download Voiceover", data=audio,
                            file_name="Annix_Voiceover.mp3", mime="audio/mpeg", use_container_width=True)

        if include_video:
            st.markdown("---")
            st.markdown("## 🎥 Your Video")
            with st.spinner("Generating video... takes about 60 seconds..."):
                project_id = generate_video(
                    sections.get("hook_text", "Watch this"),
                    sections.get("main_text", "Amazing content"),
                    sections.get("cta_text", "Try free link in bio"),
                    platform
                )

                if project_id:
                    progress = st.progress(0)
                    for i in range(30):
                        time.sleep(4)
                        progress.progress((i + 1) / 30)
                        status = check_video_status(project_id)
                        if status:
                            movie = status.get("movie", {})
                            if movie.get("status") == "done":
                                video_url = movie.get("url")
                                if video_url:
                                    progress.progress(100)
                                    st.success("Your video is ready!")
                                    st.video(video_url)
                                    with col_c:
                                        st.markdown(f"[⬇️ Download Video]({video_url})")
                                break
                            elif movie.get("status") == "error":
                                st.error("Video generation failed. Please try again.")
                                break
                else:
                    st.error("Could not start video generation. Check your JSON2Video API key in secrets.")

        st.markdown("---")
        st.markdown("<div style='text-align:center; color:#444; font-size:0.85em;'>Annix Studio — Free forever. Part of the Annix Platform. Built by Khang Nguyen</div>", unsafe_allow_html=True)
    else:
        st.warning("Tell Annix Studio what your video is about first.")

st.markdown("---")
st.markdown("<div style='text-align:center; color:#333; font-size:0.8em;'>© 2026 Annix Platform. Free for everyone. Forever.</div>", unsafe_allow_html=True)
