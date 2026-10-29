---
title: HindiVoiceForge Cloud Voice
emoji: 🎙️
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.20.0
app_file: app.py
pinned: false
---

# HindiVoiceForge Cloud Voice (IndicF5)

This Space is a cloud backend template for the HindiVoiceForge Windows app.

## Setup

1. Create a Hugging Face account and create a **Gradio Space** using ZeroGPU if your account is eligible.
2. Open the model page https://huggingface.co/ai4bharat/IndicF5 and accept its access conditions.
3. Create a Hugging Face read token with permission to read the gated model. In Space **Settings → Secrets**, add it as `HF_TOKEN`. Do not put the token in code or in a public repository.
4. Copy `app.py` and `requirements.txt` from this folder to the **root** of your Space. The Space rebuilds automatically.
5. Wait for the Space to finish building, then open it and test a short Hindi sentence with a reference recording.

## Connect HindiVoiceForge

Copy the Space URL (for example, `https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE`) into the **Cloud Space URL** field in HindiVoiceForge.

## Important limits

- This uses the IndicF5 model, which requires a reference audio clip and the exact transcript spoken in that clip.
- Free GPU access and quotas can change. The Space may sleep or be unavailable when quota is exhausted.
- This model repository is gated: you must accept its conditions and supply a Hugging Face read token as a Space secret.
- Use reference voices only when you own them or have explicit permission. Do not clone a real person's voice without permission.
- This is an experimental template. ZeroGPU model initialization and memory behavior can vary as Hugging Face updates its platform.
