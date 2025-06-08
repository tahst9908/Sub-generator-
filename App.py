import streamlit as st
import whisper
from deep_translator import GoogleTranslator
import os
from tempfile import NamedTemporaryFile

@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

def translate_text(text, lang):
    return GoogleTranslator(source='auto', target=lang).translate(text)

def save_srt(text, lang):
    lines = text.split()
    srt = ""
    for i in range(0, len(lines), 10):
        idx = i // 10 + 1
        start = f"00:00:{i:02},000"
        end = f"00:00:{i+10:02},000"
        srt += f"{idx}\n{start} --> {end}\n{' '.join(lines[i:i+10])}\n\n"
    filename = f"subtitles_{lang}.srt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(srt)
    return filename

st.set_page_config(page_title="Subtitle Generator", layout="centered")
st.title("🎬 Subtitle Generator")
st.write("Upload a video to get subtitles in multiple languages.")

video = st.file_uploader("Upload video", type=["mp4", "mov", "mkv"])
if video:
    st.video(video)
    with NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
        temp.write(video.read())
        temp_path = temp.name

    st.write("Transcribing...")
    result = model.transcribe(temp_path)
    text = result["text"]
    st.success("Done!")

    langs = st.multiselect("Select languages", ["en", "es", "fr", "de", "hi", "zh", "ko", "ar"])
    for lang in langs:
        translated = translate_text(text, lang)
        srt_file = save_srt(translated, lang)
        with open(srt_file, "r") as f:
            st.download_button(f"Download {lang.upper()} subtitles", f.read(), file_name=srt_file)
    os.remove(temp_path)
