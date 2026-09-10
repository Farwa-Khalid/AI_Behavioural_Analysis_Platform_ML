from chatbot.chatbot_engine import (
    create_conversation_state,
    start_conversation,
    chatbot_turn,
    generate_baseline_results,
    recommend_exercises,
    start_exercise_phase,
    complete_exercise,
    finish_exercise_phase,
    start_reassessment,
    begin_reassessment,
    process_reassessment_turn,
    compare_baseline_reassessment,
    generate_progress_summary,
    generate_progress_message,
    DIMENSIONS
)


print("=" * 70)
print("FULL CHATBOT LIFECYCLE TEST")
print("=" * 70)


# ============================================================
# 1. CREATE + START CHATBOT
# ============================================================

state = create_conversation_state()

start_result = start_conversation(state)

assert state["phase"] == "initial_assessment"

print("\n✅ 1. CHATBOT STARTED")
print("Phase:", state["phase"])
print("First dimension:", state["current_dimension"])
print("First question:", state["current_question"])


# ============================================================
# 2. INITIAL ASSESSMENT
# ============================================================

initial_response = (
    "I often worry about things that could go wrong. "
    "Even after preparing, I sometimes keep thinking about "
    "possible problems."
)

for _ in range(30):

    if state["phase"] != "initial_assessment":
        break

    result = chatbot_turn(
        state,
        initial_response
    )


assert state["phase"] == "assessment_complete"

print("\n✅ 2. INITIAL ASSESSMENT COMPLETE")
print("Turns:", state["turn_count"])


# ============================================================
# 3. BASELINE
# ============================================================

baseline_result = generate_baseline_results(state)

assert baseline_result["status"] == "complete"

print("\n✅ 3. BASELINE GENERATED")

for dimension in DIMENSIONS:

    data = state["dimensions"][dimension]

    print(
        f"{dimension:25s} | "
        f"Score: {data['score']} | "
        f"Evidence: {data['evidence_count']} | "
        f"Status: {data['status']}"
    )


# ============================================================
# 4. PERSONALIZED EXERCISES
# ============================================================

recommendation_result = recommend_exercises(state)

assert state["recommended_exercises"] is not None
assert len(state["recommended_exercises"]) > 0

print("\n✅ 4. EXERCISES RECOMMENDED")

for exercise in state["recommended_exercises"]:

    print(
        f"- {exercise['title']} "
        f"→ {exercise['dimension']}"
    )


# ============================================================
# 5. START EXERCISE PHASE
# ============================================================

exercise_start = start_exercise_phase(state)

assert state["phase"] == "exercises"

print("\n✅ 5. EXERCISE PHASE STARTED")


# ============================================================
# 6. COMPLETE FIRST EXERCISE
# ============================================================

first_exercise = state["recommended_exercises"][0]

first_dimension = first_exercise["dimension"]

completion_result = complete_exercise(
    state,
    first_dimension
)

assert completion_result["status"] == "complete"

assert first_dimension in state["completed_exercises"]

print("\n✅ 6. EXERCISE COMPLETED")
print("Exercise:", first_exercise["title"])
print("Dimension:", first_dimension)


# ============================================================
# 7. FINISH EXERCISE PHASE
# ============================================================

finish_result = finish_exercise_phase(state)

assert finish_result["status"] == "ready_for_reassessment"

print("\n✅ 7. EXERCISE PHASE FINISHED")
print(
    "Completed:",
    finish_result["completed_exercises"],
    "/",
    finish_result["total_exercises"]
)


# ============================================================
# 8. START REASSESSMENT
# ============================================================

reassessment_start = start_reassessment(state)

assert reassessment_start["status"] == "ready"
assert state["phase"] == "reassessment"

print("\n✅ 8. REASSESSMENT PREPARED")


# ============================================================
# 9. BEGIN REASSESSMENT
# ============================================================

begin_result = begin_reassessment(state)

assert begin_result["status"] == "started"

print("\n✅ 9. REASSESSMENT STARTED")
print("First dimension:", begin_result["dimension"])
print("First question:", begin_result["question"])


# ============================================================
# 10. REASSESSMENT
# ============================================================

reassessment_response = (
    "I feel more in control now. I still think about "
    "possible problems, but I can usually prepare and "
    "move forward without worrying for too long."
)

reassessment_turns = 0

for _ in range(30):

    if state["phase"] != "reassessment":
        break

    result = process_reassessment_turn(
        state,
        reassessment_response
    )

    reassessment_turns += 1


assert state["phase"] == "reassessment_complete"

assert state["reassessment_complete"] is True

print("\n✅ 10. REASSESSMENT COMPLETE")
print("Reassessment turns:", reassessment_turns)


# ============================================================
# 11. VERIFY ALL REASSESSMENT DIMENSIONS
# ============================================================

print("\n" + "=" * 70)
print("REASSESSMENT RESULTS")
print("=" * 70)

for dimension in DIMENSIONS:

    data = state["reassessment_dimensions"][dimension]

    print(
        f"{dimension:25s} | "
        f"Score: {data['score']} | "
        f"Evidence: {data['evidence_count']} | "
        f"Status: {data['status']}"
    )

    assert data["score"] is not None
    assert data["evidence_count"] >= 2


# ============================================================
# 12. BASELINE VS REASSESSMENT
# ============================================================

comparison_result = compare_baseline_reassessment(state)

assert comparison_result is not None

print("\n✅ 11. BASELINE VS REASSESSMENT COMPARED")

print(comparison_result)


# ============================================================
# 13. PROGRESS SUMMARY
# ============================================================

summary_result = generate_progress_summary(state)

assert summary_result is not None

print("\n" + "=" * 70)
print("PROGRESS SUMMARY")
print("=" * 70)

print(summary_result)

print("\n✅ 12. PROGRESS SUMMARY GENERATED")


# ============================================================
# 14. USER-FACING MESSAGE
# ============================================================

progress_message = generate_progress_message(state)

assert progress_message is not None

print("\n" + "=" * 70)
print("FINAL USER-FACING MESSAGE")
print("=" * 70)

print(progress_message)

print("\n✅ 13. USER-FACING MESSAGE GENERATED")


# ============================================================
# FINAL VERIFICATION
# ============================================================

print("\n" + "=" * 70)
print("FINAL LIFECYCLE VERIFICATION")
print("=" * 70)

print("Initial assessment:       ✅")
print("Baseline results:        ✅")
print("Exercise recommendation: ✅")
print("Exercise completion:     ✅")
print("Reassessment:            ✅")
print("Comparison:              ✅")
print("Progress summary:        ✅")
print("Final message:           ✅")


print("\n" + "=" * 70)
print("🎉 FULL CHATBOT LIFECYCLE TEST PASSED")
print("=" * 70)