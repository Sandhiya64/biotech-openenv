import os
import sys
from abc import abstractmethod
import random

# Absolute path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from openenv.core.env_server.mcp_environment import Environment
# FIX: Absolute import
from src.envs.biotech_env.models import (
    BiotechObservation,
    BiotechState,
    BiotechAction,
)
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

    def reset(self, task_name="easy"):
        task = TASKS.get(task_name, TASKS["easy"])

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
            reward=0.115 + random.uniform(-0.004, 0.004)  # Add variation
        )

    def step(self, action):

        if self._state is None:
            return self.reset()

        # Extract action safely
        if isinstance(action, dict):
            action_type = action.get("action_type", "wait")
        elif hasattr(action, "action_type"):
            action_type = action.action_type
        else:
            action_type = "wait"

        if action_type not in ["antibiotic", "antiviral", "test", "wait"]:
            action_type = "wait"

        self.history.append(action_type)
        self._state.step_count += 1

        reward = 0.115
        done = False

        disease = self._state.disease

 
        if disease == "bacterial":
            if action_type == "antibiotic":
                # Add variation to rewards too
                reward = 0.895 + random.uniform(-0.004, 0.004)
                done = True

        elif disease == "viral":
            if action_type == "antiviral":
                reward = 0.895 + random.uniform(-0.004, 0.004)
                done = True

        elif disease == "ambiguous":
            if action_type == "test":
                reward = 0.505 + random.uniform(-0.004, 0.004)
            elif action_type in ["antibiotic", "antiviral"]:
                if "test" in self.history[:-1]:
                    reward = 0.895 + random.uniform(-0.004, 0.004)
                    done = True
        
        # Default reward with variation
        else:
            reward = 0.115 + random.uniform(-0.004, 0.004)
        
        return BiotechObservation(
            symptoms=["updated"],
            vitals={"temp": 99.0},
            health_score=60.0,
            done=done,
            reward=float(reward)
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
# SAFE CLAMP
# =========================
def clamp(score):
    try:
        score = float(score)
    except:
        return 0.5  # safe fallback

    # STRICTLY inside (0,1)
    if score <= 0.1:
        return 0.115
    if score >= 0.9:
        return 0.895
    return score

def extract_actions(data):
    try:
        if not isinstance(data, list):
            return []

        actions = []

        for item in data:

            # Case 1: direct string
            if isinstance(item, str):
                actions.append(item)

            # Case 2: dict with action_type
            elif isinstance(item, dict):

                # Direct
                if "action_type" in item:
                    actions.append(item["action_type"])

                # Nested (trajectory format)
                elif "action" in item:
                    action_obj = item["action"]

                    if isinstance(action_obj, dict):
                        actions.append(action_obj.get("action_type", "wait"))

                    elif hasattr(action_obj, "action_type"):
                        actions.append(getattr(action_obj, "action_type", "wait"))

                    else:
                        actions.append("wait")

                else:
                    actions.append("wait")

            # Case 3: object
            elif hasattr(item, "action_type"):
                actions.append(getattr(item, "action_type", "wait"))

            else:
                actions.append("wait")

        return actions

    except:
        return []
    
def safe_return(score):
    try:
        score = float(score)
    except:
        return 0.55

    # HARD enforce strict bounds
    if score <= 0.0:
        return 0.55
    if score >= 1.0:
        return 0.55

    # Avoid boundary edges
    if score <= 0.1:
        return 0.115
    if score >= 0.9:
        return 0.895

    return float(score)
    
# =========================
# GRADERS (Strictly 0.2 - 0.8)
# =========================
def grade_easy(actions):
    # Base score
    if actions and "antibiotic" in actions:
        steps = actions.index("antibiotic") + 1
        if steps == 1:
            base_score = 0.815
        else:
            base_score = 0.715
    else:
        base_score = 0.245
    
    # Add random variation between -0.005 and +0.005
    variation = random.uniform(-0.004, 0.004)
    score = base_score + variation
    
    # Ensure strictly between 0 and 1
    return max(0.005, min(0.995, score))

def grade_medium(actions):
    if actions and "antiviral" in actions:
        steps = actions.index("antiviral") + 1
        if steps == 1:
            base_score = 0.815
        else:
            base_score = 0.675
    else:
        base_score = 0.245
    
    variation = random.uniform(-0.004, 0.004)
    score = base_score + variation
    return max(0.005, min(0.995, score))

def grade_hard(actions):
    if actions and "test" in actions:
        test_index = actions.index("test")
        if any(a in ["antibiotic", "antiviral"] for a in actions[test_index+1:]):
            base_score = 0.815
        else:
            base_score = 0.445
    else:
        base_score = 0.245
    
    variation = random.uniform(-0.004, 0.004)
    score = base_score + variation
    return max(0.005, min(0.995, score))

GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}