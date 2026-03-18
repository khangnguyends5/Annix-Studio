import streamlit as st
from groq import Groq
import requests
import time
import json
import random

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
JSON2VIDEO_API_KEY = st.secrets["JSON2VIDEO_API_KEY"]
PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
ELEVENLABS_CONN_ID = st.secrets["JSON2VIDEO_ELEVENLABS_CONN_ID"]

groq_client = Groq(api_key=GROQ_API_KEY)

TRENDING_TOPICS = [
    "AI tools that will change your life in 2026",
    "5 side hustles you can start with zero money",
    "Morning routine that made me productive",
    "Things nobody tells you about starting a business",
    "How I learned a new skill in 7 days",
    "Vietnamese grandma cooking secrets revealed",
    "Why most people never achieve their goals",
    "Simple habits that compound over time",
    "How to make money while you sleep",
    "The truth about building wealth young"
]

def get_trending_ideas():
    return random.sample(TRENDING_TOPICS, 5)

def get_pexels_video(query, orientation="portrait"):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation={orientation}&size=medium"
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        if response.get("videos"):
            for video in response["videos"]:
                for vf in video["video_files"]:
                    if vf.get("width", 0) >= 720:
                        return vf["link"]
        return None
    except:
        return None

def generate_script(idea, platform, tone, language, duration, mode, creator_info):
    language_instruction = {
        "English": "Write in English",
        "Vietnamese": "Viết bằng tiếng Việt",
        "French": "Écrivez en français",
        "Spanish": "Escriba en español",
        "Mandarin": "用普通话写"
    }.get(language, "Write in English")

    depth = "Simple, fun, fast. First-time creator friendly." if mode == "Quick" else """Professional:
- Exact camera angles
- Text overlay suggestions
- Music recommendation
- 3 alternative hooks
- Platform engagement tips"""

    creator_context = f"\nCreator: {creator_info}" if creator_info else ""

    prompt = f"""You are Annix Studio — world's best AI video director.
{language_instruction}
{depth}
{creator_context}

Create complete viral video script:
- Idea: {idea}
- Platform: {platform}
- Tone: {tone}
- Duration: {duration}

Structure:
🎣 HOOK (3 seconds)
Visual: [what appears]
Text on screen: [overlay max 6 words]
Voiceover: [exact words]
Pexels search: [2-3 word query]

🎬 MAIN CONTENT
Visual: [what appears]
Text on screen: [overlay max 8 words]
Voiceover: [exact words]
Pexels search: [2-3 word query]

📣 CALL TO ACTION
Visual: [what appears]
Text on screen: [overlay max 6 words]
Voiceover: [exact words]
Pexels search: [2-3 word query]

🎵 MUSIC: [genre, tempo]
💡 PRO TIP: [one platform tip]"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_sections(script):
    prompt = f"""Extract from this script. Return ONLY valid JSON no markdown:
{{
  "hook_text": "hook overlay max 6 words",
  "main_text": "main overlay max 8 words",
  "cta_text": "cta overlay max 6 words",
  "hook_search": "2-3 word pexels search hook",
  "main_search": "2-3 word pexels search main",
  "cta_search": "2-3 word pexels search cta",
  "voiceover": "all spoken words clean in order"
}}
Script: {script}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {
            "hook_text": "Watch This",
            "main_text": "This changes everything",
            "cta_text": "Try free link in bio",
            "hook_search": "cinematic abstract",
            "main_search": "people success",
            "cta_search": "phone technology",
            "voiceover": "Check out Annix Studio for free."
        }

