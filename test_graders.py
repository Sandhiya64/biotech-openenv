#!/usr/bin/env python3
"""
Test script to check exact scores being returned by graders
"""

import sys
import os

# Add the correct path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your grader functions
from src.envs.biotech_env.server.environment import grade_easy, grade_medium, grade_hard

# Also import the environment to test step rewards
from src.envs.biotech_env.server.environment import BiotechEnvironment

def test_graders():
    """Test each grader with different action sequences"""
    
    print("=" * 60)
    print("TESTING GRADERS")
    print("=" * 60)
    
    # Test grade_easy
    print("\n--- grade_easy ---")
    test_cases = [
        (["antibiotic"], "Perfect - antibiotic on first try"),
        (["test", "antibiotic"], "Good - antibiotic after test"),
        (["antiviral"], "Wrong treatment"),
        (["wait", "wait", "antibiotic"], "Delayed antibiotic"),
        ([], "No actions"),
    ]
    
    for actions, description in test_cases:
        score = grade_easy(actions)
        print(f"  {description}:")
        print(f"    Actions: {actions}")
        print(f"    Score: {score:.6f}")
        print(f"    Type: {type(score)}")
        print()
    
    # Test grade_medium
    print("\n--- grade_medium ---")
    test_cases = [
        (["antiviral"], "Perfect - antiviral on first try"),
        (["test", "antiviral"], "Good - antiviral after test"),
        (["antibiotic"], "Wrong treatment"),
        (["wait", "wait", "antiviral"], "Delayed antiviral"),
        ([], "No actions"),
    ]
    
    for actions, description in test_cases:
        score = grade_medium(actions)
        print(f"  {description}:")
        print(f"    Actions: {actions}")
        print(f"    Score: {score:.6f}")
        print()
    
    # Test grade_hard
    print("\n--- grade_hard ---")
    test_cases = [
        (["test", "antibiotic"], "Perfect - test then treat"),
        (["test", "antiviral"], "Perfect - test then treat"),
        (["antibiotic"], "Treat without test"),
        (["test", "wait", "antibiotic"], "Test then delayed treat"),
        ([], "No actions"),
    ]
    
    for actions, description in test_cases:
        score = grade_hard(actions)
        print(f"  {description}:")
        print(f"    Actions: {actions}")
        print(f"    Score: {score:.6f}")
        print()

def test_step_rewards():
    """Test the step() method rewards"""
    
    print("\n" + "=" * 60)
    print("TESTING STEP REWARDS")
    print("=" * 60)
    
    env = BiotechEnvironment()
    
    # Test easy task (bacterial)
    print("\n--- Easy Task (Bacterial) ---")
    obs = env.reset("easy")
    print(f"  Initial reward: {obs.reward}")
    
    # Test antibiotic (should give high reward)
    obs = env.step({"action_type": "antibiotic"})
    print(f"  After antibiotic: reward={obs.reward}, done={obs.done}")
    
    # Reset and test wrong action
    env = BiotechEnvironment()
    obs = env.reset("easy")
    obs = env.step({"action_type": "antiviral"})
    print(f"  After antiviral (wrong): reward={obs.reward}, done={obs.done}")
    
    # Test medium task (viral)
    print("\n--- Medium Task (Viral) ---")
    env = BiotechEnvironment()
    obs = env.reset("medium")
    print(f"  Initial reward: {obs.reward}")
    
    obs = env.step({"action_type": "antiviral"})
    print(f"  After antiviral: reward={obs.reward}, done={obs.done}")
    
    # Test hard task (ambiguous)
    print("\n--- Hard Task (Ambiguous) ---")
    env = BiotechEnvironment()
    obs = env.reset("hard")
    print(f"  Initial reward: {obs.reward}")
    
    obs = env.step({"action_type": "test"})
    print(f"  After test: reward={obs.reward}, done={obs.done}")
    
    obs = env.step({"action_type": "antibiotic"})
    print(f"  After antibiotic (post-test): reward={obs.reward}, done={obs.done}")

def test_multiple_runs():
    """Test multiple runs to see score variation"""
    
    print("\n" + "=" * 60)
    print("TESTING MULTIPLE RUNS (Randomization check)")
    print("=" * 60)
    
    # Run grade_easy multiple times with same input
    actions = ["antibiotic"]
    print(f"\nRunning grade_easy 10 times with actions={actions}:")
    scores = []
    for i in range(10):
        score = grade_easy(actions)
        scores.append(score)
        print(f"  Run {i+1}: {score:.6f}")
    
    print(f"\n  Min: {min(scores):.6f}")
    print(f"  Max: {max(scores):.6f}")
    print(f"  Range: {max(scores) - min(scores):.6f}")
    
    # Check if any score equals the base value exactly
    exact_matches = [s for s in scores if s == 0.815 or s == 0.715]
    if exact_matches:
        print(f"  WARNING: Found exact base scores: {exact_matches}")
    else:
        print(f"  GOOD: No exact base scores found")

if __name__ == "__main__":
    test_graders()
    test_step_rewards()
    test_multiple_runs()