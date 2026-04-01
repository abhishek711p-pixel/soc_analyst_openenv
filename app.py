from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sys
import os

# Ensure the current directory is on the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from env import SOCTriageEnv
from schemas import SOCAction, Observation, Reward

app = FastAPI(title="Tier 1 SOC Analyst Alert Triage OpenEnv")
env_instance = SOCTriageEnv()

# Mounting the templates directory as static for CSS/JS
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/reset/{task_id}")
def reset_with_id(task_id: str):
    obs = env_instance.reset(task_id)
    return obs

@app.post("/reset")
def reset_default():
    obs = env_instance.reset("random")
    return obs

@app.post("/step")
def step(action: SOCAction):
    obs, reward, done, info = env_instance.step(action)
    return {"observation": obs, "reward": reward, "done": done, "info": info}

@app.get("/state")
def state():
    return env_instance.state()

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
