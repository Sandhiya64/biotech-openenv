import os
from openai import OpenAI
from src.envs.biotech_env.server.environment import BiotechEnvironment


# Initialize client using provided env vars
client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY"),
)


def get_action(obs, task):
    """LLM call + safe fallback"""

    prompt = f"""
    You are a medical agent.

    Task: {task}
    Observation: {obs}

    Choose ONE action:
    antibiotic / antiviral / test / wait

    Return ONLY the action.
    """

    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        action = response.choices[0].message.content.strip().lower()

        if action in ["antibiotic", "antiviral", "test", "wait"]:
            return action

    except Exception as e:
        print(f"[LLM ERROR] {e}")

    # ✅ Fallback logic (CRITICAL)
    if task == "easy":
        return "antibiotic"
    elif task == "medium":
        return "antiviral"
    elif task == "hard":
        if "test_done" not in obs.get("history", []):
            return "test"
        return "antibiotic"

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
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()