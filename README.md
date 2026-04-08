---
title: Biotech Env
emoji: 🧬
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

# 🧬 Biotech Treatment Optimization Environment  
### *Evaluating AI Agents in Clinical Decision-Making Under Uncertainty*

---

## 🌟 Overview

This project presents a **real-world reinforcement learning environment** where an AI agent simulates clinical decision-making.

Instead of solving toy problems, the agent must:
- interpret symptoms  
- decide whether to act or gather more information  
- apply correct treatment  
- optimize patient outcomes  

---

## 🧠 Motivation

Healthcare decisions are complex and rarely obvious.

Doctors must operate under:
- incomplete information  
- uncertainty  
- time constraints  

This environment replicates that challenge, enabling evaluation of AI agents in **sequential reasoning and decision-making**.

---

## ⚙️ Environment Design

### 🔁 Interaction Loop


Observation → Decision → Action → Reward → Updated State


---

## 🎮 Action Space

| Action | Description |
|------|------------|
| `antibiotic` | Treat bacterial infection |
| `antiviral` | Treat viral infection |
| `test` | Request diagnostic test |
| `wait` | No action |

---

## 📊 Observation Space

| Field | Description |
|------|------------|
| `symptoms` | Patient symptoms |
| `vitals` | Clinical indicators |
| `health_score` | Patient condition |
| `done` | Episode termination |
| `reward` | Feedback signal |

---

## 🧪 Task Design (Progressive Difficulty)

### 🟢 Easy — Clear Diagnosis
- Bacterial infection  
- Optimal action: `antibiotic`  
- Tests basic decision-making  

---

### 🟡 Medium — Misleading Scenario
- Viral infection  
- Antibiotics are harmful  
- Tests reasoning and error avoidance  

---

### 🔴 Hard — Ambiguous Case


Optimal Strategy:
test → correct treatment


- Requires multi-step reasoning  
- Tests planning and decision sequencing  

---

## 🎯 Reward Design

Unlike simple environments, rewards are:

### ✅ Dense
- Partial rewards for useful actions  
- Continuous feedback  

### ✅ Directional
- Guides agent toward correct decisions  

### ✅ Realistic
- Penalizes harmful actions  
- Encourages efficient treatment  

---

### 📈 Example Rewards

| Action | Reward |
|-------|--------|
| Correct treatment | +1.0 |
| Useful test | +0.5 |
| Wrong treatment | -0.5 |
| Inefficient steps | penalty |

---

## 🧪 Deterministic Graders

Each task includes a **programmatic grader**:

- Score range: **0.0 → 1.0**
- Evaluates:
  - correctness  
  - efficiency  
  - action sequence  

---

### 🧠 Hard Task Example

| Behavior | Score |
|--------|------|
| test → treat | 1.0 |
| treat without test | 0.0 |
| test only | 0.3 |

---

## 🤖 Baseline Performance

| Task | Score |
|------|------|
| Easy | 1.0 |
| Medium | 1.0 |
| Hard | 1.0 |

👉 Demonstrates:
- correct reasoning  
- multi-step planning  
- reproducibility  

---

## 🏗️ Architecture


Agent (LLM / Policy)
↓
OpenEnv Client
↓
Biotech Environment (FastAPI)
↓
Reward + State Update


---

## 🚀 Setup

```bash
pip install -r requirements.txt
python inference.py
🐳 Docker
docker build -t biotech-env .
docker run -p 8000:8000 biotech-env
📁 Project Structure
biotech-openenv/
├── src/
│   └── envs/biotech_env/
│       ├── models.py
│       ├── client.py
│       └── server/
│           ├── environment.py
│           ├── app.py
│           └── Dockerfile
├── inference.py
├── openenv.yaml
├── requirements.txt
└── README.md
🔮 Future Work
Multi-disease simulation
Patient variability
Drug side-effect modeling
RL training pipelines
🧠 Why This Stands Out

Most RL environments:

are toy problems
use binary rewards
lack real-world relevance
This environment provides:

✔ Real-world healthcare scenario
✔ Sequential decision-making
✔ Reward shaping with depth
✔ Deterministic evaluation
✔ Production-ready architecture

🎯 Final Pitch

A production-ready reinforcement learning environment for evaluating AI agents in clinical treatment planning under uncertainty.

👤 Author

Sandhiya Shree RK
Statistical Programmer | AI Builder | Future Founder 🚀