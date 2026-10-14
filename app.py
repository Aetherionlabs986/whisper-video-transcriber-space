"""
Whisper Video Transcriber & Audio Intelligence Workbench
Developed by Muhammed Hammad S (@hammad986) | Aetherion Labs
Live Streamlit App optimized for Hugging Face Spaces & Local Execution
"""

import os
import sys
import tempfile
import time
from pathlib import Path
import streamlit as st

# Configure Page
st.set_page_config(
    page_title="Whisper Video Transcriber | Aetherion Labs",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #A855F7, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .segment-box {
        background-color: #1E293B;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid #8B5CF6;
    }
    .time-badge {
        font-family: monospace;
        background-color: #334155;
        color: #38BDF8;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_whisper_model(model_size: str, device: str, compute_type: str):
    """Load and cache the Faster-Whisper model."""
    from faster_whisper import WhisperModel
    return WhisperModel(model_size, device=device, compute_type=compute_type)


def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def generate_srt(segments) -> str:
    """Generate standard SubRip (.srt) subtitle content."""
    lines = []
    for idx, seg in enumerate(segments, start=1):
        def to_srt_time(s):
            h = int(s // 3600)
            m = int((s % 3600) // 60)
            sec = int(s % 60)
            ms = int((s - int(s)) * 1000)
            return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

        start_t = to_srt_time(seg["start"])
        end_t = to_srt_time(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{idx}\n{start_t} --> {end_t}\n{text}\n")
    return "\n".join(lines)


def generate_vtt(segments) -> str:
    """Generate WebVTT (.vtt) subtitle content."""
    lines = ["WEBVTT\n"]
    for seg in segments:
        def to_vtt_time(s):
            h = int(s // 3600)
            m = int((s % 3600) // 60)
            sec = int(s % 60)
            ms = int((s - int(s)) * 1000)
            return f"{h:02d}:{m:02d}:{sec:02d}.{ms:03d}"

        start_t = to_vtt_time(seg["start"])
        end_t = to_vtt_time(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{start_t} --> {end_t}\n{text}\n")
    return "\n".join(lines)


def download_youtube_audio(url: str, output_dir: Path) -> str:
    """Download audio stream from YouTube URL using yt-dlp."""
    import yt_dlp
    out_tmpl = str(output_dir / "yt_audio.%(ext)s")
    ydl_opts = {
        "outtmpl": out_tmpl,
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    mp3_candidates = list(output_dir.glob("yt_audio*.mp3"))
    if mp3_candidates:
        return str(mp3_candidates[0])
    all_files = list(output_dir.glob("yt_audio*.*"))
    if all_files:
        return str(all_files[0])
    raise FileNotFoundError("Failed to download audio from YouTube.")


# ──────────────────────────────────────────────────────────────
# SIDEBAR CONTROLS
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/334643280?s=120&v=4", width=80)
    st.markdown("### **Aetherion Labs**")
    st.markdown("Autonomous AI Systems & Applied Intelligence")
    st.markdown("---")

    st.subheader("⚙️ Model Configuration")
    model_size = st.selectbox(
        "Whisper Model Size",
        options=["tiny", "base", "small", "medium"],
        index=1,
        help="Base is fast and balanced; Small/Medium provide superior accuracy."
    )

    import torch
    has_cuda = torch.cuda.is_available()
    device = "cuda" if has_cuda else "cpu"
    compute_type = "float16" if has_cuda else "int8"

    st.caption(f"Hardware Engine: **{device.upper()}** ({compute_type})")

    st.markdown("---")
    st.subheader("🌐 Developer & Links")
    st.markdown("[👤 Muhammed Hammad S](https://github.com/hammad986)")
    st.markdown("[🏢 Aetherion Labs Org](https://github.com/Aetherionlabs986)")
    st.markdown("[💼 LinkedIn (@hammad986)](https://www.linkedin.com/in/hammad986/)")
    st.markdown("[🤗 Hugging Face Profile](https://huggingface.co/hammad986)")


# ──────────────────────────────────────────────────────────────
# MAIN UI
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🎬 Whisper Video & Audio Transcriber</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Production-grade speech intelligence workbench powered by Faster-Whisper. Transcribe local video files or YouTube content with high timestamp accuracy.</div>', unsafe_allow_html=True)

input_tab1, input_tab2 = st.tabs(["📁 Upload Video / Audio File", "📺 YouTube URL"])

audio_file_path = None
temp_dir = tempfile.mkdtemp()

with input_tab1:
    uploaded_file = st.file_uploader(
        "Choose an audio or video file",
        type=["mp4", "mkv", "mov", "webm", "avi", "mp3", "wav", "m4a", "ogg"],
        help="Supported formats: MP4, MKV, MOV, WebM, MP3, WAV, etc."
    )
    if uploaded_file is not None:
        save_path = Path(temp_dir) / uploaded_file.name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_file_path = str(save_path)
        st.success(f"Loaded: `{uploaded_file.name}` ({len(uploaded_file.getbuffer()) / (1024*1024):.2f} MB)")

with input_tab2:
    yt_url = st.text_input("Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    if yt_url:
        if st.button("Fetch YouTube Audio", type="primary"):
            with st.spinner("Downloading audio stream from YouTube via yt-dlp..."):
                try:
                    audio_file_path = download_youtube_audio(yt_url, Path(temp_dir))
                    st.success("YouTube audio extracted successfully!")
                except Exception as e:
                    st.error(f"Error fetching YouTube stream: {e}")

st.markdown("---")

# Transcription Trigger
if audio_file_path and os.path.exists(audio_file_path):
    col_run, col_info = st.columns([1, 3])
    with col_run:
        start_btn = st.button("🚀 Start Transcription", type="primary", use_container_width=True)

    if start_btn:
        progress_bar = st.progress(0, text="Initializing Faster-Whisper engine...")
        status_box = st.empty()

        try:
            start_time = time.time()
            status_box.info(f"Loading `{model_size}` model on `{device}`...")
            model = load_whisper_model(model_size, device, compute_type)

            progress_bar.progress(30, text="Transcribing audio stream and detecting language...")
            status_box.info("Transcribing audio segments with timestamp alignment...")

            segments_iter, info = model.transcribe(
                audio_file_path,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )

            detected_lang = info.language
            lang_prob = info.language_probability * 100

            parsed_segments = []
            full_text_list = []

            for seg in segments_iter:
                parsed_segments.append({
                    "id": seg.id,
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                })
                full_text_list.append(seg.text)

            elapsed = time.time() - start_time
            progress_bar.progress(100, text="Transcription completed!")
            status_box.success(
                f"✅ Done in {elapsed:.2f}s | Detected Language: **{detected_lang.upper()}** ({lang_prob:.1f}% confidence) | Segments: {len(parsed_segments)}"
            )

            # Store in session state
            st.session_state["transcription_result"] = {
                "segments": parsed_segments,
                "full_text": "\n".join(full_text_list),
                "language": detected_lang,
                "duration": info.duration,
            }

        except Exception as err:
            status_box.error(f"Transcription failed: {err}")
            progress_bar.empty()

# Display Results if Available
if "transcription_result" in st.session_state:
    res = st.session_state["transcription_result"]
    segments = res["segments"]
    full_text = res["full_text"]

    st.markdown("### 📝 Transcription Results")

    # Export Buttons
    srt_content = generate_srt(segments)
    vtt_content = generate_vtt(segments)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "⬇️ Download Plain Text (.txt)",
            data=full_text,
            file_name="transcription.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "⬇️ Download Subtitles (.srt)",
            data=srt_content,
            file_name="subtitles.srt",
            mime="application/x-subrip",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            "⬇️ Download WebVTT (.vtt)",
            data=vtt_content,
            file_name="subtitles.vtt",
            mime="text/vtt",
            use_container_width=True,
        )

    st.markdown("---")

    # Search in transcript
    search_query = st.text_input("🔍 Search within transcript:", placeholder="Type a keyword to filter segments...")

    # Display Segments
    for seg in segments:
        text = seg["text"].strip()
        if search_query and search_query.lower() not in text.lower():
            continue

        start_str = format_timestamp(seg["start"])
        end_str = format_timestamp(seg["end"])

        st.markdown(
            f"""
            <div class="segment-box">
                <span class="time-badge">[{start_str} → {end_str}]</span>
                <span style="margin-left: 10px; font-size: 1rem;">{text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
