import os
from functools import lru_cache

import gradio as gr
import numpy as np
import soundfile as sf
import spaces
import torch
from transformers import AutoModel

MODEL_ID = "ai4bharat/IndicF5"


@lru_cache(maxsize=1)
def get_model():
    # The model is cached on CPU between requests; ZeroGPU is allocated only
    # while generate_speech is running.
    return AutoModel.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        token=os.environ.get("HF_TOKEN"),
    )


@spaces.GPU(duration=180)
def generate_speech(text: str, reference_audio: str, reference_text: str):
    if not text or not text.strip():
        raise gr.Error("Enter Hindi text first.")
    if len(text) > 1800:
        raise gr.Error("Keep each request under 1,800 characters. HindiVoiceForge splits longer scripts.")
    if not reference_audio:
        raise gr.Error("Upload a short reference recording you own or have permission to use.")
    if not reference_text or not reference_text.strip():
        raise gr.Error("Enter the exact words spoken in the reference recording.")

    model = get_model()
    try:
        model = model.to("cuda")
        with torch.inference_mode():
            audio = model(
                text.strip(),
                ref_audio_path=reference_audio,
                ref_text=reference_text.strip(),
            )
    finally:
        # Free GPU allocation after each request on ZeroGPU.
        try:
            model = model.to("cpu")
        except Exception:
            pass
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    audio = np.asarray(audio)
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    else:
        audio = audio.astype(np.float32)
    out_path = "/tmp/hindivoiceforge_indicf5.wav"
    sf.write(out_path, audio, samplerate=24000)
    return out_path


with gr.Blocks(title="HindiVoiceForge Cloud Voice") as demo:
    gr.Markdown(
        """
        # HindiVoiceForge · Cloud Hindi Voice
        Powered by AI4Bharat IndicF5. This Space uses GPU compute when available.

        **Important:** Use only a reference voice you own or have explicit permission to use.
        Your text and reference audio are sent to this Space for processing. Avoid confidential content.
        """
    )
    text = gr.Textbox(label="Hindi text", lines=6, placeholder="यहाँ हिंदी पाठ लिखें…")
    reference_audio = gr.Audio(label="Reference voice (WAV/MP3)", type="filepath")
    reference_text = gr.Textbox(
        label="Exact transcript of the reference audio",
        lines=2,
        placeholder="Reference recording में जो शब्द बोले गए हैं, वही यहाँ लिखें।",
    )
    generate = gr.Button("Generate speech", variant="primary")
    output = gr.Audio(label="Generated Hindi speech", type="filepath")
    generate.click(
        fn=generate_speech,
        inputs=[text, reference_audio, reference_text],
        outputs=output,
        api_name="generate_speech",
    )

demo.queue().launch()
