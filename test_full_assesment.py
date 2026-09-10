from chatbot.chatbot_engine import (
    create_conversation_state,
    start_conversation,
    chatbot_turn,
    generate_baseline_results,
    DIMENSIONS
)


print("=" * 70)
print("FULL 8-DIMENSION ASSESSMENT TEST")
print("=" * 70)


# ============================================================
# 1. CREATE CHATBOT STATE
# ============================================================

state = create_conversation_state()

start_result = start_conversation(state)

print("\nCHATBOT START")
print("-" * 70)
print("Phase:", state["phase"])
print("First dimension:", state["current_dimension"])
print("First question:", state["current_question"])

assert state["phase"] == "initial_assessment"
assert state["current_dimension"] == DIMENSIONS[0]
assert state["current_question"] is not None

print("✅ Chatbot started successfully")


# ============================================================
# 2. RESPONSES FOR EACH DIMENSION
# ============================================================

sample_response = (
    "I often think about possible problems and sometimes "
    "keep worrying even after I have prepared for the situation."
)


# ============================================================
# 3. KEEP ANSWERING UNTIL ASSESSMENT COMPLETES
# ============================================================

max_turns = 30

for turn in range(max_turns):

    if state["phase"] != "initial_assessment":
        break

    current_dimension = state["current_dimension"]
    current_question = state["current_question"]

    print("\n" + "=" * 70)
    print(f"TURN {turn + 1}")
    print("=" * 70)

    print("Dimension:", current_dimension)
    print("Question:", current_question)

    result = chatbot_turn(
        state,
        sample_response
    )

    print("Response type:", result["response_type"])

    if result.get("analysis"):
        print(
            "Neurotic probability:",
            result["analysis"]["probability"]
        )

    dimension_data = state["dimensions"][current_dimension]

    print(
        "Evidence count:",
        dimension_data["evidence_count"]
    )

    print(
        "Score:",
        dimension_data["score"]
    )

    print(
        "Status:",
        dimension_data["status"]
    )

    print(
        "Next dimension:",
        result.get("next_dimension")
    )

    print(
        "Next question:",
        result.get("next_question")
    )


# ============================================================
# 4. VERIFY ASSESSMENT COMPLETED
# ============================================================

print("\n" + "=" * 70)
print("ASSESSMENT RESULT")
print("=" * 70)

print("Phase:", state["phase"])
print("Total turns:", state["turn_count"])

assert state["phase"] == "assessment_complete"

print("✅ Initial assessment completed")


# ============================================================
# 5. VERIFY ALL 8 DIMENSIONS
# ============================================================

print("\nDIMENSION RESULTS")
print("-" * 70)

for dimension in DIMENSIONS:

    data = state["dimensions"][dimension]

    print(
        f"{dimension:25s} | "
        f"Evidence: {data['evidence_count']} | "
        f"Score: {data['score']} | "
        f"Status: {data['status']}"
    )

    assert data["evidence_count"] >= 1
    assert data["score"] is not None


print("\n✅ All 8 dimensions contain assessment evidence")


# ============================================================
# 6. GENERATE BASELINE RESULTS
# ============================================================

baseline = generate_baseline_results(state)

print("\n" + "=" * 70)
print("BASELINE RESULTS")
print("=" * 70)

print(baseline)


assert baseline is not None

print("\n✅ Baseline results generated")


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("🎉 FULL ASSESSMENT TEST PASSED")
print("=" * 70)