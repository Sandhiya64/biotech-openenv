from src.envs.biotech_env.server.environment import (
    BiotechEnvironment,
    grade_easy,
    grade_medium,
    grade_hard
)

TASKS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}

VALID_ACTIONS = ["antibiotic", "antiviral", "test", "wait"]


def simulate_agent(task):
    """
    Simulates evaluator calling your env + actions
    """
    env = BiotechEnvironment()
    obs = env.reset(task)

    actions = []
    done = False
    steps = 0

    while not done and steps < 5:
        # Simulate evaluator / random agent
        action = VALID_ACTIONS[steps % len(VALID_ACTIONS)]

        actions.append(action)

        obs = env.step({"action_type": action})
        done = obs.done
        steps += 1

    return actions


def validate_task(task, grader):
    actions = simulate_agent(task)

    print(f"\n[TEST] {task}")
    print(f"Actions: {actions}")

    score = grader(actions)

    print(f"Score: {score}")

    # 🔥 CRITICAL VALIDATION (same as evaluator)
    assert isinstance(score, float), "Score is not float"
    assert 0 < score < 1, f"Score out of range: {score}"

    return True


def main():
    for task, grader in TASKS.items():
        validate_task(task, grader)

    print("\n✅ ALL TASKS PASSED VALIDATION")


if __name__ == "__main__":
    main()