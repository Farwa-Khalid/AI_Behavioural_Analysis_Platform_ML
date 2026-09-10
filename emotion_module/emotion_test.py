import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from emotion_model import detect_emotions
from shared_utils.preprocessing import preprocess_text
text = input("Enter text: ")

processed_text = preprocess_text(text)

print("Original:", text)
print("Processed:", processed_text)

print(detect_emotions(processed_text))