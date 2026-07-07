#!/usr/bin/env python3
"""Encode an {audio, text} manifest into frozen VoxCPM2 AudioVAE latents.

Training never touches raw audio: we encode every clip once (25 Hz x 64-dim,
stored fp16) and write sharded .pt files that pretrain.py / sft.py read directly.
"""

import argparse
import json
import os
import sys
import time

import librosa
import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from freyatts.vae import load_audio_vae

VAE_SAMPLE_RATE = 16000
LATENT_RATE_HZ = 25
LATENT_DIM = 64


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True,
                        help="JSONL manifest, one {\"audio\": path, \"text\": str} per line")
    parser.add_argument("--out", default="data/latents",
                        help="output directory for latent shards")
    parser.add_argument("--min_s", type=float, default=1.0,
                        help="drop clips shorter than this many seconds")
    parser.add_argument("--max_s", type=float, default=14.0,
                        help="drop clips longer than this many seconds")
    parser.add_argument("--shard_size", type=int, default=2000,
                        help="number of clips per .pt shard")
    parser.add_argument("--device", default="cuda",
                        help="device for the AudioVAE encoder")
    parser.add_argument("--prefix", default="shard",
                        help="shard filename prefix")
    return parser.parse_args()


def load_clip(path):
    """Read an audio file as mono float32 at the VAE sample rate."""
    audio, sr = sf.read(path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != VAE_SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=VAE_SAMPLE_RATE)
    return audio


def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)

    vae = load_audio_vae(args.device)

    shard = []
    shard_index = 0
    shard_manifest = []
    total_sec = 0.0
    kept = 0
    skipped = 0
    t0 = time.time()

    def flush():
        nonlocal shard, shard_index
        if not shard:
            return
        path = os.path.join(args.out, f"{args.prefix}_{shard_index:05d}.pt")
        torch.save(shard, path)
        shard_manifest.append(dict(file=os.path.basename(path), n=len(shard)))
        shard = []
        shard_index += 1

    with open(args.manifest) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            text = entry.get("text")
            audio_path = entry.get("audio")
            if not text or not audio_path:
                skipped += 1
                continue

            try:
                audio = load_clip(audio_path)
            except Exception as e:
                print(f"[skip] {audio_path}: {str(e)[:70]}", flush=True)
                skipped += 1
                continue

            duration = len(audio) / VAE_SAMPLE_RATE
            if duration < args.min_s or duration > args.max_s:
                skipped += 1
                continue

            with torch.no_grad():
                wav = torch.from_numpy(audio).to(args.device).view(1, 1, -1)
                z = vae.encode(wav, VAE_SAMPLE_RATE)  # [1, 64, T]
                latent = z.squeeze(0).transpose(0, 1).contiguous().to(torch.float16).cpu()  # [T, 64]

            shard.append(dict(latent=latent, text=str(text)[:300]))
            total_sec += duration
            kept += 1

            if len(shard) >= args.shard_size:
                flush()
            if kept % 1000 == 0:
                rt = total_sec / max(1.0, time.time() - t0)
                print(f"kept {kept} ({total_sec / 3600:.2f}h)  skipped {skipped}  {rt:.0f}x realtime", flush=True)

    flush()

    summary = dict(
        kept=kept,
        skipped=skipped,
        total_hours=round(total_sec / 3600, 2),
        shards=shard_manifest,
        latent_rate_hz=LATENT_RATE_HZ,
        latent_dim=LATENT_DIM,
    )
    with open(os.path.join(args.out, "manifest.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"done: {total_sec / 3600:.2f}h in {shard_index} shards -> {args.out}", flush=True)


if __name__ == "__main__":
    main()
