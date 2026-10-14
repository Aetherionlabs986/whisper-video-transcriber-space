---
title: Whisper Video Transcriber & Audio Intelligence
emoji: 🎬
colorFrom: purple
colorTo: indigo
sdk: streamlit
sdk_version: "1.32.0"
app_file: app.py
pinned: false
license: mit
---

# 🎬 Whisper Video Transcriber & Audio Intelligence Workbench

An enterprise-ready speech-to-text intelligence workbench powered by **Faster-Whisper (CTranslate2)**. Designed for local execution, cloud environments, and Hugging Face Spaces.

Developed by **[Muhammed Hammad S](https://github.com/hammad986)** under **[Aetherion Labs](https://github.com/Aetherionlabs986)**.

---

## ⚡ Features

- **Multimodal Audio Ingestion:** Direct file upload (MP4, MKV, MOV, WebM, MP3, WAV, M4A) or stream extraction from YouTube URLs via `yt-dlp`.
- **Faster-Whisper Engine:** High-throughput CTranslate2 inference with VAD (Voice Activity Detection) filter to strip background silence.
- **Timestamp Alignment:** Frame-level segment timestamps `[HH:MM:SS]`.
- **Multi-Format Export:** Instant export to Plain Text (`.txt`), SubRip Subtitles (`.srt`), and WebVTT (`.vtt`).
- **In-Transcript Search:** Instant keyword lookup with highlighted playback segments.
- **Zero-Cloud Dependency:** Fully self-contained local inference with GPU (CUDA) and CPU fallback.

---

## 🚀 Quickstart (Local Run)

```bash
# 1. Clone repository
git clone https://github.com/Aetherionlabs986/whisper-video-transcriber-space.git
cd whisper-video-transcriber-space

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ensure ffmpeg is installed
# Windows: winget install Gyan.FFmpeg
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg

# 4. Launch Streamlit UI
streamlit run app.py
```

---

## 🌐 Deploy to Hugging Face Spaces

1. Create a new Space on [Hugging Face](https://huggingface.co/new-space).
2. Choose **Streamlit** as SDK and set visibility to **Public**.
3. Push or clone this repository to the Hugging Face Space Git remote:
```bash
git remote add space https://huggingface.co/spaces/hammad986/whisper-video-transcriber
git push space main
```

---

## 👨‍💻 Author & Maintainer

* **Muhammed Hammad S** ([@hammad986](https://github.com/hammad986))
* **Organization:** [Aetherion Labs](https://github.com/Aetherionlabs986)
* **LinkedIn:** [linkedin.com/in/hammad986](https://www.linkedin.com/in/hammad986/)
* **Portfolio:** [hammad986.dpdns.org](https://hammad986.dpdns.org)
