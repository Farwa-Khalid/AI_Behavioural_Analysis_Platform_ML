# AI Behavioural Analysis Platform

An AI-powered behavioural analysis platform developed as a Final Year Project (FYP). The system combines Natural Language Processing (NLP), machine learning, and conversational analysis to provide behavioural insights through multiple AI-based modules.

## Overview

The AI Behavioural Analysis Platform analyzes user-provided text and conversational responses using multiple specialized AI modules.

The platform currently includes:

* **Emotion Analysis**
* **Sentiment Analysis**
* **Toxicity Detection**
* **Neuroticism Analysis**
* **Behavioural Analysis Chatbot**

The system is designed to analyze different aspects of user language and behaviour while providing a structured conversational assessment and personalized exercises.

> **Note:** This project is intended for educational and research purposes. It is not a medical or clinical diagnostic system.

---

## Features

### 1. Emotion Analysis

The emotion analysis module uses a pretrained Hugging Face transformer model to identify emotions expressed in user text.

The system can return the most relevant emotions along with their confidence scores.

### 2. Sentiment Analysis

The sentiment module determines whether the provided text expresses a positive or negative sentiment.

### 3. Toxicity Detection

The toxicity module analyzes text for potentially toxic language using a pretrained toxicity detection model.

### 4. Neuroticism Analysis

The neuroticism module uses sentence embeddings and a machine-learning classifier to estimate whether text contains behavioural patterns associated with neuroticism.

The current implementation uses:

* `all-mpnet-base-v2` sentence embeddings
* Logistic Regression classifier
* Saved trained model (`neurotic_model.pkl`)

The model produces probabilities for the predicted classes rather than relying only on a binary prediction.

### 5. Behavioural Analysis Chatbot

The chatbot provides a structured conversational assessment focused on behavioural dimensions associated with neuroticism.

The current chatbot considers eight dimensions:

1. Future Worry
2. Rumination
3. Uncertainty
4. Overthinking
5. Social Evaluation
6. Self-Doubt
7. Emotional Reactivity
8. Worry Persistence

The chatbot:

* Asks assessment questions
* Routes user responses
* Detects unclear or unrelated responses
* Collects behavioural evidence
* Tracks dimension scores
* Identifies higher-scoring behavioural dimensions
* Recommends personalized coping exercises
* Supports reassessment after exercises

---

## Project Structure

```text
AI-Behavioural-Analysis-Platform/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── chatbot/
│   └── chatbot_engine.py
│
├── emotion_module/
│   ├── emotion_model.py
│   └── emotion_test.py
│
├── neuroticism_module/
│   ├── neuroticism_model.py
│   ├── neuroticism_test.py
│   ├── neurotic_model.pkl
│   └── mpnet_embedder/
│
├── sentiment_module/
│   ├── sentiment_model.py
│   └── sentiment_test.py
│
├── toxicity_module/
│   ├── toxicity_model.py
│   └── toxicity_test.py
│
├── shared_utils/
│   ├── emoji_mapper.py
│   ├── preprocessing.py
│   └── slang_mapper.py
│
├── templates/
│   ├── index.html
│   └── chatbot.html
│
└── test_*.py
```

---

## Technologies Used

### Programming Language

* Python

### Backend

* Flask

### Machine Learning & NLP

* Scikit-learn
* PyTorch
* Hugging Face Transformers
* Sentence Transformers
* Detoxify

### Models

The project currently integrates pretrained and custom machine-learning models, including:

* `SamLowe/roberta-base-go_emotions`
* `distilbert-base-uncased-finetuned-sst-2-english`
* Detoxify
* `all-mpnet-base-v2`
* Custom Logistic Regression neuroticism classifier

### Frontend

* HTML
* CSS
* JavaScript
* Flask Jinja templates

---

## Chatbot Assessment Flow

The behavioural chatbot follows a structured assessment process.

