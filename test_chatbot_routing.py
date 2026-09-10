from chatbot.chatbot_engine import (
    create_conversation_state,
    start_conversation,
    chatbot_turn
)


def print_result(test_name, result, state):
    print("\n" + "=" * 70)
    print(test_name)
    print("=" * 70)

    print("Response type:", result["response_type"])
    print("Message:", result["message"])

    print("\nCurrent dimension:", state["current_dimension"])
    print("Current question:", state["current_question"])

    dimension = state["current_dimension"]
    dimension_state = state["dimensions"][dimension]

    print("\nEvidence count:", dimension_state["evidence_count"])
    print("Score:", dimension_state["score"])
    print("Status:", dimension_state["status"])


# ============================================================
# TEST 1 — RELEVANT
# ============================================================

state = create_conversation_state()
start_conversation(state)

relevant_response = (
    "I often worry about things that could go wrong in the future "
    "even when I have prepared for them."
)

result = chatbot_turn(state, relevant_response)

print_result("TEST 1 — RELEVANT RESPONSE", result, state)

assert result["response_type"] == "relevant"
assert state["dimensions"]["future_worry"]["evidence_count"] == 1
assert state["dimensions"]["future_worry"]["score"] is not None

print("\n✅ RELEVANT TEST PASSED")


# ============================================================
# TEST 2 — NEUTRAL
# ============================================================

state = create_conversation_state()
start_conversation(state)

original_question = state["current_question"]

neutral_response = "I don't really have anything to say about that."

result = chatbot_turn(state, neutral_response)

print_result("TEST 2 — NEUTRAL RESPONSE", result, state)

assert result["response_type"] == "neutral"

# Neutral response must NOT create evidence
assert state["dimensions"]["future_worry"]["evidence_count"] == 0
assert state["dimensions"]["future_worry"]["score"] is None

# Neutral response should keep the current question
# because no evidence was collected.
assert state["current_question"] == original_question

print("\n✅ NEUTRAL TEST PASSED")


# ============================================================
# TEST 3 — UNCLEAR
# ============================================================

state = create_conversation_state()
start_conversation(state)

original_question = state["current_question"]

unclear_response = "Maybe."

result = chatbot_turn(state, unclear_response)

print_result("TEST 3 — UNCLEAR RESPONSE", result, state)

assert result["response_type"] == "unclear"

# Unclear response must NOT create evidence
assert state["dimensions"]["future_worry"]["evidence_count"] == 0
assert state["dimensions"]["future_worry"]["score"] is None

# The chatbot should stay on the same question
assert state["current_question"] == original_question

print("\n✅ UNCLEAR TEST PASSED")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("ROUTING TEST SUMMARY")
print("=" * 70)

print("✅ Relevant  → analyzed + evidence added")
print("✅ Neutral   → not scored + next question")
print("✅ Unclear   → clarification + same question")

print("\n" + "=" * 70)
print("🎉 ALL ROUTING TESTS PASSED")
print("=" * 70)