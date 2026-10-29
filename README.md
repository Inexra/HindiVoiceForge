# HindiVoiceForge

A browser-based Hindi text-to-speech studio for long-form narration, movie recaps, educational scripts and voice-overs.

## First version

- Online neural Hindi voices using Microsoft's Edge TTS service (no API key required by this app).
- Hindi male and female voices: Madhur and Swara.
- Long-text chunking with paragraph and sentence boundaries.
- Adjustable narration speed, pitch and volume.
- MP3 output with chunks joined into one file.
- Pronunciation-friendly text workflow and a simple Gradio interface.
- Automated tests and GitHub Actions.

> **Important:** The online voice mode requires an internet connection and relies on a third-party service. This project is not affiliated with Microsoft. Do not submit confidential text. Voice availability and service access can change.

## Run locally on Windows

Python 3.11 is recommended. FFmpeg is required for combining generated audio.

1. Install FFmpeg from https://ffmpeg.org/download.html and ensure `ffmpeg` is available on PATH.
2. Open PowerShell in this repository.
3. Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open the local URL printed by Gradio.

## Voice choices

- **Hindi male:** `hi-IN-MadhurNeural`
- **Hindi female:** `hi-IN-SwaraNeural`

These are neural voices. Pronunciation can still vary for English names, acronyms, unusual spellings and code-switching. Listen to the result and edit difficult names before generating the final audio.

## Usage tips

- Keep Hindi text in Devanagari where possible.
- Put paragraph breaks where you want natural pauses.
- For English film titles or uncommon names, test the pronunciation in a short sample first.
- Generate large scripts in smaller batches if your connection is unstable.

## Privacy and limitations

The text is sent to the online speech service to generate audio. This first version does not provide offline neural TTS. A local model backend can be added later, but quality, language coverage and hardware requirements need to be tested separately. Your 4 GB RAM laptop is better suited to the online mode.

## License

MIT. Third-party services and voice models remain subject to their own terms.
