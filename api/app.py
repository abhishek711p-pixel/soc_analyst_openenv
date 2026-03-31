from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sys
import os

# Ensure the root directory is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.env import SOCTriageEnv
from src.schemas import SOCAction, Observation, Reward

app = FastAPI(title="Tier 1 SOC Analyst Alert Triage OpenEnv", default_response_class=ORJSONResponse)
env_instance = SOCTriageEnv()

# Mounting the templates directory as static for CSS/JS
app.mount("/static", StaticFiles(directory="api/templates"), name="static")
templates = Jinja2Templates(directory="api/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/reset/{task_id}")
def reset(task_id: str):
    obs = env_instance.reset(task_id)
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
