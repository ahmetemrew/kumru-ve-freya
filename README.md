<h2 align="center">FreyaTTS: An Efficient 183M Turkish Speech Foundation Model</h2>

<p align="center">
  <a href="https://huggingface.co/freyavoice/freya-tts"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-freya--tts-yellow" alt="Hugging Face"></a>
  <a href="https://huggingface.co/datasets/freyavoice/freya-tr-eval"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-Freya--TR--Eval-orange" alt="Eval Set"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-Apache--2.0-green" alt="License"></a>
</p>

FreyaTTS is a **183M-parameter Turkish text-to-speech model**. It reads Turkish directly at the character level (92 symbols, no phonemizer, no G2P) and generates speech with a **non-autoregressive conditional flow-matching DiT** in the frozen AudioVAE2 latent space (25 Hz, 64-dim latents, 16 kHz encode / 48 kHz decode).

The result is a model that runs comfortably where 2B-class TTS models cannot: 1.5 GB of VRAM on a GPU, real time on a laptop CPU, and well under real time on the Apple Neural Engine.

### Highlights

- **Small and fast** - 183.2M parameters, RTF 0.10-0.11 and TTFT ~0.5 s on an RTX 4090, about 3.2x faster RTF and 3.7x less VRAM than the 2B VoxCPM2
- **Tokenizer-free Turkish** - character-level input over a 92-symbol vocabulary, no phonemizer or G2P stage to maintain
- **Non-autoregressive** - a single 32-step Euler ODE per clause, no classifier-free guidance needed
- **48 kHz output** - the frozen AudioVAE2 decodes 25 Hz latents straight to 48 kHz audio
- **Runs on CPUs** - real time on an Apple M3 laptop CPU (RTF 0.70 fp32), and RTF ~0.12 end to end via Core ML on Apple silicon
- **Apache-2.0** - weights and code free for commercial use

### News

- **[2026.07]** FreyaTTS 0.1.0 released: [weights](https://huggingface.co/freyavoice/freya-tts) | [eval set](https://huggingface.co/datasets/freyavoice/freya-tr-eval)

---

## Quick Start

### Installation

```sh
git clone https://github.com/freyavoiceai/FreyaTTS.git
cd FreyaTTS
pip install -r requirements.txt
```

### Command line

```sh
python infer.py --text "Merhaba, size nasıl yardımcı olabilirim?" --out output.wav
```

### Batch inference

Non-autoregressive generation batches naturally: one masked ODE solve serves a
whole batch of requests. On an RTX 4090 this reaches about 65 seconds of audio
per wall-second at batch size 8 in under 4 GB of VRAM.

```sh
python batch_infer.py --texts texts.txt --outdir wavs/ --batch-size 8
```

### Python API

```python
from freyatts import FreyaTTS

tts = FreyaTTS.from_pretrained("freyavoice/freya-tts", device="cuda")
wav = tts.synthesize("Merhaba, size nasıl yardımcı olabilirim?")   # np.float32, 48 kHz
tts.save_wav(wav, "output.wav")
```

`from_pretrained` also accepts a local directory containing `config.json` and `model.safetensors`. `synthesize` takes optional `steps` (default 32) and `seed` (default 0) arguments. Long inputs are normalized and split into clauses automatically, then joined with short pauses. Normalization spells out digit runs in Turkish (`14:45` becomes `on dört kırk beş`): the duration predictor sizes the utterance from the character sequence, so numbers left as digits come out truncated.

Or run the bundled example:

```sh
python examples/synthesize.py --text "Merhaba, size nasıl yardımcı olabilirim?" --output output.wav
```

---

## Model

FreyaTTS is a conditional flow-matching diffusion transformer (DiT) operating in the latent space of the frozen AudioVAE2:

- **Text encoding:** character-level Turkish, 92 symbols shipped with the package (`freyatts/char_vocab.json`)
- **Generation:** non-autoregressive flow matching, 32 Euler ODE steps, no CFG
- **Latent space:** 64-dim latents at 25 Hz; AudioVAE2 encodes at 16 kHz and decodes at 48 kHz
- **Training:** from scratch on Turkish speech; pretraining followed by SFT stage 1/2 (voice lock, short-utterance coverage)

AudioVAE2 is not retrained. It is downloaded from [openbmb/VoxCPM2](https://huggingface.co/openbmb/VoxCPM2) (Apache-2.0) at load time via the `voxcpm` package.

## Performance

### Intelligibility (Freya-TR-Eval)

Evaluated on [Freya-TR-Eval](https://huggingface.co/datasets/freyavoice/freya-tr-eval), a public Turkish TTS evaluation set.

| Model | Params | WER ⬇ | CER ⬇ |
| ----- | ------ | ----- | ----- |
| **FreyaTTS** | **183M** | **8.0%** | **3.0%** |
| XTTS-v2 | 0.5B | 11.1% | - |
| F5-TTS | 0.3B | 24.3% | - |

FreyaTTS ranks 3rd of 7 among open sub-1B Turkish TTS models on this benchmark, at a fraction of the compute of the models above it.

### Speed

| Setting | RTF | Notes |
| ------- | --- | ----- |
| RTX 4090 | 0.10-0.11 | TTFT ~0.5 s, 1.5 GB VRAM, 9.4 audio-s/s at concurrency 4 |
| Apple M3 CPU (fp32) | 0.70 | real time on a laptop, no GPU |
| Apple silicon, Core ML | ~0.12 | end to end via the Neural Engine |

Compared to the 2B VoxCPM2, FreyaTTS is about 3.2x faster in RTF and uses 3.7x less VRAM.

Reproduce with `eval/benchmark.py` (WER/CER) and `eval/speed.py` (latency/TTFT/RTF/concurrency).

---

## Training

The training pipeline is included:

```sh
# encode audio to AudioVAE2 latents once, up front
python training/precompute_latents.py --manifest data/manifest.jsonl --output-dir data/latents

# pretraining
python training/pretrain.py --config training/configs/pretrain.yaml

# SFT stage 1/2 (voice lock, short-utterance coverage)
python training/sft.py --config training/configs/sft_stage1.yaml
```

---

## License

FreyaTTS weights and code are released under the [Apache-2.0](LICENSE) license.

## Acknowledgments

- [VoxCPM2](https://github.com/OpenBMB/VoxCPM) (Apache-2.0) for the AudioVAE2 that FreyaTTS generates into; FreyaTTS reuses it frozen and unchanged
- The flow matching and DiT literature this model builds on

## Citation

```bib
@techreport{freyatts2026,
  title       = {FreyaTTS Technical Report},
  author      = {{Freya Team}},
  institution = {Freya Voice AI},
  year        = {2026},
}
```
