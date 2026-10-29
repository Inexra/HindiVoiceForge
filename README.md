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
