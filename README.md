# HindiVoiceForge

A browser-based Hindi text-to-speech studio for long-form narration, movie recaps, educational scripts and voice-overs.

## One-click local setup (Windows)

You do not need Android Studio, Docker, or a separate FFmpeg installation. Python 3.11 is recommended.

1. Download this repository using **Code → Download ZIP** from https://github.com/Inexra/HindiVoiceForge and extract it.
2. Double-click **`START_HINDIVOICEFORGE.bat`**.
3. On first launch, it creates a local Python environment and installs dependencies. This can take a few minutes and requires internet.
4. A browser tab should open. The terminal prints the **Network URL** for your other devices.

### Open it from a phone on the same Wi-Fi

- Keep the terminal window open on the Windows computer.
- Connect the phone to the same home Wi-Fi and open the actual Network URL printed in the terminal, for example `http://192.168.1.25:7860`. The IP shown here is only an example.
- If Windows Firewall asks, allow Python on **Private networks only**.
- If it does not connect, verify both devices are on the same Wi-Fi and your router does not enable client/AP isolation.
- Close the terminal or press **Ctrl+C** to stop the website.

The port defaults to `7860`. The server is intended for a trusted home network only. Anyone who can reach it may use the page. Do not use public Wi-Fi, forward port 7860 on your router, or paste private/confidential scripts.

## Features

- Online neural Hindi voices using the Edge TTS service (no API key required by this app).
- Hindi male and female voices: Madhur and Swara.
- Long-text chunking with paragraph and sentence boundaries.
- Adjustable narration speed, pitch and volume.
- MP3 output with chunks joined into one file.
- Automated tests and GitHub Actions.

> Speech generation requires internet and relies on a third-party service. This project is not affiliated with Microsoft. Voice availability and service access can change. This first version does not provide offline neural TTS.


## Optional cloud AI voice (IndicF5)

The local Edge TTS button remains available. To try the Hindi-focused IndicF5 model without running it on your 4 GB laptop, you can deploy the template in `cloud_space/` to a Hugging Face Gradio Space and use the **Try the more natural cloud AI voice (IndicF5)** section in the app.

1. Create a Hugging Face account and create a Gradio Space. Free ZeroGPU use depends on account eligibility and quota; availability is not guaranteed.
2. Open https://huggingface.co/ai4bharat/IndicF5 and accept the model's access conditions.
3. Create a Hugging Face read token and add it to the Space as a secret named `HF_TOKEN`. This is not a paid TTS API key, but it is a credential needed to download this gated model. Never put it in this repository.
4. Copy `cloud_space/app.py` and `cloud_space/requirements.txt` to the **root** of your new Space. Wait for the Space to build and test it there.
5. In HindiVoiceForge, expand the cloud AI section, paste your Space URL, upload a short reference recording, and enter the exact transcript of that recording.
6. Generate a short test first. Cloud inference requires internet and may be unavailable when the Space sleeps or free GPU quota is exhausted.

IndicF5 uses a reference recording to guide voice characteristics and prosody. Use only recordings you own or have explicit permission to use; do not clone another person's voice without permission. The generated speech is not guaranteed to sound fully human. Text and reference audio are sent to your Space for processing, so do not submit confidential material.

Template source: https://github.com/AI4Bharat/IndicF5

## Gemini AI text-to-speech

HindiVoiceForge now includes an optional **Generate with Gemini TTS** mode. It sends text to Google's dedicated Gemini TTS API and saves the generated speech as an MP3. Edge TTS remains available as a fallback.

1. Open [Google AI Studio](https://aistudio.google.com/apikey) and create an API key.
2. Start HindiVoiceForge and expand **Generate with Gemini AI (natural expressive voice)**.
3. Paste your key into the password-style field, choose a voice, and adjust the delivery-style instructions if desired.
4. Generate a short test before sending a long script.

The app currently uses the Gemini 3.8 Flash TTS model. Google lists a free tier for this model, but availability, quotas, rate limits, and model access can vary by account and may change. Check the [official Gemini API pricing page](https://ai.google.dev/gemini-api/docs/pricing) before relying on it for large projects. On the free tier, Google may use submitted content to improve its products; avoid sensitive or confidential scripts. The key is entered locally in the app and is not saved to the repository. Do not share it or commit it to GitHub.

For more natural results, try a style such as: “Natural Hindi narration by an experienced Indian narrator; warm, clear, conversational, moderate pace, natural pauses, subtle emotion; speak the provided text exactly as written.” TTS output quality and Hindi pronunciation can vary, so listen to a short sample first.

Official documentation: [Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation) · [Pricing](https://ai.google.dev/gemini-api/docs/pricing)

## Manual start (optional)

Open PowerShell in the repository folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Voice choices

- **Hindi male:** `hi-IN-MadhurNeural`
- **Hindi female:** `hi-IN-SwaraNeural`

Pronunciation can still vary for English names, acronyms, unusual spellings and code-switching. The text is sent to the online speech service. A local model backend can be explored separately, but it is not included in this version; online mode is the practical starting point for a 4 GB RAM laptop.

## License

MIT. Third-party services and voice models remain subject to their own terms.
