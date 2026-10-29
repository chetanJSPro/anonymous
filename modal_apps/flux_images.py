"""
flux_images.py — Modal app that renders story scene images with FLUX.1-schnell
(Apache-2.0, commercial use OK). Paid from Modal credits; core/story.py uses it
only after Cloudflare's free daily allocation is spent.

Deploy once (and again after editing this file):
    modal deploy modal_apps/flux_images.py

Weights (~33 GB) are cached in a Modal Volume so only the very first cold
start downloads them. The container stays warm for a couple of minutes, so
the ~8-10 scenes of one episode share a single cold start.
"""

import io

import modal

app = modal.App("story-images")

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.5.1", "diffusers==0.32.2", "transformers==4.47.1",
    "accelerate==1.2.1", "sentencepiece==0.2.0", "protobuf==5.29.2",
    "huggingface_hub[hf_transfer]==0.27.0",
).env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/cache"})

cache = modal.Volume.from_name("flux-cache", create_if_missing=True)


@app.cls(gpu="L40S", image=image, volumes={"/cache": cache}, timeout=900,
         scaledown_window=120)
class Flux:
    @modal.enter()
    def load(self):
        import torch
        from diffusers import FluxPipeline
        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
        self.pipe.to("cuda")
        cache.commit()

    @modal.method()
    def generate(self, prompt, width=768, height=1344, seed=None):
        import torch
        gen = torch.Generator("cuda").manual_seed(seed) if seed is not None else None
        img = self.pipe(prompt, width=width, height=height, num_inference_steps=4,
                        guidance_scale=0.0, max_sequence_length=256, generator=gen).images[0]
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92)
        return buf.getvalue()


@app.local_entrypoint()
def main(prompt: str = "an old veteran smiling in a small-town diner, cinematic film still"):
    data = Flux().generate.remote(prompt)
    with open("flux_test.jpg", "wb") as f:
        f.write(data)
    print(f"wrote flux_test.jpg ({len(data)} bytes)")
