from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict

class AlertContext(BaseModel):
    alert_id: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    description: str
    source_ip: Optional[str] = None
    affected_host: Optional[str] = None
    status: Literal["OPEN", "INVESTIGATING", "ESCALATED", "RESOLVED", "FALSE_POSITIVE"]

class Observation(BaseModel):
    current_alert: AlertContext
    available_logs: Dict[str, str] = Field(default_factory=dict, description="Logs retrieved by the agent")
    system_time_remaining: int = Field(..., description="Time left before SLA breach or system compromise")
    last_action_result: str = Field(..., description="Feedback from the last tool executed")

class SOCAction(BaseModel):
    command: Literal[
        "READ_LOGS", 
        "CHECK_IP_REPUTATION", 
        "QUARANTINE_HOST", 
        "BLOCK_IP", 
        "RUN_MALWARE_SANDBOX",
        "EMAIL_USER",
        "CLOSE_FALSE_POSITIVE", 
        "CLOSE_RESOLVED",
        "ESCALATE_TIER_2"
    ] = Field(..., description="The action to take")
    target: Optional[str] = Field(None, description="The IP address or hostname to target, if applicable")
    reason: str = Field(..., description="Justification for the action")

class Reward(BaseModel):
    score: float = Field(..., description="The reward value")
    message: str = Field(..., description="Explanation of the reward")
