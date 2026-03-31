import random
import traceback
from env import SOCTriageEnv
from schemas import SOCAction

def advanced_fuzzing_test():
    print("==================================================")
    print("🚀 INITIATING ADVANCED STOCHASTIC FUZZING TEST 🚀")
    print("==================================================\n")
    print("This suite acts as an unhinged, semi-random AI Agent. It will fire 100 chaotic, unpredictable combinations of commands at the 'hard' scenario to ensure the state machine never crashes and mathematically protects the RL time boundaries.\n")

    env = SOCTriageEnv()
    obs = env.reset("hard")
    
    # Extract possible targets to mix with garbage targets
    valid_host = obs.current_alert.affected_host
    valid_ip = obs.current_alert.source_ip
    garbage_targets = [None, "127.0.0.1", "UNKNOWN", "random_string_1234", valid_host, valid_ip]
    
    available_commands = [
        "READ_LOGS", "CHECK_IP_REPUTATION", "QUARANTINE_HOST", "BLOCK_IP",
        "RUN_MALWARE_SANDBOX", "EMAIL_USER", "CLOSE_FALSE_POSITIVE",
        "CLOSE_RESOLVED", "ESCALATE_TIER_2"
    ]

    total_steps = 0
    crashes = 0
    
    # We force 100 steps to test SLA Breach and "Zombie AI" defenses
    for i in range(1, 101):
        rand_cmd = random.choice(available_commands)
        rand_tgt = random.choice(garbage_targets)
        
        action = SOCAction(
            command=rand_cmd,
            target=rand_tgt,
            reason=f"Fuzz iteration {i}"
        )
        
        try:
            obs, reward, done, info = env.step(action)
            total_steps += 1
            
            # Print a few samples sequentially so we can see the chaos
            if i <= 3 or i == 50 or i == 100:
                print(f"[Step {i:03d}] Command: {rand_cmd}({rand_tgt}) | Done: {done} | Time Remaining: {obs.system_time_remaining}")
                print(f"   -> Reward: {reward.score:.2f} | Message: {reward.message}\n")
                
        except Exception as e:
            print(f"❌ CRITICAL STATE CRASH AT STEP {i}: {e}")
            traceback.print_exc()
            crashes += 1
            break

    print("==================================================")
    print("📊 FUZZING TEST RESULTS 📊")
    print("==================================================")
    print(f"Total Steps Handled: {total_steps}")
    print(f"Mathematical Limit Maintained (Did time breach SLA properly?): {'YES' if obs.system_time_remaining <= 0 and done else 'NO'}")
    print(f"Total Framework Crashes: {crashes}")
    
    if crashes == 0 and done:
        print("\n✅ VERDICT: State Machine is BULLETPROOF. ZERO CRASHES.")
    else:
        print("\n❌ VERDICT: Environment requires hardening.")

if __name__ == "__main__":
    advanced_fuzzing_test()
