from chatbot.chatbot_engine import (
    create_conversation_state,
    start_conversation,
    chatbot_turn
)


print("=" * 70)
print("CHATBOT REAL TURN TEST")
print("=" * 70)


# --------------------------------------------------
# 1. Start chatbot
# --------------------------------------------------

state = create_conversation_state()

start_result = start_conversation(state)

print("\nCHATBOT START")
print("-" * 70)
print("Phase:", state["phase"])
print("Dimension:", state["current_dimension"])
print("Question:", state["current_question"])


# --------------------------------------------------
# 2. Send actual user response
# --------------------------------------------------

user_response = (
    "I usually prepare for important things, but I keep thinking "
    "about everything that could go wrong."
)

print("\nUSER RESPONSE")
print("-" * 70)
print(user_response)


# --------------------------------------------------
# 3. Process response
# --------------------------------------------------

result = chatbot_turn(state, user_response)


print("\nCHATBOT RESULT")
print("-" * 70)
print(result)

# --------------------------------------------------
# 4. Inspect state
# --------------------------------------------------

print("\nUPDATED STATE")
print("-" * 70)

print("Phase:", state["phase"])
print("Current dimension:", state["current_dimension"])
print("Current question:", state["current_question"])

dimension = state["current_dimension"]
dimension_state = state["dimensions"][dimension]

print("\nDIMENSION STATE")
print("-" * 70)

print("Dimension:", dimension)
print("Responses:", dimension_state["responses"])
print("Probabilities:", dimension_state["probabilities"])
print("Evidence count:", dimension_state["evidence_count"])
print("Score:", dimension_state["score"])
print("Status:", dimension_state["status"])

print("\nNEXT STEP")
print("-" * 70)

print("Next dimension:", result["next_dimension"])
print("Next question:", result["next_question"])

print("\n" + "=" * 70)
print("✅ REAL CHATBOT TURN TEST COMPLETED")
print("=" * 70)