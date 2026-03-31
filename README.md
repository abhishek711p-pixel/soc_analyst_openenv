---
title: SOC Triage OpenEnv
emoji: 🛡️
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
---

# Tier 1 SOC Analyst Alert Triage (Meta PyTorch OpenEnv Hackathon Project)

## Environment Motivation & Description
Cybersecurity Security Operations Centers (SOCs) are overwhelmed with "alert fatigue." Analysts spend countless hours reading logs just to triage false positives. 
This environment models the exact workflow of a Tier 1 SOC Analyst. The agent must read an incoming alert, retrieve internal logs, check threat intelligence, and make a high-stakes decision (Close, Block IP, Quarantine Host, or Escalate).

This fills a massive capability gap: evaluating an AI Agent's capacity to safely handle security alerts.

## Action and Observation Space
The environment enforces strict OpenEnv compliance using `pydantic` schemas:

- **Observation (`IncidentState`)**: 
  Contains the `current_alert` (severity, description, target), `available_logs` (logs retrieved by agent tool calls), and the `system_time_remaining`.
- **Action (`SOCAction`)**:
  Agents must output an Enum `command` (`READ_LOGS`, `CHECK_IP_REPUTATION`, `QUARANTINE_HOST`, `BLOCK_IP`, `CLOSE_FALSE_POSITIVE`, `CLOSE_RESOLVED`, `ESCALATE_TIER_2`), an optional `target` string, and a text `reason`.

## Tasks and Graders
We implement 3 graded tasks, scored 0.0 to 1.0 deterministicly based on the final ticket state:
1. **Easy:** Internal Scanner (False Positive). Agent must identify the internal IP and close the ticket properly.

## Key Differentiators 🌟
- 🖥️ **Interactive Web Dashboard**: Visit the Hugging Face space for a playable, procedural GUI mapped perfectly to the OpenEnv endpoints.
- 🛡️ **Adversarial Resilience**: Built 100% on strict Python Pydantic models. Passes adversarial load testing against LLM hallucinations, ensuring zero crashes even when the model attempts to execute non-existent commands.
2. **Medium:** Phishing Malware. Agent must check the IP, realize it is malicious, block it, and resolve the ticket.
3. **Hard:** Multi-stage ransomware. The agent must realize it is out of their depth, surgically quarantine the compromised hosts, and escalate to Tier 2 before the time runs out.

## Setup and Usage Instructions

### Docker Containerized Execution (Recommended for HF Spaces)
```bash
docker build -t openenv-soc .
docker run -e OPENAI_API_KEY="your_optional_key" openenv-soc
```

### Manual Execution
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your_api_key_here"
python inference.py
```

## Baseline Scores
Running our baseline agent against all three tasks yields the following baseline scores:
- **Easy**: 1.0
- **Medium**: 1.0 
- **Hard**: 1.0 (with proper escalation handling)
