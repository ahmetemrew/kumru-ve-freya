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

app = FastAPI(title="Freya TTS Web App")
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
print("Model loaded.")

os.makedirs("temp_audio", exist_ok=True)

def remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass

from typing import Optional
class SynthesizeRequest(BaseModel):
    text: str
    steps: int = 32
    seed: Optional[int] = None

@app.post("/api/synthesize")
def synthesize(req: SynthesizeRequest, background_tasks: BackgroundTasks):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        kwargs = {"steps": req.steps}
        if req.seed is not None:
            kwargs["seed"] = req.seed
            
        wav = tts.synthesize(req.text, **kwargs)
        filename = f"temp_audio/{uuid.uuid4().hex}.wav"
        tts.save_wav(wav, filename)
        
        background_tasks.add_task(remove_file, filename)
        return FileResponse(filename, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")

if __name__ == "__main__":
    import webbrowser
    print("Starting server at http://127.0.0.1:8000")
    webbrowser.open("http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
