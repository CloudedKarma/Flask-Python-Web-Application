import random
import json
import os

# load disease metadata
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "disease_info.json")

with open(JSON_PATH, "r") as f:
    DISEASE_DATA = json.load(f)

# placeholder classes until CNN is added
CLASSES = list(DISEASE_DATA.keys())

def predict_disease(image_path):
    # random prediction for now — replaced later with real CNN inference
    predicted_class = random.choice(CLASSES)
    confidence = random.randint(80, 99)  # fake confidence

    info = DISEASE_DATA[predicted_class]

    return {
        "class": predicted_class,
        "confidence": confidence,
        "description": info["description"],
        "steps": info["steps"]
    }
