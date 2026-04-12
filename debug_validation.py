#!/usr/bin/env python3
"""
Debug what the validation system is actually seeing
"""

import sys
import os
import json
import random

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your environment and graders
from src.envs.biotech_env.server.environment import BiotechEnvironment, GRADERS

def simulate_validation_run():
    """Simulate what the validation system might be doing"""
    
    print("=" * 70)
    print("SIMULATING VALIDATION SYSTEM CHECK")
    print("=" * 70)
    
    results = {}
    
    for task_name in ["easy", "medium", "hard"]:
        print(f"\n--- Task: {task_name} ---")
        
        # Create environment
        env = BiotechEnvironment()
        obs = env.reset(task_name)
        
        actions_taken = []
        rewards = []
        done = False
        step_count = 0
        
        # Run up to 5 steps
        while not done and step_count < 5:
            # Simple policy for testing
            if task_name == "easy":
                action = "antibiotic"
            elif task_name == "medium":
                action = "antiviral"
            else:  # hard
                if step_count == 0:
                    action = "test"
                else:
                    action = "antibiotic"
            
            actions_taken.append(action)
            obs = env.step({"action_type": action})
            rewards.append(obs.reward)
            done = obs.done
            step_count += 1
        
        print(f"  Actions taken: {actions_taken}")
        print(f"  Rewards: {[f'{r:.6f}' for r in rewards]}")
        
        # Get grader score
        grader = GRADERS[task_name]
        final_score = grader(actions_taken)
        
        print(f"  Grader score: {final_score:.10f}")
        print(f"  Score type: {type(final_score)}")
        
        # Check validation requirements
        issues = []
        
        if final_score <= 0:
            issues.append("Score <= 0")
        if final_score >= 1:
            issues.append("Score >= 1")
        if final_score == 0.0:
            issues.append("Score is exactly 0.0")
        if final_score == 1.0:
            issues.append("Score is exactly 1.0")
        
        # Check if it's too close to boundaries (within 0.001)
        if final_score < 0.001:
            issues.append(f"Score too close to 0: {final_score}")
        if final_score > 0.999:
            issues.append(f"Score too close to 1: {final_score}")
        
        # Check for suspiciously round numbers
        if final_score == round(final_score, 3):
            issues.append(f"Score rounds to 3 decimal places: {final_score:.3f}")
        
        if issues:
            print(f"  ❌ ISSUES FOUND: {', '.join(issues)}")
            results[task_name] = "FAILED"
        else:
            print(f"  ✓ Score passes basic validation")
            results[task_name] = "PASSED"
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for task, status in results.items():
        print(f"  {task}: {status}")
    
    return results

def check_openenv_yaml():
    """Check if openenv.yaml has any issues"""
    
    print("\n" + "=" * 70)
    print("CHECKING openenv.yaml")
    print("=" * 70)
    
    import yaml
    
    try:
        with open("openenv.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        print("✓ openenv.yaml loaded successfully")
        
        # Check tasks configuration
        if "tasks" in config:
            print("\n  Tasks configured:")
            for task in config["tasks"]:
                print(f"    - {task.get('name')}: {task.get('grader')}")
        
        # Check reward_range
        if "reward_range" in config:
            reward_range = config["reward_range"]
            print(f"\n  reward_range: {reward_range}")
            
            if reward_range[0] <= 0:
                print(f"  ⚠️  reward_range min is {reward_range[0]} (should be > 0)")
            if reward_range[1] >= 1:
                print(f"  ⚠️  reward_range max is {reward_range[1]} (should be < 1)")
        
        return config
        
    except Exception as e:
        print(f"❌ Error loading openenv.yaml: {e}")
        return None

def check_grader_imports():
    """Check if graders can be properly imported"""
    
    print("\n" + "=" * 70)
    print("CHECKING GRADER IMPORTS")
    print("=" * 70)
    
    try:
        from src.envs.biotech_env.server.environment import grade_easy, grade_medium, grade_hard
        
        print("✓ All graders imported successfully")
        
        # Test each grader returns float
        test_actions = ["test", "antibiotic"]
        
        easy_score = grade_easy(test_actions)
        medium_score = grade_medium(test_actions)
        hard_score = grade_hard(test_actions)
        
        print(f"\n  grade_easy(['test', 'antibiotic']) = {easy_score:.10f}")
        print(f"  grade_medium(['test', 'antibiotic']) = {medium_score:.10f}")
        print(f"  grade_hard(['test', 'antibiotic']) = {hard_score:.10f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment_rewards():
    """Check that step rewards are within bounds"""
    
    print("\n" + "=" * 70)
    print("CHECKING ENVIRONMENT REWARDS")
    print("=" * 70)
    
    env = BiotechEnvironment()
    
    for task in ["easy", "medium", "hard"]:
        print(f"\n  Task: {task}")
        obs = env.reset(task)
        print(f"    Reset reward: {obs.reward:.10f}")
        
        # Test each action type
        for action in ["antibiotic", "antiviral", "test", "wait"]:
            # Create fresh env for each test
            env2 = BiotechEnvironment()
            obs2 = env2.reset(task)
            obs3 = env2.step({"action_type": action})
            print(f"    Action '{action}': reward={obs3.reward:.10f}, done={obs3.done}")
            
            # Check bounds
            if obs3.reward <= 0:
                print(f"      ❌ Reward <= 0")
            if obs3.reward >= 1:
                print(f"      ❌ Reward >= 1")
            if obs3.reward == 0.1 or obs3.reward == 0.9:
                print(f"      ⚠️  Reward is exactly 0.1 or 0.9")

if __name__ == "__main__":
    # Run all checks
    check_grader_imports()
    check_openenv_yaml()
    check_environment_rewards()
    simulate_validation_run()