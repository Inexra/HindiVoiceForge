from __future__ import annotations

import asyncio
import os
import re
import tempfile
from pathlib import Path

import edge_tts
import gradio as gr
from pydub import AudioSegment

APP_TITLE = "HindiVoiceForge"
VOICES = {
    "Hindi male · Madhur": "hi-IN-MadhurNeural",
    "Hindi female · Swara": "hi-IN-SwaraNeural",
}


def split_text(text: str, max_chars: int = 2200) -> list[str]:
    """Split long text at paragraph/sentence boundaries without losing content."""
    text = text.strip()
    if not text:
        return []
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    def add_piece(piece: str) -> None:
        nonlocal current
        piece = piece.strip()
        if not piece:
            return
        while len(piece) > max_chars:
            cut = piece.rfind(" ", 0, max_chars + 1)
            if cut < max_chars // 2:
                cut = max_chars
            head, piece = piece[:cut].strip(), piece[cut:].strip()
            if current:
                chunks.append(current)
                current = ""
            if head:
                chunks.append(head)
        if not current:
            current = piece
        elif len(current) + 1 + len(piece) <= max_chars:
            current += " " + piece
        else:
            chunks.append(current)
            current = piece

    for paragraph in paragraphs:
        # Keep punctuation attached to each sentence.
        sentences = re.split(r"(?<=[.!?।॥])\s+", paragraph)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(sentence) > max_chars:
                add_piece(sentence)
            else:
                add_piece(sentence)
    if current:
        chunks.append(current)
    return chunks


async def synthesize_chunk(text: str, voice: str, rate: int, pitch: int, volume: int, output: Path) -> None:
    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=f"{rate:+d}%",
        pitch=f"{pitch:+d}Hz",
        volume=f"{volume:+d}%",
    )
    await communicate.save(str(output))


def generate_audio(
    text: str,
    voice_label: str,
    rate: int,
    pitch: int,
    volume: int,
    progress=gr.Progress(),
):
    if not text or not text.strip():
        raise gr.Error("Paste your Hindi script first.")
    if voice_label not in VOICES:
        raise gr.Error("Choose a supported Hindi voice.")

    chunks = split_text(text)
    if not chunks:
        raise gr.Error("There is no text to convert.")
    if len(text) > 100_000:
        raise gr.Error("This version supports up to 100,000 characters per job. Split larger scripts into separate jobs.")

    try:
        with tempfile.TemporaryDirectory(prefix="hindi-voiceforge-") as tmp:
            tmp_path = Path(tmp)
            audio_parts: list[AudioSegment] = []
            for index, chunk in enumerate(chunks, start=1):
                progress((index - 1) / len(chunks), desc=f"Generating section {index} of {len(chunks)}")
                part_path = tmp_path / f"part_{index:04d}.mp3"
                asyncio.run(synthesize_chunk(chunk, VOICES[voice_label], int(rate), int(pitch), int(volume), part_path))
                audio_parts.append(AudioSegment.from_file(part_path, format="mp3"))
            progress(0.95, desc="Joining audio sections")
            combined = AudioSegment.empty()
            for index, part in enumerate(audio_parts):
                if index:
                    combined += AudioSegment.silent(duration=220)
                combined += part
            output_path = Path(tempfile.gettempdir()) / f"hindi_voiceforge_{os.getpid()}.mp3"
            combined.export(output_path, format="mp3", bitrate="192k")
            progress(1.0, desc="Done")
            duration = len(combined) / 1000
            return str(output_path), f"Done. Generated {len(chunks)} section(s), {duration / 60:.1f} minute(s) of audio."
    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(
            "Audio generation failed. Check your internet connection and make sure FFmpeg is installed and available on PATH. "
            f"Technical detail: {type(exc).__name__}: {exc}"
        ) from exc


with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎙️ HindiVoiceForge
        Turn Hindi scripts into downloadable neural voice-overs.

        **Online mode:** uses internet-based Hindi neural voices. Do not submit private or confidential text.
        """
    )
    with gr.Row():
        with gr.Column(scale=3):
            script = gr.Textbox(
                label="Your script",
                placeholder="Paste your Hindi narration here…",
                lines=18,
                max_lines=30,
            )
            with gr.Row():
                voice = gr.Dropdown(choices=list(VOICES), value="Hindi male · Madhur", label="Hindi voice")
                rate = gr.Slider(-25, 25, value=0, step=5, label="Speed (%)")
            with gr.Row():
                pitch = gr.Slider(-10, 10, value=0, step=1, label="Pitch (Hz)")
                volume = gr.Slider(-20, 20, value=0, step=5, label="Volume (%)")
            generate = gr.Button("Generate Hindi audio", variant="primary")
        with gr.Column(scale=2):
            audio_file = gr.Audio(label="Preview", type="filepath")
            status = gr.Textbox(label="Status", interactive=False)
            gr.Markdown(
                """
                ### Tips for better pronunciation
                - Keep Hindi in Devanagari.
                - Use punctuation and paragraph breaks.
                - Test difficult English names in a short sample.
                - The generated audio is joined into one MP3.
                """
            )
    generate.click(
        fn=generate_audio,
        inputs=[script, voice, rate, pitch, volume],
        outputs=[audio_file, status],
    )

if __name__ == "__main__":
    demo.queue().launch()
