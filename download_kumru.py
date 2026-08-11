import os
import urllib.request

model_dir = "kumru_model"
os.makedirs(model_dir, exist_ok=True)
url = "https://huggingface.co/icecubetr/Kumru-2B-GGUF/resolve/main/kumru-2b-Q4_K_M.gguf"
model_path = os.path.join(model_dir, "kumru-2b-Q4_K_M.gguf")

if not os.path.exists(model_path):
    print(f"Downloading {url} to {model_path}...")
    urllib.request.urlretrieve(url, model_path)
    print("Download complete.")
else:
    print("Model already exists.")
