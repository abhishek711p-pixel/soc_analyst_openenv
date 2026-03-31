import json
import random
from schemas import SOCAction, Observation, Reward, AlertContext
from typing import Tuple, Dict

class SOCTriageEnv:
    """
    OpenEnv Specification Compliance:
    - Implements step(), reset(), state()
    - Returns typed Pydantic models (Observation, Reward, SOCAction)
    - FEATURES PROCEDURAL THREAT GENERATION AND HUGE JSON DATA STRUCTURES
    """
    def __init__(self):
        self.current_task_id: str = None
        self.state_obs: Observation = None
        self.time_spent: int = 0
        self.max_time: int = 10
        self.done: bool = False
        self.task_data: Dict = {}
        self.action_history: list = []
        
    def _generate_task_data(self, task_id: str) -> Dict:
        malicious_ips = [f"{random.randint(100, 200)}.{random.randint(10, 50)}.{random.randint(1, 255)}.{random.randint(1, 255)}" for _ in range(10)]
        internal_ips = [f"192.168.1.{random.randint(10, 250)}" for _ in range(10)]
        hosts = [f"prod-db-{random.randint(10,99)}", f"workstation-hr-{random.randint(100,999)}", f"file-server-{random.randint(1,5)}"]
        users = ["alice.smith", "bob.jones", "charlie.davis"]
        
        target_ip = random.choice(malicious_ips)
        internal_ip = random.choice(internal_ips)
        target_host = random.choice(hosts)
        target_user = random.choice(users)
        
        task_data = {}
        
        if task_id == "easy":
            task_data["alert"] = AlertContext(
                alert_id=f"TKT-{random.randint(1000, 9999)}",
                severity="LOW",
                description=f"Multiple failed login attempts detected for {target_user}.",
                source_ip=internal_ip,
                affected_host=target_host,
                status="OPEN"
            )
            # Massive JSON logs simulating Windows Event Log
            task_data["logs"] = {
                target_host: json.dumps({
                    "eventContext": {
                        "TargetUserName": target_user,
                        "LogonType": 3,
                        "IpAddress": internal_ip,
                        "Status": "0xC000006D",
                        "SubStatus": "0xC000006A",
                        "AuthenticationPackageName": "NTLM",
                        "WorkstationName": "SCANNER-ENG-01"
                    },
                    "Message": "An account failed to log on. Continuous authentication checks detected from internal vulnerability scanner endpoint.",
                    "syslog_timestamp": "2026-04-06T08:15:30Z"
                }, indent=2),
                internal_ip: json.dumps({"threat_intel": "INTERNAL_SCANNER", "confidence": 0.99, "owner": "IT_AUDIT_TEAM"}, indent=2)
            }
            task_data["user_reply"] = f"Hi, I'm {target_user}. I didn't try to log into {target_host} today."
            task_data["time_limit"] = 10
            
        elif task_id == "medium":
            task_data["alert"] = AlertContext(
                alert_id=f"TKT-{random.randint(1000, 9999)}",
                severity="HIGH",
                description="Suspicious executable downloaded from unknown IP.",
                source_ip=target_ip,
                affected_host=target_host,
                status="OPEN"
            )
            task_data["logs"] = {
                target_host: json.dumps({
                    "process_execution": {
                        "parent": "chrome.exe",
                        "child": "invoice_urgent.exe",
                        "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        "command_line": "invoice_urgent.exe -silent -install"
                    },
                    "network_connections": [{"remote_ip": target_ip, "port": 443, "bytes_out": 4096}]
                }, indent=2),
                target_ip: json.dumps({
                    "threat_intel": "MALICIOUS", 
                    "tags": ["C2", "Botnet"],
                    "geo": "Unknown",
                    "confidence": 0.95
                }, indent=2)
            }
            task_data["sandbox_result"] = json.dumps({
                "verdict": "MALICIOUS",
                "behavior": ["Drops executable in AppData", "Establishes persistence via Registry", f"Connects to C2 at {target_ip}"]
            }, indent=2)
            task_data["user_reply"] = f"Hi, yes I downloaded an invoice earlier from an email. Is everything okay?"
            task_data["time_limit"] = 12
            
        elif task_id == "hard":
            task_data["alert"] = AlertContext(
                alert_id=f"TKT-{random.randint(1000, 9999)}",
                severity="CRITICAL",
                description="Massive outbound data anomalies and rapid internal file modifications.",
                source_ip="UNKNOWN",
                affected_host=target_host,
                status="OPEN"
            )
            task_data["logs"] = {
                target_host: json.dumps({
                    "aws_cloudtrail_sim": {
                        "eventName": "AssumeRole",
                        "userIdentity": {"type": "AssumedRole", "principalId": f"AROAJ52...:{target_user}"},
                        "sourceIPAddress": target_ip,
                        "userAgent": "aws-cli/2.0.30 Python/3.8.3"
                    },
                    "edr_telemetry": {
                        "behavior": "Ransomware_Heuristics",
                        "files_encrypted": 1405,
                        "shadow_copies_deleted": True
                    }
                }, indent=2),
                target_ip: json.dumps({"threat_intel": "CRITICAL THREAT", "tags": ["APT_Group_Zero"], "recent_activity": "Ransomware distribution"}, indent=2)
            }
            task_data["user_reply"] = "I don't know what you're talking about, my laptop just blue-screened."
            task_data["sandbox_result"] = "ERROR: Sandbox analysis timed out. Payload is obfuscated and extremely complex."
            task_data["time_limit"] = 15
            
        return task_data

    def reset(self, task_id: str) -> Observation:
        if task_id == "random":
            task_id = random.choice(["easy", "medium", "hard"])
            
        if task_id not in ["easy", "medium", "hard"]:
            raise ValueError(f"Task {task_id} not found. Must be easy, medium, hard, or random.")
            
        self.current_task_id = task_id
        self.task_data = self._generate_task_data(task_id)
        self.time_spent = 0
        self.max_time = self.task_data["time_limit"]
        self.done = False
        self.action_history = []
        
        self.state_obs = Observation(
            current_alert=self.task_data["alert"].model_copy(),
            available_logs={},
            system_time_remaining=self.max_time,
            last_action_result="Ticket assigned. Environment procedurally generated. Awaiting analyst action."
        )
        return self.state_obs
        
    def state(self) -> Observation:
        return self.state_obs

    def _get_grader_score(self) -> float:
        # Strict 0.0 to 1.0 scoring
        alert = self.state_obs.current_alert
        if self.current_task_id == "easy":
            return 1.0 if alert.status == "FALSE_POSITIVE" else 0.0
        elif self.current_task_id == "medium":
            if alert.status == "RESOLVED":
                return 1.0
            return 0.5 if alert.status == "ESCALATED" else 0.0
        elif self.current_task_id == "hard":
            if alert.status == "ESCALATED":
                return 1.0
            return 0.0
        return 0.0

    def step(self, action: SOCAction) -> Tuple[Observation, Reward, bool, dict]:
        if self.done:
            return self.state_obs, Reward(score=0.0, message="Episode already finished"), True, {}
            
        reward_val = 0.0
        result_msg = ""
        self.time_spent += 1
        self.state_obs.system_time_remaining -= 1
        
        # Action Loop Prevention (Anti-Hallucination mechanism)
        current_action_signature = f"{action.command}_{action.target}"
        if len(self.action_history) > 0 and self.action_history[-1] == current_action_signature:
            reward_val -= 2.0
            result_msg = "WARNING: You repeated the exact same action. Time wasted."
            self.state_obs.system_time_remaining -= 1 # extra penalty
        else:
            reward_val -= 0.1 # Standard time penalty
            
        self.action_history.append(current_action_signature)
        
        # Process Actions
        if action.command == "READ_LOGS":
            target = action.target or self.state_obs.current_alert.affected_host
            if target in self.task_data["logs"]:
                self.state_obs.available_logs[target] = self.task_data["logs"][target]
                result_msg = f"Raw JSON logs retrieved for {target}."
                reward_val += 0.2
            else:
                result_msg = f"No logs found for {target}."
                
        elif action.command == "CHECK_IP_REPUTATION":
            target = action.target or self.state_obs.current_alert.source_ip
            if target in self.task_data["logs"]:
                self.state_obs.available_logs[target] = self.task_data["logs"][target]
                result_msg = f"Threat Intel retrieved for {target}."
                reward_val += 0.2
            else:
                result_msg = f"No known intel on {target}."
                
        elif action.command == "RUN_MALWARE_SANDBOX":
            target = action.target or self.state_obs.current_alert.affected_host
            self.state_obs.system_time_remaining -= 2 # Sandbox takes much more time
            if "sandbox_result" in self.task_data:
                self.state_obs.available_logs["sandbox_analysis"] = self.task_data["sandbox_result"]
                result_msg = f"Sandbox execution completed. Detailed artifact analysis appended to logs."
                reward_val += 0.5
            else:
                result_msg = "No artifact to sandbox."
                
        elif action.command == "EMAIL_USER":
            if "user_reply" in self.task_data:
                self.state_obs.available_logs["user_communication"] = self.task_data["user_reply"]
                result_msg = "User replied to automated ticketing ping. Check logs for communication."
                reward_val += 0.2
            else:
                result_msg = "User did not reply."

        elif action.command == "BLOCK_IP":
            result_msg = f"IP {action.target} blocked at firewall."
            # High reward for blocking the malicious IP generated randomly
            if self.current_task_id == "medium" and action.target == self.task_data["alert"].source_ip:
                reward_val += 0.5
                
        elif action.command == "QUARANTINE_HOST":
            result_msg = f"Host {action.target} quarantined from network."
            if self.current_task_id == "hard" and action.target == self.task_data["alert"].affected_host:
                reward_val += 1.0
                
        elif action.command == "CLOSE_FALSE_POSITIVE":
            self.state_obs.current_alert.status = "FALSE_POSITIVE"
            self.done = True
            result_msg = "Ticket closed as false positive."
            if self.current_task_id == "easy":
                reward_val += 2.0
            else:
                reward_val -= 5.0 
                
        elif action.command == "CLOSE_RESOLVED":
            self.state_obs.current_alert.status = "RESOLVED"
            self.done = True
            result_msg = "Ticket closed as resolved."
            if self.current_task_id == "medium":
                reward_val += 2.0
            else:
                reward_val -= 5.0
                
        elif action.command == "ESCALATE_TIER_2":
            self.state_obs.current_alert.status = "ESCALATED"
            self.done = True
            result_msg = "Ticket escalated to Tier 2."
            if self.current_task_id == "hard":
                reward_val += 2.0
            else:
                reward_val -= 1.0 
                
        if self.state_obs.system_time_remaining <= 0 and not self.done:
            self.done = True
            result_msg += " SLA Breach! Time ran out before resolution."
            reward_val -= 5.0
            
        self.state_obs.last_action_result = result_msg
        
        info = {}
        if self.done:
            score = self._get_grader_score()
            info["grader_score"] = score
            self.state_obs.last_action_result += f" | Episode Done. Final Grader Score: {score}"
            
        return self.state_obs, Reward(score=reward_val, message=result_msg), self.done, info
