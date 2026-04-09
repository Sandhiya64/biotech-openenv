import json
from src.envs.biotech_env.server.environment import BiotechEnvironment


def get_action(obs, task):
    """Rule-based policy (NO API CALLS)"""

    if task == "easy":
        return "antibiotic"

    elif task == "medium":
        return "antiviral"

    elif task == "hard":
        # Proper sequence logic
        if "test_done" not in obs.get("history", []):
            return "test"
        elif "bacterial" in obs.get("diagnosis", ""):
            return "antibiotic"
        else:
            return "antiviral"

    return "wait"


def run_task(env, task):
    print(f"[START] Task: {task}")

    obs = env.reset()
    done = False

    while not done:
        action = get_action(obs, task)
        print(f"[STEP] Action: {action}")

        obs = env.step(action)

        done = obs["done"]

    print(f"[END] Task: {task} | Final Reward: {obs['reward']}\n")


def main():
    try:
        env = BiotechEnvironment()

        for task in ["easy", "medium", "hard"]:
            run_task(env, task)

    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main()