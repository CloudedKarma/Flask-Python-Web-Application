import random
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

JSON_PATH = os.path.join(BASE_DIR, "disease_info.json")

with open(JSON_PATH, "r") as f:
    DISEASE_DATA = json.load(f)

CLASSES = list(DISEASE_DATA.keys())

def predict_disease(image_path):
    predicted_class = random.choice(CLASSES)
    confidence = random.randint(80, 99)

    info = DISEASE_DATA[predicted_class]

    # Build a combined description text
    description_text = f"Common name: {info.get('common_name', 'N/A')}\n"
    description_text += f"Affects: {info.get('plant', 'Unknown')}\n"

    # The treatment steps list
    steps = info.get("treatment", [])

    return {
        "class": predicted_class,
        "confidence": confidence,
        "description": description_text,
        "steps": steps
    }
