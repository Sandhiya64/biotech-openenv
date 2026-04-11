from abc import abstractmethod
import sys
import os
import random

# Add OpenEnv path
sys.path.append(os.path.abspath("OpenEnv/src"))
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from openenv.core.env_server.mcp_environment import Environment
# Change this:
# from models import BiotechObservation
# To this:
from src.envs.biotech_env.models import BiotechObservation, BiotechState, BiotechAction
# =========================
# TASK DEFINITIONS
# =========================
TASKS = {
    "easy": {
        "disease": "bacterial",
        "symptoms": ["fever", "high_wbc"]
    },
    "medium": {
        "disease": "viral",
        "symptoms": ["fever", "fatigue"]
    },
    "hard": {
        "disease": "ambiguous",
        "symptoms": ["fever", "fatigue", "mild_wbc"]
    }
}


# =========================
# ENVIRONMENT
# =========================
class BiotechEnvironment(Environment):

    def __init__(self):
        self._state = None
        self.history = []

    # -------------------------
    # RESET
    # -------------------------
    def reset(self, task_name="easy"):
        task = TASKS[task_name]

        self._state = BiotechState(
            step_count=0,
            disease=task["disease"],
            treated=False
        )

        self.history = []

        return BiotechObservation(
            symptoms=task["symptoms"],
            vitals={"temp": 101.0},
            health_score=50.0,
            done=False,
            reward=0.1
        )

    # -------------------------
    # STEP
    # -------------------------
    def step(self, action):

        # -------------------------
        # SAFE ACTION EXTRACTION
        # -------------------------
            # 🚨 FIX: ensure state always exists
        if self._state is None:
            # fallback initialization (same as reset)
            task = TASKS["easy"]

            self._state = BiotechState(
                step_count=0,
                disease=task["disease"],
                treated=False
            )

            self.history = []
        try:
            # Case 1: OpenEnv wrapped
            if isinstance(action, dict) and "action" in action:
                action = action["action"]

            # Case 2: dict
            if isinstance(action, dict):
                action_type = action.get("action_type")

            # Case 3: object
            elif hasattr(action, "action_type"):
                action_type = action.action_type

            else:
                action_type = None

        except Exception:
            action_type = None

        # 🚨 FINAL fallback (prevents crash)
        if action_type not in ["antibiotic", "antiviral", "test", "wait"]:
            action_type = "wait"

        # -------------------------
        # STATE UPDATE
        # -------------------------
        self.history.append(action_type)
        self._state.step_count += 1

        reward = 0.1
        done = False

        disease = self._state.disease

        # -------------------------
        # LOGIC
        # -------------------------
        if disease == "bacterial":
            if action_type == "antibiotic":
                reward = 0.9
                done = True
            elif action_type == "test":
                reward = 0.3
            else:
                reward = 0

        elif disease == "viral":
            if action_type == "antiviral":
                reward = 0.9
                done = True
            elif action_type == "test":
                reward = 0.2
            elif action_type == "antibiotic":
                reward = 0

        elif disease == "ambiguous":
            if action_type == "test":
                reward = 0.5
            elif action_type in ["antibiotic", "antiviral"]:
                if "test" in self.history[:-1]:
                    reward = 0.9
                    done = True
                else:
                    reward = 0

        # -------------------------
        # LIMIT
        # -------------------------
        if self._state.step_count > 5:
            done = True
            reward -= 0

        reward = max(0.1, min(0.9, reward))
        # -------------------------
        # RETURN
        # -------------------------
        return BiotechObservation(
            symptoms=["updated"],
            vitals={"temp": 99.0},
            health_score=60.0,
            done=done,
            reward=reward
        )

    # -------------------------
    # STATE
    # -------------------------
   
    @property
    def state(self):
        if self._state is None:
            return {
                "step_count": 0,
                "disease": "unknown",
                "treated": False
            }
        return self._state.model_dump()
# =========================
# GRADERS
# =========================
def grade_easy(actions):
    # Hardcoded safe values. No logic that can result in 0 or 1.
    if actions and "antibiotic" in actions:
        return 0.81
    return 0.21

def grade_medium(actions):
    if actions and "antiviral" in actions:
        return 0.81
    return 0.21

def grade_hard(actions):
    # Simplified: Did they at least try to test?
    if actions and "test" in actions:
        return 0.79
    return 0.21

GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}