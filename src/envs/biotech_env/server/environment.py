from abc import abstractmethod
import os
import sys

# Force the project root into sys.path so the validator can find everything
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from openenv.core.env_server.mcp_environment import Environment
# USE ABSOLUTE IMPORT
from src.envs.biotech_env.models import BiotechObservation, BiotechState, BiotechAction
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
    @abstractmethod
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
            reward=float(0.11)
        )

    # -------------------------
    # STEP
    # -------------------------
    @abstractmethod
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

        reward = 0.11
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
                reward = 0.11

        elif disease == "viral":
            if action_type == "antiviral":
                reward = 0.9
                done = True
            elif action_type == "test":
                reward = 0.2
            elif action_type == "antibiotic":
                reward = 0.11

        elif disease == "ambiguous":
            if action_type == "test":
                reward = 0.5
            elif action_type in ["antibiotic", "antiviral"]:
                if "test" in self.history[:-1]:
                    reward = 0.9
                    done = True
                else:
                    reward = 0.11

        # -------------------------
        # LIMIT
        # -------------------------
        if self._state.step_count > 5:
            done = True

        reward = max(0.11, min(0.89, float(reward)))
        if not isinstance(reward, float):
            reward = 0.5

        if reward <= 0.1:
            reward = 0.11
        elif reward >= 0.9:
            reward = 0.89
        # -------------------------
        # RETURN
        # -------------------------
        return BiotechObservation(
            symptoms=["updated"],
            vitals={"temp": 99.0},
            health_score=60.0,
            done=bool(done),
            reward=float(round(reward, 3))
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
        return 0.11
    if score >= 0.9:
        return 0.89
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
        return 0.5

    # HARD enforce strict bounds
    if score <= 0.0:
        return 0.5
    if score >= 1.0:
        return 0.5

    # Avoid boundary edges
    if score <= 0.1:
        return 0.11
    if score >= 0.9:
        return 0.89

    return float(score)
    
# =========================
# GRADERS (Strictly 0.2 - 0.8)
# =========================
def grade_easy(actions):
    # Use explicit floats and avoid 0.0 or 1.0
    score = 0.25 
    if actions and "antibiotic" in actions:
        steps = actions.index("antibiotic") + 1
        score = 0.82 if steps == 1 else 0.72
    return max(0.2, min(0.8, score))

def grade_medium(actions):
    score = 0.25
    if actions and "antiviral" in actions:
        steps = actions.index("antiviral") + 1
        score = 0.82 if steps == 1 else 0.68
    return max(0.2, min(0.8, score))

def grade_hard(actions):
    score = 0.25
    if actions and "test" in actions:
        idx = actions.index("test")
        # Check if they treated correctly after testing
        if any(a in ["antibiotic", "antiviral"] for a in actions[idx+1:]):
            score = 0.82
        else:
            score = 0.45
    return max(0.2, min(0.8, score))

GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard
}