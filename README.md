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

- Local open-weight Hindi AI TTS using Indic Tiny TTS (no per-request API quota after the model is downloaded).\n- Online neural Hindi voices using the Edge TTS service (no API key required by this app).
- Hindi male and female voices: Madhur and Swara.
- Long-text chunking with paragraph and sentence boundaries.
- Adjustable narration speed, pitch and volume.
- MP3 output with chunks joined into one file.
- Automated tests and GitHub Actions.

> The first launch and initial local-model download require internet. Local AI speech generation works on this computer after the model is cached. Edge TTS and cloud IndicF5 remain online options.


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

## Optional open Hindi AI voice (compact IndicF5 student)

The app also includes **Hindi TTS — distilled IndicF5 student (~190M parameters)** as an online demo option. Choose **Generate with more natural open Hindi AI** in the app. This model is open-weight and Hindi-focused, and its model card reports a benchmark against the larger IndicF5 teacher; results are not a guarantee that every sentence will sound more natural than Edge TTS.

- Model card: https://huggingface.co/5ivatej/hindi-tts-190M
- Public demo: https://huggingface.co/spaces/5ivatej/hindi-tts-190M
- This option sends text to the public demo and requires internet. The demo may sleep, be busy, or change its API.
- It is exposed as an online option rather than a local model because the app targets a low-memory Windows laptop. Even a 190M-parameter model can use significant RAM and run slowly on CPU.
- The model card lists an MIT license for the student model and notes that the upstream IndicF5/F5-TTS licenses should also be reviewed.

## Local open-weight Hindi AI TTS

HindiVoiceForge uses **Indic Tiny TTS: Hindi** as its local AI speech engine. It has male and female Hindi voices, is designed for CPU inference, and downloads about 90 MB of model files. The first model download requires internet; after that, speech generation runs on your own computer without a Gemini API key or per-request API quota.

- The app downloads the model automatically the first time you click **Generate with Local Hindi AI**.
- The model is intended for Hindi written in Devanagari. English words in Latin script may be skipped; write names phonetically in Hindi where necessary.
- The voice is a calm reading style rather than highly expressive acting.
- Model weights are licensed CC BY 4.0 and require attribution; the model code is MIT. Review the [model card and license](https://huggingface.co/sulabhkatiyar/indic-tiny-tts-hindi) before redistribution or commercial use.
- PyTorch is a large dependency, so the first installation may take a while. The model is small, but the app still needs enough RAM for Python, PyTorch, and Gradio.

Model: [sulabhkatiyar/indic-tiny-tts-hindi](https://huggingface.co/sulabhkatiyar/indic-tiny-tts-hindi)

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

Pronunciation can still vary for English names, acronyms, unusual spellings and code-switching. The text is sent to the online speech service. The local AI option is included, but initial dependency and model downloads can be large. On a 4 GB RAM laptop, close other heavy applications while installing or generating audio.

## License

MIT. Third-party services and voice models remain subject to their own terms.
