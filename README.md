WAN2.1 Motion Preference Feedback Loop - version 0.1 / proof of concept
A self-improving ComfyUI workflow for WAN‑based motion generation.
Users generate 81-frame videos, rank them, and the system learns which prompt tokens correlate with desired motions — then applies weightings automatically to future prompts.

Features
Generate motion clips via WAN2.1

Rate each clip (1–5) in ComfyUI

ComfyUI logs metadata: prompt, seed, ranking, video path

Use anaconda to embed videos with XCLIP

Use anaconda to rank tokens via motion correlation

ComfyUI Re-weights prompts for the next generations

This creates a full generate → rate → learn → refine loop — all within lightweight Python & ComfyUI, no fine-tuning required.

System Overview

ComfyUI:
[String Holder] → [Prompt Mutator] → (WAN2.1 workflow) → [Generate]
                                      ↑ ranking manually in ComfyUI
                                      ↓
                              [Metadata Logger] → dataset.jsonl
Then offline:

embed_videos.py → embeddings.jsonl

rank_learn.py → token_weights.json

On next run, mutator uses new weights automatically

✅ Installation
Clone repo into your ComfyUI custom nodes:

cd ComfyUI/custom_nodes
git clone https://github.com/Pastafazou/Wan2.1-evolutive-prompt-weighing

Install Python tools in anaconda:

cd wan2-motion-feedback
conda create -n wan_feedback python=3.10 -y
conda activate wan_feedback
conda install -c conda-forge pytorch torchvision torchaudio -y
pip install open_clip_torch jsonlines tqdm opencv-python pillow regex
Restart ComfyUI. You should see nodes:

String Holder

Prompt Weight Mutator

Metadata Logger

Usage
A. Generate & Rate
Use String Holder to input your prompt.

Wire to Prompt Weight Mutator (weights will apply once learned).

Set seed and feed into your WAN2.1 workflow.

Generate an 81-frame video (WebM recommended).

Set a 1–5 ranking in Metadata Logger and wire prompt, seed, ranking, and video path.

Run Metadata Logger → JSON will appear via DisplayAny (copy it).

Paste the JSON line into feedback/dataset.jsonl.

B. Learn Token Weights
conda activate wan_feedback
python embed_videos.py        # turn videos + metadata into embeddings
python rank_learn.py          # create token_weights.json
➡ feedback/token_weights.json now contains your learned token weight mappings.

C. Improve Next Generation
Use Prompt Weight Mutator in your workflow

Next generation prompts are now automatically weighted

Best Practices
Start with 4–8 clip batch, then loop with new rankings

Keep prompt length focused on motion + camera words

Run rank_learn.py with len >= 1 until dataset size > 4, then tighten to >= 3

Adjust boost_scale / damp_scale in mutator to fine-tune intensity

Current Weaknesses
This project was develloped in conjunction with ChatGPT which is not the best at writing code, but i'm unfamiliar with the packages/syntax comfyui requires. Therefore most of the project is hastily hacked together.
As a result, certain things don't make sense. The ranking is applied at the same time as the generation, so you need to change it before pasting into the dataset.jsonl 
The seed and prompt need to come from a secondary node so the metadata logger can extract it
Now other issues come from my personnal comfyui setup.
Firstly, mine is unable to save automatically. As such I am renaming each clip manually along with changing the filename in the .jsonl string spat out by the logger (this will probably not change anytime soon)
Secondly, as my computer uses an Intel Arc, the project currently runs on CPU for embedding, which means it takes approx. 15s/video (on i5-13600KF). 
I may update this in the future, but I do not have access to an NVIDIA card, so garanteeing compatibility would not be possible.

Roadmap & Extensions
✅ Automated prompt weighting

⚠️ Auto-suggestion (not currently supported)

⬜ Later: prune bad tokens automatically

⬜ Later: LLM-based prompt mutation & LoRA training for obscure movements



