from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sys
import os
import traceback

# Ensure the current directory is on the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from env import SOCTriageEnv
from schemas import SOCAction, Observation, Reward

app = FastAPI(title="Tier 1 SOC Analyst Alert Triage OpenEnv")

# --- Error Handling ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"INTERNAL_SERVER_ERROR: {str(exc)}\n{traceback.format_exc()}"
    print(error_msg) # Log to stdout for HF logs
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "trace": traceback.format_exc()}
    )

env_instance = SOCTriageEnv()

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.1.0"}

# --- Routes ---

# Mounting the templates directory as static for CSS/JS
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/reset/{task_id}")
def reset_with_id(task_id: str):
    obs = env_instance.reset(task_id)
    return obs.model_dump()

@app.post("/reset")
def reset_default():
    obs = env_instance.reset("random")
    return obs.model_dump()

@app.post("/step")
def step(action: SOCAction):
    obs, reward, done, info = env_instance.step(action)
    return {
        "observation": obs.model_dump(), 
        "reward": reward.model_dump(), 
        "done": done, 
        "info": info
    }

@app.get("/state")
def state():
    return env_instance.state().model_dump()

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
