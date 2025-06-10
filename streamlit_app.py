# streamlit_app.py
import streamlit as st
import os
import docx
import uuid
import requests
from moviepy.editor import TextClip, ImageClip, concatenate_videoclips, AudioFileClip

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
VOICE_ID = st.secrets["VOICE_ID"]

st.set_page_config(page_title="Doc-to-Video", layout="centered")
st.title("📄➡️🎥 Google Doc to Narrated Video")

uploaded_file = st.file_uploader("Upload a Google Doc (.docx) with text and images", type=["docx"])

def parse_doc(filepath):
    doc = docx.Document(filepath)
    blocks = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            blocks.append({"type": "text", "content": text})
    for rel in doc.part._rels:
        rel_obj = doc.part._rels[rel]
        if "image" in rel_obj.target_ref:
            img_part = rel_obj.target_part
            img_data = img_part.blob
            img_name = f"{uuid.uuid4()}.png"
            img_path = os.path.join(UPLOAD_FOLDER, img_name)
            with open(img_path, "wb") as f:
                f.write(img_data)
            blocks.append({"type": "image", "content": img_path})
    return blocks

def generate_audio(blocks):
    text = " ".join(b["content"] for b in blocks if b["type"] == "text"])
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    )
    audio_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.mp3")
    with open(audio_path, "wb") as f:
        f.write(response.content)
    return audio_path

def build_video(blocks, audio_path):
    clips = []
    for b in blocks:
        if b["type"] == "text":
            clip = TextClip(b["content"], fontsize=40, color='white', size=(1280, 720)).set_duration(5)
        elif b["type"] == "image":
            clip = ImageClip(b["content"]).set_duration(5).resize(height=720)
        clips.append(clip)
    final_clip = concatenate_videoclips(clips, method="compose")
    audio_clip = AudioFileClip(audio_path)
    video_with_audio = final_clip.set_audio(audio_clip)
    output_path = os.path.join(OUTPUT_FOLDER, f"final_video_{uuid.uuid4()}.mp4")
    video_with_audio.write_videofile(output_path, fps=24)
    return output_path

if uploaded_file is not None:
    st.info("Parsing and generating video... This may take a minute.")
    with st.spinner("Processing your document..."):
        filename = f"{uuid.uuid4()}.docx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.read())
        blocks = parse_doc(filepath)
        audio = generate_audio(blocks)
        video = build_video(blocks, audio)

    st.success("✅ Video generated successfully!")
    st.video(video)
    with open(video, "rb") as f:
        st.download_button("Download Video", f, file_name="generated_video.mp4")
