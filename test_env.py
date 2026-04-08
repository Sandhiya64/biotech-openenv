import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from envs.biotech_env.server.environment import BiotechEnvironment
from models import BiotechAction

env = BiotechEnvironment()

print("\n=== TESTING RESET ===")
obs = env.reset("easy")
print(obs)

print("\n=== TESTING STEP ===")
action = BiotechAction(action_type="antibiotic")
obs = env.step(action)
print(obs)