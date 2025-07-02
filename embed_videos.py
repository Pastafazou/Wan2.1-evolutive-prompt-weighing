import jsonlines
import torch
import numpy as np
import tqdm
import cv2
import os
from PIL import Image
import open_clip

# ───────── Load XCLIP model (ViT-B-32) ─────────
device = torch.device("cpu")
model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32', pretrained='laion2b_s34b_b79k'
)
model.to(device).eval()

# ────── Extract all frames from a video (720p ok) ──────
def extract_frames(path):
    cap = cv2.VideoCapture(path)
    frames = []
    success, frame = cap.read()
    while success:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(Image.fromarray(rgb))
        success, frame = cap.read()
    cap.release()
    return frames

# ────── Embed all frames and average ──────
@torch.no_grad()
def embed_video(path):
    pil_frames = extract_frames(path)
    if len(pil_frames) == 0:
        raise RuntimeError(f"No frames in video: {path}")

    processed = [preprocess(f).unsqueeze(0).to(device) for f in pil_frames]
    batch = torch.cat(processed, dim=0)  # (N, 3, 224, 224)

    feats = model.encode_image(batch)   # (N, 512)
    avg_feat = feats.mean(0)
    norm_feat = avg_feat / avg_feat.norm()
    return norm_feat.cpu().numpy()

# ────── Main loop ──────
dataset_path = "feedback/dataset.jsonl"
out_path = "feedback/embeddings.jsonl"

with jsonlines.open(dataset_path) as reader, jsonlines.open(out_path, "w") as writer:
    for item in tqdm.tqdm(reader):
        vpath = item.get("video_path")
        if not vpath or not os.path.isfile(vpath):
            print(f"Skipping: {vpath}")
            continue
        try:
            emb = embed_video(vpath)
            item["embedding"] = emb.tolist()
            writer.write(item)
        except Exception as e:
            print(f"Failed to embed {vpath}: {e}")
