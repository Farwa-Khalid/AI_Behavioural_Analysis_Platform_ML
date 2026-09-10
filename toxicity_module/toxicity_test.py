import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from toxicity_model import detect_toxicity
from shared_utils.preprocessing import preprocess_text

text = input("Enter text: ")
processed_text = preprocess_text(text)

print(processed_text)
results = detect_toxicity(processed_text)

print(results)