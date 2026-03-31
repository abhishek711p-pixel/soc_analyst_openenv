import os
import json
from openai import OpenAI
from env import SOCTriageEnv
from schemas import SOCAction

# Hackathon Mandatory Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def run_inference(task_id: str):
    print(f"\n{'='*50}\n--- Running Inference for Task: {task_id.upper()} ---\n{'='*50}")
    
    if not API_KEY:
        print("Set HF_TOKEN or API_KEY environment variable. Running in mock heuristic baseline mode.")
        return mock_inference(task_id)
        
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = SOCTriageEnv()
    obs = env.reset(task_id)
    
    done = False
    step_count = 0
    total_reward = 0.0
    info = {}
    
    while not done:
        print(f"\n[Step {step_count}] Current State: {obs.model_dump_json(indent=2)}")
        
        system_prompt = (
            "You are an AI SOC Analyst. Read the current OpenEnv Observation. "
            "Output ONLY a valid JSON object matching the SOCAction Pydantic schema. "
            "Valid commands: READ_LOGS, CHECK_IP_REPUTATION, QUARANTINE_HOST, BLOCK_IP, RUN_MALWARE_SANDBOX, EMAIL_USER, CLOSE_FALSE_POSITIVE, CLOSE_RESOLVED, ESCALATE_TIER_2."
        )
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": obs.model_dump_json()}
                ]
            )
            response_text = response.choices[0].message.content or ""
            action_data = json.loads(response_text)
            action = SOCAction(**action_data)
        except Exception as e:
            print(f"Agent generated invalid action schema: {e}. Escalating mechanically to prevent infinite loop.")
            action = SOCAction(command="ESCALATE_TIER_2", target=None, reason="Fallback due to parsing error.")
            
        print(f"-> Agent Action: {action.command} | Target: {action.target} | Reason: {action.reason}")
        
        obs, reward, done, info = env.step(action)
        total_reward += reward.score
        print(f"<- Reward: {reward.score} | Msg: {reward.message}")
        step_count += 1
        
        if step_count > 10:
            print("Force stopping to prevent infinite loop.")
            break
            
    print(f"\n--- Task {task_id.upper()} Completed ---")
    print(f"Total Trajectory Reward: {total_reward}")
    if "grader_score" in info:
        print(f"Final Grader Score: {info['grader_score']} / 1.0")

def mock_inference(task_id: str):
    env = SOCTriageEnv()
    obs = env.reset(task_id)
    info = {}
    
    if task_id == "easy":
        actions = [
            SOCAction(command="EMAIL_USER", target=obs.current_alert.affected_host, reason="Ask user about failed logins"),
            SOCAction(command="READ_LOGS", target=obs.current_alert.affected_host, reason="Check login attempts"),
            SOCAction(command="CLOSE_FALSE_POSITIVE", target=None, reason="Internal scanner")
        ]
    elif task_id == "medium":
        actions = [
            SOCAction(command="CHECK_IP_REPUTATION", target=obs.current_alert.source_ip, reason="Check threat intel"),
            SOCAction(command="RUN_MALWARE_SANDBOX", target=obs.current_alert.affected_host, reason="Sandbox executable"),
            SOCAction(command="BLOCK_IP", target=obs.current_alert.source_ip, reason="Blocking malicious IP"),
            SOCAction(command="CLOSE_RESOLVED", target=None, reason="IP blocked")
        ]
    else:
        actions = [
            SOCAction(command="READ_LOGS", target=obs.current_alert.affected_host, reason="Investigate traffic"),
            SOCAction(command="RUN_MALWARE_SANDBOX", target=obs.current_alert.affected_host, reason="Detonate payload"),
            SOCAction(command="QUARANTINE_HOST", target=obs.current_alert.affected_host, reason="Quarantining host"),
            SOCAction(command="ESCALATE_TIER_2", target=None, reason="Escalating complex ransomware")
        ]
        
    for act in actions:
        print(f"\n-> Action: {act.command} | Target: {act.target}")
        obs, reward, done, info = env.step(act)
        print(f"<- Reward: {reward.score} | Msg: {reward.message}")
        if done:
            break
            
    print(f"--- Task {task_id.upper()} Completed ---")
    if "grader_score" in info:
         print(f"Final Grader Score: {info['grader_score']} / 1.0")

if __name__ == "__main__":
    for t in ["easy", "medium", "hard"]:
        run_inference(t)
