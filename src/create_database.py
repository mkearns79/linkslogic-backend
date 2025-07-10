"""Script to create and populate the rules database."""
import json
import os
from pathlib import Path

# Define paths
DATA_DIR = "data"
RULES_FILE = f"{DATA_DIR}/rules_database.json"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Sample rules data (you'll replace with your 10 common rules)
rules_data = {
    "rules": [
        {
            "id": "16-1a",
            "title": "Rule 16.1a: Relief from Abnormal Course Condition",
            "section": "Relief Options",
            "text": "When your ball lies in a temporary water, ground under repair, animal hole, or is up against an immovable obstruction, you may take free relief by dropping a ball in a relief area based on the nearest point of complete relief.",
            "keywords": ["abnormal", "course", "condition", "relief", "temporary", "standing", "casual", "mud", "water", "puddle", "pool", "ground", "repair", "animal", "hole", "immovable", "obstruction", "free", "drop", "nearest", "point"],
            "situations": ["abnormal course conditions", "relief options"],
            "examples": [
                {
                    "question": "What do I do if my ball is in casual water?",
                    "answer": "When your ball lies in casual water (temporary water), you may take free relief by dropping a ball in a relief area that is based on your nearest point of complete relief, within one club-length, and not nearer the hole."
                },
                {
                    "question": "Can I get relief from ground under repair?",
                    "answer": "Yes, when your ball lies in ground under repair, you may take free relief by dropping a ball in a relief area based on your nearest point of complete relief, within one club-length, and not nearer the hole."
                },
                {
                    "question": "Ball came to rest in a puddle, what do I do?",
                    "answer": "When your ball is in a puddle (temporary water), you're entitled to free relief. Find your nearest point of complete relief where the puddle doesn't interfere with your stance or swing, then drop within one club-length of that point, no nearer the hole."
                },
                {
                    "question": "My ball is landed in a tractor tire track, do I get relief?",
                    "answer": "Yes, when your ball comes to rest in a tire track in any area of the course deemed to be in play (i.e., not a hazzard), you may take relief by dropping the ball within one club-length, no nearer to the hole."
                }
            ],
            "related_rules": ["16.1b", "16.1c", "16.1d"]
        },
        {
            "id": "19-2",
            "title": "Rule 19.2: Relief Options for Unplayable Ball",
            "section": "Relief Options",
            "text": "A player may take unplayable ball relief using one of the three options in Rule 19.2a, b or c, in each case adding one penalty stroke.",
            "keywords": ["unplayable", "ball", "relief", "options", "penalty", "stroke"],
            "situations": ["unplayable ball"],
            "examples": [
                {
                    "question": "What are my options if my ball is unplayable?",
                    "answer": "When you declare your ball unplayable, you have three options with a one-stroke penalty: 1) Stroke-and-distance relief, 2) Back-on-the-line relief, or 3) Lateral relief within two club-lengths of where the ball lies (not nearer the hole)."
                }
            ],
            "related_rules": ["19.2a", "19.2b", "19.2c", "19.3"]
        }
    ]
}

# Write to JSON file
with open(RULES_FILE, 'w') as f:
    json.dump(rules_data, f, indent=2)

print(f"Database created with {len(rules_data['rules'])} rules at {RULES_FILE}")
