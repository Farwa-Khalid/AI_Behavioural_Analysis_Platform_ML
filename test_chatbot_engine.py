from neuroticism_module.neuroticism_model import predict_neuroticism
from chatbot.chatbot_engine import (
    create_conversation_state,
    start_conversation
)


print("=" * 60)
print("CHATBOT + NEUROTICISM MODEL INTEGRATION TEST")
print("=" * 60)


# --------------------------------------------------
# 1. Test Neuroticism model interface
# --------------------------------------------------

test_text = "I keep worrying about everything that could go wrong."

result = predict_neuroticism(test_text)

print("\nMODEL TEST")
print("-" * 60)
print("Text:", test_text)
print("Prediction:", result["prediction"])
print("Neurotic probability:", result["neurotic_probability"], "%")
print("Non-neurotic probability:", result["non_neurotic_probability"], "%")

print("✅ Neuroticism model interface works")


# --------------------------------------------------
# 2. Test chatbot initialization
# --------------------------------------------------

state = create_conversation_state()

print("\nCHATBOT INITIALIZATION")
print("-" * 60)

print("Phase:", state["phase"])

conversation = start_conversation(state)

print("Greeting:", conversation["message"])
print("First dimension:", state["current_dimension"])
print("First question:", state["current_question"])
print("Session ID:", state["session_id"])

print("✅ Chatbot initialization works")


print("\n" + "=" * 60)
print("✅ INTEGRATION TEST PASSED")
print("=" * 60)