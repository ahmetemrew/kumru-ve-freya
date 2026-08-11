import os
import uuid
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from freyatts import FreyaTTS
from typing import Optional

app = FastAPI(title="Voice Assistant with Kumru 2B & FreyaTTS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading FreyaTTS on {device}...")
tts = FreyaTTS.from_pretrained("freyavoice/freya-tts", device=device)
print("FreyaTTS loaded.")

try:
    from llama_cpp import Llama
    print("Loading Kumru 2B model...")
    model_path = "kumru_model/kumru-2b-Q4_K_M.gguf"
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_gpu_layers=-1
    )
    print("Kumru model loaded.")
except Exception as e:
    print(f"Warning: Could not load Kumru model: {e}")
    llm = None

os.makedirs("temp_audio", exist_ok=True)

def remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: list[Message]
    seed: Optional[int] = None
    steps: int = 32

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest, background_tasks: BackgroundTasks):
    if not req.history:
        raise HTTPException(status_code=400, detail="History cannot be empty")
    
    if llm is None:
        raise HTTPException(status_code=500, detail="Kumru model is still downloading or not loaded.")
        
    try:
        # Kara-Kumru, Llama-3 chat template'ini kullanır
        prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nSen yardımsever bir asistansın.<|eot_id|>"
        recent_history = req.history[-10:]
        
        for msg in recent_history:
            role = "user" if msg.role == "user" else "assistant"
            prompt += f"<|start_header_id|>{role}<|end_header_id|>\n{msg.content}<|eot_id|>"
            
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n"
        
        response = llm(
            prompt,
            max_tokens=150,
            stop=["<|eot_id|>", "<|end_of_text|>"],
            echo=False
        )
        
        ai_text = response['choices'][0]['text'].strip()
        
        # Synthesis
        kwargs = {"steps": req.steps, "seed": 42} # Sabit ses kimliği (Seed)
            
        wav = tts.synthesize(ai_text, **kwargs)
        filename = f"temp_audio/{uuid.uuid4().hex}.wav"
        tts.save_wav(wav, filename)
        
        return {"text": ai_text, "audio_url": f"/api/audio/{os.path.basename(filename)}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/{filename}")
def get_audio(filename: str, background_tasks: BackgroundTasks):
    filepath = os.path.join("temp_audio", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio not found")
    
    background_tasks.add_task(remove_file, filepath)
    return FileResponse(filepath, media_type="audio/wav")

app.mount("/", StaticFiles(directory="ui_voice", html=True), name="ui_voice")

if __name__ == "__main__":
    import webbrowser
    print("Starting Voice Assistant at http://127.0.0.1:8001")
    webbrowser.open("http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
