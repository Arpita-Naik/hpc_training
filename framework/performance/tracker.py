import json
import os


def load_history(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return json.load(f)


def save_history(file_path, history):
    with open(file_path, "w") as f:
        json.dump(history, f, indent=4)


def analyze(current, history, key):

    recent = history[-5:]  
    if len(recent) == 0:
        baseline = current
    else:
        baseline = sum(r[key] for r in recent) / len(recent)

    delta = ((current - baseline) / baseline) * 100

    if current < baseline * 0.8:
        status = "⚠️ REGRESSION"

    elif current > baseline * 1.1:
        status = " IMPROVED"

    else:
        status = "✔ STABLE"

    return baseline, delta, status