```text
Start
  │
  ▼
Initial Greeting
  │
  ▼
Behavioural Question
  │
  ▼
User Response
  │
  ├── Relevant ──────► Analyze & Store Evidence
  │
  ├── Unclear ───────► Ask for Clarification
  │
  └── Unrelated ─────► Neutral/Fallback Response
  │
  ▼
Continue Assessment
  │
  ▼
Analyze Behavioural Dimensions
  │
  ▼
Identify Higher-Scoring Dimensions
  │
  ▼
Recommend Exercises
  │
  ▼
User Completes Exercises
  │
  ▼
Reassessment
  │
  ▼
Compare Behavioural Scores
```

---

## Behavioural Dimensions

The chatbot currently evaluates the following dimensions:

| Dimension            | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| Future Worry         | Concern about future events and possible negative outcomes |
| Rumination           | Repeatedly thinking about past events                      |
| Uncertainty          | Difficulty dealing with uncertain situations               |
| Overthinking         | Excessive analysis and difficulty stopping thoughts        |
| Social Evaluation    | Concern about how others perceive or judge the user        |
| Self-Doubt           | Doubting one's own abilities or decisions                  |
| Emotional Reactivity | Strong emotional responses to stressful events             |
| Worry Persistence    | Difficulty stopping worry once it begins                   |

---

## Personalized Exercises

Based on the assessment results, the chatbot can recommend exercises related to the user's higher-scoring dimensions.

Examples include:

* **Future Worry Reset**
* **Thought Release**
* **Uncertainty Practice**
* **Decision Stop Point**
* **Social Judgment Check**
* **Self-Confidence Evidence**
* **Pause and Calm**
* **Worry Time Boundary**

After completing the exercises, the chatbot can move into a reassessment phase.

---

## Testing

The repository contains separate test files for different components of the chatbot:

```text
test_chatbot_engine.py
test_chatbot_routing.py
test_chatbot_turn.py
test_exercise_phase.py
test_full_assesment.py
test_full_chatbot.py
test_reassessment.py
```

These tests are used to verify:

* Chatbot initialization
* Response routing
* Conversation turns
* Evidence collection
* Exercise recommendations
* Assessment completion
* Reassessment
* End-to-end chatbot behaviour

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

### 2. Open the project

```bash
cd AI-Behavioural-Analysis-Platform
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

On Windows:

```powershell
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Then open the local Flask address shown in the terminal.

---

## Running Tests

Individual tests can be executed using:

```bash
python test_chatbot_engine.py
```

or:

```bash
python test_full_chatbot.py
```

The complete test suite can also be executed with:

```bash
python -m pytest
```

if `pytest` is installed.

---

## Current Development Status

### Completed

* [x] Flask application
* [x] Emotion analysis module
* [x] Sentiment analysis module
* [x] Toxicity detection module
* [x] Neuroticism prediction module
* [x] Shared text preprocessing
* [x] Behavioural chatbot engine
* [x] Behavioural dimension tracking
* [x] Response routing
* [x] Neutral/fallback handling
* [x] Personalized exercise recommendations
* [x] Reassessment flow
* [x] Multiple chatbot tests

### Future Work

* [ ] Improve neuroticism model performance
* [ ] Expand behavioural question bank
* [ ] Improve uncertainty handling
* [ ] Improve chatbot response generation
* [ ] Complete API-based architecture
* [ ] Develop React frontend
* [ ] Add persistent database storage
* [ ] Improve authentication and user management
* [ ] Improve UI/UX
* [ ] Add comprehensive evaluation metrics

---

## Disclaimer

This project is an academic Final Year Project and is intended for educational and research purposes.

The behavioural and neuroticism predictions should not be interpreted as medical, psychological, or clinical diagnoses.

---

## Authors

**Final Year Project — AI Behavioural Analysis Platform**

Developed as part of a Bachelor of Science in Computer Science degree.

---

## License

This project is currently intended for academic and educational use.
