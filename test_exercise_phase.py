from chatbot.chatbot_engine import (
    create_conversation_state,
    start_conversation,
    chatbot_turn,
    generate_baseline_results,
    recommend_exercises,
    complete_exercise,
    start_exercise_phase,
    finish_exercise_phase,
    DIMENSIONS
)


print("=" * 70)
print("EXERCISE / COPING PHASE TEST")
print("=" * 70)


# ============================================================
# 1. CREATE STATE + START ASSESSMENT
# ============================================================

state = create_conversation_state()

start_conversation(state)

assert state["phase"] == "initial_assessment"

print("\n✅ Chatbot initialized")


# ============================================================
# 2. COMPLETE INITIAL ASSESSMENT
# ============================================================

sample_response = (
    "I often think about possible problems and sometimes "
    "keep worrying even after I have prepared for the situation."
)

max_turns = 30

for _ in range(max_turns):

    if state["phase"] != "initial_assessment":
        break

    chatbot_turn(
        state,
        sample_response
    )


assert state["phase"] == "assessment_complete"

print("✅ Initial assessment completed")
print("Total assessment turns:", state["turn_count"])


# ============================================================
# 3. GENERATE BASELINE
# ============================================================

baseline = generate_baseline_results(state)

assert baseline["status"] == "complete"

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

print("\n✅ Baseline results generated")


# ============================================================
# 4. RECOMMEND EXERCISES
# ============================================================

recommendation_result = recommend_exercises(state)

print("\n" + "=" * 70)
print("EXERCISE RECOMMENDATIONS")
print("=" * 70)

print(recommendation_result)


assert state["recommended_exercises"] is not None
assert len(state["recommended_exercises"]) > 0

print(
    "\nRecommended exercises:",
    len(state["recommended_exercises"])
)

print("✅ Exercise recommendations generated")


# ============================================================
# 5. START EXERCISE PHASE
# ============================================================

exercise_start = start_exercise_phase(state)

print("\n" + "=" * 70)
print("START EXERCISE PHASE")
print("=" * 70)

print(exercise_start)

assert state["phase"] == "exercises"

print("\nPhase:", state["phase"])
print("✅ Exercise phase started")


# ============================================================
# 6. INSPECT RECOMMENDED EXERCISES
# ============================================================

print("\n" + "=" * 70)
print("RECOMMENDED EXERCISES")
print("=" * 70)

for index, exercise in enumerate(
    state["recommended_exercises"],
    start=1
):

    print(f"\nExercise {index}")
    print("-" * 50)
    print(exercise)


# ============================================================
# 7. COMPLETE FIRST EXERCISE
# ============================================================

first_exercise = state["recommended_exercises"][0]
first_dimension = first_exercise["dimension"]

print("\n" + "=" * 70)
print("COMPLETE FIRST EXERCISE")
print("=" * 70)

print("Exercise:", first_exercise["title"])
print("Dimension:", first_dimension)

completion_result = complete_exercise(
    state,
    first_dimension
)

print(completion_result)

assert completion_result["status"] == "complete"
assert first_dimension in state["completed_exercises"]

print("\nCompleted exercises:")
print(len(state["completed_exercises"]))

print("Completed dimensions:")
print(state["completed_exercises"])

print("✅ First exercise completed")


# ============================================================
# 8. FINISH EXERCISE PHASE
# ============================================================

finish_result = finish_exercise_phase(state)

print("\n" + "=" * 70)
print("FINISH EXERCISE PHASE")
print("=" * 70)

print(finish_result)

assert finish_result["status"] == "ready_for_reassessment"

print("\nCompleted exercises:")
print(
    finish_result["completed_exercises"],
    "/",
    finish_result["total_exercises"]
)

assert finish_result["completed_exercises"] == 1
assert finish_result["total_exercises"] == 3

print("✅ Exercise phase finished")

# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("🎉 EXERCISE PHASE TEST PASSED")
print("=" * 70)