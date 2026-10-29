from __future__ import annotations

import asyncio
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import gradio as gr
import imageio_ffmpeg

APP_TITLE = "HindiVoiceForge"
HOST = "0.0.0.0"
PORT = int(os.environ.get("HINDIVOICEFORGE_PORT", "7860"))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

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
        for sentence in re.split(r"(?<=[.!?।॥])\s+", paragraph):
            if sentence.strip():
                add_piece(sentence)
        # Keep paragraph boundaries so the audio can breathe between ideas.
        if current:
            chunks.append(current)
            current = ""
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


def _concat_file_line(path: Path) -> str:
    """Format a path for FFmpeg's concat demuxer."""
    value = path.resolve().as_posix().replace("'", "'\\''")
    return f"file '{value}'"


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
    if len(text) > 100_000:
        raise gr.Error("This version supports up to 100,000 characters per job. Split larger scripts into separate jobs.")

    chunks = split_text(text)
    if not chunks:
        raise gr.Error("There is no text to convert.")

    try:
        with tempfile.TemporaryDirectory(prefix="hindi-voiceforge-") as tmp:
            tmp_path = Path(tmp)
            part_paths: list[Path] = []
            for index, chunk in enumerate(chunks, start=1):
                progress((index - 1) / len(chunks), desc=f"Generating section {index} of {len(chunks)}")
                part_path = tmp_path / f"part_{index:04d}.mp3"
                asyncio.run(synthesize_chunk(
                    chunk, VOICES[voice_label], int(rate), int(pitch), int(volume), part_path
                ))
                if not part_path.exists() or part_path.stat().st_size == 0:
                    raise RuntimeError(f"Voice service returned an empty audio file for section {index}.")
                part_paths.append(part_path)

            progress(0.92, desc="Joining audio sections")
            # Add a short natural pause at paragraph/chunk boundaries instead of
            # stitching every generated section directly together.
            silence_path = tmp_path / "pause.mp3"
            silence_command = [
                FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", "0.28", "-codec:a", "libmp3lame", "-b:a", "48k",
                str(silence_path),
            ]
            silence_result = subprocess.run(
                silence_command, capture_output=True, text=True, check=False
            )
            if silence_result.returncode != 0 or not silence_path.exists():
                detail = (silence_result.stderr or silence_result.stdout or "Could not create pause audio").strip()
                raise RuntimeError(detail[-800:])

            concat_items: list[Path] = []
            for index, part_path in enumerate(part_paths):
                concat_items.append(part_path)
                if index < len(part_paths) - 1:
                    concat_items.append(silence_path)

            concat_list = tmp_path / "concat_list.txt"
            concat_list.write_text(
                "\n".join(_concat_file_line(path) for path in concat_items),
                encoding="utf-8",
            )
            output_path = Path(tempfile.gettempdir()) / f"hindi_voiceforge_{os.getpid()}.mp3"
            command = [
                FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-vn", "-c:a", "libmp3lame", "-b:a", "192k", str(output_path),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            if result.returncode != 0 or not output_path.exists() or output_path.stat().st_size == 0:
                detail = (result.stderr or result.stdout or "FFmpeg did not create an output file").strip()
                raise RuntimeError(detail[-1200:])

            progress(1.0, desc="Done")
            return str(output_path), f"Done. Generated {len(chunks)} section(s) and joined them into one MP3."
    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(
            "Audio generation failed. Check your internet connection. HindiVoiceForge includes its own FFmpeg, "
            "so you do not need to install FFmpeg separately. "
            f"Technical detail: {type(exc).__name__}: {exc}"
        ) from exc


def generate_cloud_audio(
    text: str,
    cloud_space_url: str,
    reference_audio: str,
    reference_text: str,
    progress=gr.Progress(),
):
    """Use a user-owned Hugging Face Space for IndicF5 cloud inference."""
    if not text or not text.strip():
        raise gr.Error("Paste your Hindi script first.")
    if len(text) > 100_000:
        raise gr.Error("This version supports up to 100,000 characters per job.")
    if not cloud_space_url or not cloud_space_url.strip():
        raise gr.Error("Paste the URL of your deployed HindiVoiceForge Cloud Space.")
    if not reference_audio:
        raise gr.Error("Upload a short reference voice recording you own or have permission to use.")
    if not reference_text or not reference_text.strip():
        raise gr.Error("Enter the exact transcript spoken in the reference recording.")

    try:
        from gradio_client import Client

        chunks = split_text(text)
        if not chunks:
            raise gr.Error("There is no text to convert.")

        space_url = cloud_space_url.strip().rstrip("/")
        if not (space_url.startswith("https://") or space_url.startswith("http://")):
            raise gr.Error("Cloud Space URL should start with https:// or http://.")
        client = Client(space_url, verbose=False)

        with tempfile.TemporaryDirectory(prefix="hindi-voiceforge-cloud-") as tmp:
            tmp_path = Path(tmp)
            wav_paths: list[Path] = []
            for index, chunk in enumerate(chunks, start=1):
                progress((index - 1) / len(chunks), desc=f"Cloud AI: section {index} of {len(chunks)}")
                result = client.predict(
                    chunk,
                    reference_audio,
                    reference_text.strip(),
                    api_name="/generate_speech",
                )
                if isinstance(result, (tuple, list)):
                    result = result[0]
                source_path = Path(str(result))
                if not source_path.exists() or source_path.stat().st_size == 0:
                    raise RuntimeError("The Cloud Space returned no audio file.")
                destination = tmp_path / f"part_{index:04d}.wav"
                shutil.copy2(source_path, destination)
                wav_paths.append(destination)

            progress(0.92, desc="Joining cloud-generated audio")
            silence_path = tmp_path / "pause.wav"
            silence_command = [
                FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", "0.28", "-c:a", "pcm_s16le", str(silence_path),
            ]
            silence_result = subprocess.run(silence_command, capture_output=True, text=True, check=False)
            if silence_result.returncode != 0 or not silence_path.exists():
                raise RuntimeError((silence_result.stderr or "Could not create pause audio")[-800:])

            concat_items: list[Path] = []
            for index, path in enumerate(wav_paths):
                concat_items.append(path)
                if index < len(wav_paths) - 1:
                    concat_items.append(silence_path)
            concat_list = tmp_path / "concat_list.txt"
            concat_list.write_text(
                "\n".join(_concat_file_line(path) for path in concat_items),
                encoding="utf-8",
            )
            output_path = Path(tempfile.gettempdir()) / f"hindi_voiceforge_cloud_{os.getpid()}.mp3"
            command = [
                FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(concat_list),
                "-vn", "-c:a", "libmp3lame", "-b:a", "192k", str(output_path),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            if result.returncode != 0 or not output_path.exists() or output_path.stat().st_size == 0:
                raise RuntimeError((result.stderr or result.stdout or "FFmpeg could not join audio")[-1000:])
            progress(1.0, desc="Done")
            return str(output_path), f"Done. IndicF5 cloud voice generated {len(chunks)} section(s)."

    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(
            "Cloud generation failed. Check that your Space is running, the model access was accepted, "
            "and the Space exposes the /generate_speech API. "
            f"Technical detail: {type(exc).__name__}: {exc}"
        ) from exc


with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎙️ HindiVoiceForge
        Turn Hindi scripts into downloadable neural voice-overs.

        **Online mode:** internet is required for Hindi neural voices. Other devices on the same Wi-Fi can open this site at this computer’s LAN IP and port 7860. Use only on a trusted home network; do not submit confidential text.
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
                rate = gr.Slider(-25, 25, value=-5, step=5, label="Speed (%)")
            with gr.Row():
                pitch = gr.Slider(-10, 10, value=0, step=1, label="Pitch (Hz)")
                volume = gr.Slider(-20, 20, value=0, step=5, label="Volume (%)")
            generate = gr.Button("Generate with Edge TTS", variant="primary")
            with gr.Accordion("Try the more natural cloud AI voice (IndicF5)", open=False):
                gr.Markdown(
                    "Requires your own deployed Hugging Face Space. This model uses a reference recording, "
                    "so upload a voice you own or have permission to use and enter its exact transcript."
                )
                cloud_space_url = gr.Textbox(
                    label="Cloud Space URL",
                    placeholder="https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE",
                )
                reference_audio = gr.Audio(label="Reference voice recording", type="filepath")
                reference_text = gr.Textbox(
                    label="Exact transcript of the reference recording",
                    lines=2,
                    placeholder="Type exactly what is spoken in the recording…",
                )
                generate_cloud = gr.Button("Generate with IndicF5 Cloud AI", variant="primary")
        with gr.Column(scale=2):
            audio_file = gr.Audio(label="Preview", type="filepath")
            status = gr.Textbox(label="Status", interactive=False)
            gr.Markdown(
                """
                ### Tips for more natural narration
                - Start around **-5% speed** for a calmer Hindi delivery; test 0% for energetic scripts.
                - Keep Hindi in Devanagari and write numbers the way you want them spoken.
                - Add commas where a speaker would take a small breath and full stops at complete thoughts.
                - Use a blank line between paragraphs; the app adds a short pause between sections.
                - Spell out tricky names or English terms phonetically in Hindi if needed.
                - Avoid ALL CAPS, repeated exclamation marks, and long unpunctuated sentences.
                
                **Note:** The free online voice engine does not expose full acting/emotion controls. These changes improve pacing, but cannot guarantee a fully human voice.
                """
            )
    generate.click(
        fn=generate_audio,
        inputs=[script, voice, rate, pitch, volume],
        outputs=[audio_file, status],
    )
    generate_cloud.click(
        fn=generate_cloud_audio,
        inputs=[script, cloud_space_url, reference_audio, reference_text],
        outputs=[audio_file, status],
    )

if __name__ == "__main__":
    demo.queue().launch(server_name=HOST, server_port=PORT, share=False, inbrowser=True)
