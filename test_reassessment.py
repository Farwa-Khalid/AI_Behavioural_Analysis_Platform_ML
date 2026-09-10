from chatbot.chatbot_engine import (
    create_conversation_state,
    start_conversation,
    chatbot_turn,
    generate_baseline_results,
    recommend_exercises,
    complete_exercise,
    start_exercise_phase,
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
print("REASSESSMENT PHASE TEST")
print("=" * 70)


# ============================================================
# 1. CREATE STATE + START INITIAL ASSESSMENT
# ============================================================

state = create_conversation_state()

start_conversation(state)

assert state["phase"] == "initial_assessment"

print("\n✅ Chatbot initialized")


# ============================================================
# 2. COMPLETE INITIAL ASSESSMENT
# ============================================================

initial_response = (
    "I often worry about possible problems and keep thinking "
    "about things even after I have prepared for them."
)

max_turns = 30

for _ in range(max_turns):

    if state["phase"] != "initial_assessment":
        break

    chatbot_turn(
        state,
        initial_response
    )


assert state["phase"] == "assessment_complete"

print("✅ Initial assessment completed")
print("Assessment turns:", state["turn_count"])


# ============================================================
# 3. GENERATE BASELINE
# ============================================================

baseline_result = generate_baseline_results(state)

assert baseline_result["status"] == "complete"

print("\n" + "=" * 70)
print("BASELINE RESULTS")
print("=" * 70)

for dimension in DIMENSIONS:

    data = state["dimensions"][dimension]

    print(
        f"{dimension:25s} | "
        f"Score: {data['score']} | "
        f"Evidence: {data['evidence_count']}"
    )

print("\n✅ Baseline generated")


# ============================================================
# 4. RECOMMEND EXERCISES
# ============================================================

recommendation_result = recommend_exercises(state)

assert state["recommended_exercises"] is not None
assert len(state["recommended_exercises"]) > 0

print("\n" + "=" * 70)
print("EXERCISE RECOMMENDATIONS")
print("=" * 70)

print("Recommended exercises:")

for exercise in state["recommended_exercises"]:

    print(
        f"- {exercise['title']} "
        f"({exercise['dimension']})"
    )

print(
    "\nTotal recommendations:",
    len(state["recommended_exercises"])
)

print("✅ Exercises recommended")


# ============================================================
# 5. START EXERCISE PHASE
# ============================================================

exercise_start = start_exercise_phase(state)

assert state["phase"] == "exercises"

print("\n" + "=" * 70)
print("EXERCISE PHASE")
print("=" * 70)

print(exercise_start)

print("Phase:", state["phase"])


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

print("\nCompleted exercise:")
print(first_exercise["title"])

print("Completed dimensions:")
print(state["completed_exercises"])

print("✅ Exercise completed")


# ============================================================
# 7. FINISH EXERCISE PHASE
# ============================================================

finish_result = finish_exercise_phase(state)

assert finish_result["status"] == "ready_for_reassessment"

print("\n" + "=" * 70)
print("FINISH EXERCISE PHASE")
print("=" * 70)

print(finish_result)

print(
    "\nExercises completed:",
    finish_result["completed_exercises"],
    "/",
    finish_result["total_exercises"]
)

print("✅ Exercise phase finished")


# ============================================================
# 8. PREPARE REASSESSMENT
# ============================================================

reassessment_start = start_reassessment(state)

print("\n" + "=" * 70)
print("START REASSESSMENT")
print("=" * 70)

print(reassessment_start)

assert reassessment_start["status"] == "ready"
assert state["phase"] == "reassessment"

print("\nPhase:", state["phase"])
print("✅ Reassessment prepared")


# ============================================================
# 9. BEGIN REASSESSMENT
# ============================================================

begin_result = begin_reassessment(state)

print("\n" + "=" * 70)
print("BEGIN REASSESSMENT")
print("=" * 70)

print(begin_result)

assert begin_result["status"] == "started"
assert begin_result["dimension"] == DIMENSIONS[0]
assert begin_result["question"] is not None

print("\nFirst dimension:", begin_result["dimension"])
print("First question:", begin_result["question"])

print("✅ Reassessment started")


# ============================================================
# 10. PROCESS REASSESSMENT
# ============================================================

reassessment_response = (
    "I feel better now. I still think about possible problems, "
    "but I am usually able to prepare and move on without "
    "worrying for too long."
)

max_reassessment_turns = 30

for turn in range(max_reassessment_turns):

    if state["phase"] != "reassessment":
        break

    result = process_reassessment_turn(
        state,
        reassessment_response
    )

    print(
        f"\nTurn {turn + 1}: "
        f"{result.get('response_type', 'N/A')}"
    )

    print(
        "Dimension:",
        result.get("dimension")
    )

    print(
        "Evidence:",
        result.get("evidence_count")
    )

    print(
        "Next question:",
        result.get("question")
    )


# ============================================================
# 11. VERIFY REASSESSMENT COMPLETION
# ============================================================

assert state["phase"] == "reassessment_complete"

assert state["reassessment_complete"] is True

print("\n" + "=" * 70)
print("REASSESSMENT COMPLETED")
print("=" * 70)

print(
    "Total reassessment dimensions:",
    len(state["reassessment_dimensions"])
)

for dimension in DIMENSIONS:

    data = state["reassessment_dimensions"][dimension]

    print(
        f"{dimension:25s} | "
        f"Score: {data['score']} | "
        f"Evidence: {data['evidence_count']} | "
        f"Status: {data['status']}"
    )

print("\n✅ Reassessment completed")


# ============================================================
# 12. COMPARE BASELINE VS REASSESSMENT
# ============================================================

comparison_result = compare_baseline_reassessment(state)

print("\n" + "=" * 70)
print("BASELINE VS REASSESSMENT")
print("=" * 70)

print(comparison_result)

assert comparison_result is not None

print("\n✅ Comparison generated")


# ============================================================
# 13. GENERATE PROGRESS SUMMARY
# ============================================================

summary_result = generate_progress_summary(state)

print("\n" + "=" * 70)
print("PROGRESS SUMMARY")
print("=" * 70)

print(summary_result)

assert summary_result is not None

print("\n✅ Progress summary generated")


# ============================================================
# 14. GENERATE USER-FACING PROGRESS MESSAGE
# ============================================================

progress_message = generate_progress_message(state)

print("\n" + "=" * 70)
print("USER-FACING PROGRESS MESSAGE")
print("=" * 70)

print(progress_message)

assert progress_message is not None

print("\n✅ Progress message generated")


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("🎉 REASSESSMENT PHASE TEST PASSED")
print("=" * 70)