def generate_caption(topic, platform):
    prompt = f"""Create a viral {platform} caption for: {topic}
Include strong hook, 2-3 value sentences, call to action, 8-10 hashtags including #AnnixStudio #FreeAI
Return only the caption."""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def remix_script(original_script):
    prompt = f"""Rewrite this video script to be MORE viral, emotional, engaging, shareable.
Same topic. Better hook. More compelling content. More urgent CTA.
Original:
{original_script}
Return complete rewritten script in same format."""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_video_unified(sections, platform, voiceover_text):
    if platform in ["TikTok", "Instagram Reels", "YouTube Shorts"]:
        resolution = "portrait-hd"
        orientation = "portrait"
    else:
        resolution = "full-hd"
        orientation = "landscape"

    fallback = "https://videos.pexels.com/video-files/4459031/4459031-hd_720_1280_30fps.mp4"
    hook_video = get_pexels_video(sections.get("hook_search", "cinematic nature"), orientation) or fallback
    main_video = get_pexels_video(sections.get("main_search", "people success"), orientation) or fallback
    cta_video = get_pexels_video(sections.get("cta_search", "phone technology"), orientation) or fallback

    movie = {
        "comment": "Annix Studio — Free AI Video",
        "resolution": resolution,
        "quality": "high",
        "scenes": [
            {
                "comment": "Hook",
                "duration": 3,
                "elements": [
                    {
                        "type": "video",
                        "src": hook_video,
                        "duration": 3,
                        "volume": 0
                    },
                    {
                        "type": "text",
                        "style": "005",
                        "text": sections.get("hook_text", "Watch This"),
                        "duration": 3,
                        "settings": {
                            "color": "#FFFFFF",
                            "font-size": "72px",
                            "font-family": "Montserrat",
                            "font-weight": "900",
                            "text-align": "center"
                        }
                    },
                    {
                        "type": "text",
                        "style": "001",
                        "text": "Made with Annix Studio",
                        "y": "90%",
                        "duration": 3,
                        "settings": {
                            "color": "#FFFFFF",
                            "font-size": "22px",
                            "font-family": "Montserrat",
                            "opacity": "0.7",
                            "text-align": "center"
                        }
                    }
                ]
            },
            {
                "comment": "Main with voice",
                "duration": -1,
                "elements": [
                    {
                        "type": "video",
                        "src": main_video,
                        "duration": -2,
                        "volume": 0
                    },
                    {
                        "type": "voice",
                        "text": voiceover_text,
                        "connection": ELEVENLABS_CONN_ID,
                        "voice": "21m00Tcm4TlvDq8ikWAM",
                        "duration": -1,
                        "settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    },
                    {
                        "type": "text",
                        "style": "001",
                        "text": sections.get("main_text", ""),
                        "y": "15%",
                        "duration": -1,
                        "settings": {
                            "color": "#FF6B35",
                            "font-size": "52px",
                            "font-family": "Montserrat",
                            "font-weight": "700",
                            "text-align": "center"
                        }
                    },
                    {
                        "type": "text",
                        "style": "001",
                        "text": "Made with Annix Studio",
                        "y": "90%",
                        "duration": -1,
                        "settings": {
                            "color": "#FFFFFF",
                            "font-size": "22px",
                            "font-family": "Montserrat",
                            "opacity": "0.7",
                            "text-align": "center"
                        }
                    }
                ]
            },
            {
                "comment": "CTA",
                "duration": 3,
                "background-color": "#0a0a0a",
                "elements": [
                    {
                        "type": "video",
                        "src": cta_video,
                        "duration": 3,
                        "volume": 0,
                        "settings": {"opacity": "0.4"}
                    },
                    {
                        "type": "text",
                        "style": "005",
                        "text": sections.get("cta_text", "Try Free Now"),
                        "duration": 3,
                        "settings": {
                            "color": "#FF6B35",
                            "font-size": "68px",
                            "font-family": "Montserrat",
                            "font-weight": "900",
                            "text-align": "center"
                        }
                    },
                    {
                        "type": "text",
                        "style": "001",
                        "text": "Create yours free at Annix Studio",
                        "y": "75%",
                        "duration": 3,
                        "settings": {
                            "color": "#FFFFFF",
                            "font-size": "28px",
                            "font-family": "Montserrat",
                            "text-align": "center"
                        }
                    },
                    {
                        "type": "text",
                        "style": "001",
                        "text": "Made with Annix Studio",
                        "y": "90%",
                        "duration": 3,
                        "settings": {
                            "color": "#FFFFFF",
                            "font-size": "22px",
                            "font-family": "Montserrat",
                            "opacity": "0.7",
                            "text-align": "center"
                        }
                    }
                ]
            }
        ],
        "elements": [
            {
                "type": "subtitles",
                "settings": {
                    "style": "classic",
                    "font-family": "Montserrat",
                    "font-size": 60,
                    "position": "center-center",
                    "word-color": "#FFFFFF",
                    "line-color": "#FFFFFF",
                    "outline-color": "#000000",
                    "outline-width": 4,
                    "max-words-per-line": 3
                }
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
        return response.json().get("project")
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
    <p style='font-size:1.2em; color:#FF6B35; margin:0 0 6px 0;'>The fastest way to create viral videos. Free forever.</p>
    <p style='font-size:0.95em; color:#666; margin:0;'>Script. Voice. Real footage. Caption. Any language. Any platform.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🔥 Trending Ideas Today")
trending = get_trending_ideas()
cols = st.columns(5)
selected_trend = None
for i, trend in enumerate(trending):
    with cols[i]:
        if st.button(f"💡 {trend[:28]}...", key=f"trend_{i}", use_container_width=True):
            selected_trend = trend

st.markdown("---")

ex1, ex2, ex3, ex4 = st.columns(4)
with ex1: st.info("👵 Grandma's pho recipe")
with ex2: st.info("🍜 Restaurant specials")
with ex3: st.info("🎓 Student project")
with ex4: st.info("💼 Freelancer portfolio")

st.markdown("---")
st.markdown("### Tell Annix Studio what you want")

col1, col2 = st.columns(2)
with col1:
    default_idea = selected_trend if selected_trend else ""
    idea = st.text_area("What is your video about?",
        value=default_idea,
        placeholder="e.g. My grandmother teaching her secret pho recipe...",
        height=120)
    creator_info = st.text_input("About you (optional)",
        placeholder="e.g. Vietnamese woman sharing family recipes")
    platform = st.selectbox("Platform", ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube", "LinkedIn", "Facebook"])

with col2:
    mode = st.selectbox("Mode", ["Quick — simple and fast", "Pro — detailed and professional"])
    mode = "Quick" if "Quick" in mode else "Pro"
    tone = st.selectbox("Tone", ["Fun and energetic", "Warm and personal", "Professional", "Emotional and inspiring", "Educational", "Funny and entertaining"])
    language = st.selectbox("Language", ["English", "Vietnamese", "French", "Spanish", "Mandarin"])
    duration = st.selectbox("Duration", ["15 seconds", "30 seconds", "60 seconds", "2 minutes", "5 minutes"])

st.markdown("---")
col3, col4, col5 = st.columns(3)
with col3: include_video = st.checkbox("Generate video with real footage", value=True)
with col4: include_caption = st.checkbox("Generate viral caption", value=True)
with col5: st.caption("🎥 Pexels + ElevenLabs + JSON2Video")

st.markdown("---")

if st.button("🎬 Create My Viral Video", type="primary", use_container_width=True):
    if idea:
        with st.spinner("✍️ Writing your script..."):
            script = generate_script(idea, platform, tone, language, duration, mode, creator_info)

        st.markdown("## 📝 Your Video Script")
        st.markdown(script)

        sections = extract_sections(script)
        voiceover_text = sections.get("voiceover", "")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.download_button("📄 Download Script", data=script,
                file_name="Annix_Script.txt", mime="text/plain", use_container_width=True)

        if include_caption:
            st.markdown("---")
            st.markdown("## 📢 Your Viral Caption")
            with st.spinner("Generating viral caption..."):
                caption = generate_caption(idea, platform)
                st.text_area("Copy this caption:", value=caption, height=150)

        if include_video:
            st.markdown("---")
            st.markdown("## 🎥 Generating Your Video")
            st.caption("Real footage + voice + subtitles + watermark — all in one")

            with st.spinner("Fetching footage and generating video... 60-90 seconds..."):
                project_id = generate_video_unified(sections, platform, voiceover_text)

                if project_id:
                    progress = st.progress(0)
                    status_text = st.empty()
                    for i in range(36):
                        time.sleep(5)
                        progress.progress((i + 1) / 36)
                        status_text.caption(f"Rendering... {(i+1)*5}s")
                        status = check_video_status(project_id)
                        if status:
                            movie = status.get("movie", {})
                            if movie.get("status") == "done":
                                video_url = movie.get("url")
                                if video_url:
                                    progress.progress(100)
                                    status_text.empty()
                                    st.success("🎬 Your video is ready!")
                                    st.video(video_url)
                                    with col_b:
                                        st.markdown(f"[⬇️ Download Video]({video_url})")
                                    st.info("💡 Download and post on TikTok with your caption above. Tag @annix.studio!")
                                break
                            elif movie.get("status") == "error":
                                st.error("Video generation failed. Try again or uncheck video generation.")
                                break
                else:
                    st.error("Could not start video. Check your API keys in Streamlit secrets.")

        st.markdown("---")
        if st.button("🔁 Remix This Video — Make It More Viral", use_container_width=True):
            with st.spinner("Remixing for maximum virality..."):
                remixed = remix_script(script)
                st.markdown("## 🔁 Remixed Script")
                st.markdown(remixed)
                st.download_button("📄 Download Remixed Script", data=remixed,
                    file_name="Annix_Remixed_Script.txt", mime="text/plain")

        st.markdown("---")
        st.markdown("<div style='text-align:center; color:#444; font-size:0.85em;'>Annix Studio — Free forever. Part of the Annix Platform. Built by Khang Nguyen 🌪️</div>", unsafe_allow_html=True)
    else:
        st.warning("Tell Annix Studio what your video is about — or click a trending idea above.")

st.markdown("---")
st.markdown("<div style='text-align:center; color:#333; font-size:0.8em;'>© 2026 Annix Platform. Free for everyone. Forever. | @annix.studio</div>", unsafe_allow_html=True)
