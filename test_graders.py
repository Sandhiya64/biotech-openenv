from src.envs.biotech_env.server.environment import (
    grade_easy,
    grade_medium,
    grade_hard
)

test_cases = [
    ("easy_good", grade_easy(["antibiotic"])),
    ("medium_good", grade_medium(["antiviral"])),
    ("hard_good", grade_hard(["test", "antibiotic"])),

    ("easy_none", grade_easy(None)),
    ("medium_empty", grade_medium([])),
    ("hard_invalid", grade_hard(["random"])),

    ("easy_delayed", grade_easy(["wait", "wait", "antibiotic"])),
    ("medium_delayed", grade_medium(["wait", "antiviral"])),
    ("hard_no_treatment", grade_hard(["test", "wait"]))
]

for name, score in test_cases:
    print(f"{name}: {score}")