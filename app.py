
from flask import Flask, render_template, request, session

from shared_utils.preprocessing import preprocess_text

from emotion_module.emotion_model import detect_emotions
from toxicity_module.toxicity_model import detect_toxicity
from sentiment_module.sentiment_model import detect_sentiment
from neuroticism_module.neuroticism_model import predict_neuroticism

import uuid

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
    generate_progress_message
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"

conversation_states = {}

# ============================================================
# MAIN TEXT ANALYSIS PAGE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        text = request.form["text"]

        processed_text = preprocess_text(text)

        result = {
            "emotion": detect_emotions(processed_text),
            "toxicity": detect_toxicity(processed_text),
            "sentiment": detect_sentiment(processed_text),
            "neuroticism": predict_neuroticism(text)
        }

    return render_template(
        "index.html",
        result=result
    )


# ============================================================
# START CHATBOT
# ============================================================

@app.route("/chatbot", methods=["GET"])
def chatbot_page():

    state = create_conversation_state()

    start_result = start_conversation(state)

    conversation_id = str(uuid.uuid4())

    conversation_states[conversation_id] = state
    session["conversation_id"] = conversation_id
    
    return render_template(
        "chatbot.html",
        message=start_result.get("message"),
        question=start_result.get("question"),
        state=state,
        result=start_result
    )


# ============================================================
# CHATBOT MESSAGE HANDLER
# ============================================================
@app.route("/chatbot", methods=["POST"])
def chatbot_message():
    conversation_id = session.get("conversation_id")

    state = conversation_states.get(conversation_id)



    # --------------------------------------------------------
    # START SESSION IF NONE EXISTS
    # --------------------------------------------------------

    if state is None:

     state = create_conversation_state()
     start_conversation(state)

    conversation_id = str(uuid.uuid4())

    conversation_states[conversation_id] = state
    session["conversation_id"] = conversation_id

    user_message = request.form.get("message", "").strip()

    # --------------------------------------------------------
    # EMPTY MESSAGE
    # --------------------------------------------------------

    if not user_message:

        return render_template(
            "chatbot.html",
            message="Please enter a response.",
            question=state.get("current_question"),
            state=state,
            result=None
        )

    # ========================================================
    # INITIAL ASSESSMENT
    # ========================================================

    if state["phase"] == "initial_assessment":

        result = chatbot_turn(
            state,
            user_message
        )

        print("\n========== INITIAL ASSESSMENT ==========")
        print(result)
        print("=========================================\n")

        # ----------------------------------------------------
        # CHECK IF ASSESSMENT IS COMPLETE
        # ----------------------------------------------------

        if state["phase"] == "assessment_complete":

            baseline_results = generate_baseline_results(state)

            print("\n========== BASELINE RESULTS ==========")
            print(baseline_results)
            print("======================================\n")

            result["baseline_results"] = baseline_results

            next_question = None

        else:

            next_question = (
                result.get("question")
                or result.get("next_question")
            )

        
        return render_template(
            "chatbot.html",
            message=result.get("message"),
            question=next_question,
            result=result,
            state=state
        )

    # ========================================================
    # EXERCISE PHASE
    # ========================================================

    elif state["phase"] == "exercises":

        if state.get("recommended_exercises"):

            incomplete_exercises = [
                exercise
                for exercise in state["recommended_exercises"]
                if not exercise["completed"]
            ]

            if incomplete_exercises:

                current_exercise = incomplete_exercises[0]

                completion_result = complete_exercise(
                    state,
                    current_exercise["dimension"]
                )

                print("\n========== EXERCISE COMPLETION ==========")
                print(completion_result)
                print("==========================================\n")

                # ------------------------------------------------
                # CHECK FOR MORE EXERCISES
                # ------------------------------------------------

                remaining = [
                    exercise
                    for exercise in state["recommended_exercises"]
                    if not exercise["completed"]
                ]

                if remaining:

                    next_exercise = remaining[0]

                    

                    return render_template(
                        "chatbot.html",
                        message=(
                            f"Great! You've completed "
                            f"'{current_exercise['title']}'. "
                            f"Let's move to the next exercise."
                        ),
                        exercise=next_exercise,
                        state=state,
                        result=completion_result
                    )

                # ------------------------------------------------
                # ALL EXERCISES COMPLETE
                # ------------------------------------------------

                finish_result = finish_exercise_phase(state)

                

                return render_template(
                    "chatbot.html",
                    message=finish_result.get("message"),
                    state=state,
                    result=finish_result
                )

    # ========================================================
    # REASSESSMENT
    # ========================================================

    elif state["phase"] == "reassessment":

        result = process_reassessment_turn(
            state,
            user_message
        )

        print("\n========== REASSESSMENT ==========")
        print(result)
        print("==================================\n")

        # ----------------------------------------------------
        # CHECK IF REASSESSMENT IS COMPLETE
        # ----------------------------------------------------

        if state["phase"] == "reassessment_complete":

            comparison = compare_baseline_reassessment(
                state
            )

            summary = generate_progress_summary(
                state
            )

            progress_message = generate_progress_message(
                state
            )

            result = {
                "status": "complete",
                "phase": "reassessment_complete",
                "comparison": comparison,
                "summary": summary,
                "progress_message": progress_message
            }

            

            return render_template(
                "chatbot.html",
                message=progress_message,
                question=None,
                result=result,
                state=state
            )

        # ----------------------------------------------------
        # REASSESSMENT STILL IN PROGRESS
        # ----------------------------------------------------

        next_question = (
            result.get("question")
            or result.get("next_question")
        )

      

        return render_template(
            "chatbot.html",
            message=result.get("message"),
            question=next_question,
            result=result,
            state=state
        )

    # ========================================================
    # REASSESSMENT COMPLETE
    # ========================================================

    elif state["phase"] == "reassessment_complete":

        comparison = compare_baseline_reassessment(
            state
        )

        summary = generate_progress_summary(
            state
        )

        progress_message = generate_progress_message(
            state
        )

        result = {
            "status": "complete",
            "phase": "reassessment_complete",
            "comparison": comparison,
            "summary": summary,
            "progress_message": progress_message
        }

       

        return render_template(
            "chatbot.html",
            message=progress_message,
            question=None,
            result=result,
            state=state
        )

    # # ========================================================
    # # READY FOR REASSESSMENT
    # # ========================================================

    # elif state["phase"] == "ready_for_reassessment":

    #     session["chatbot_state"] = state
    #     session.modified = True

    #     return render_template(
    #         "chatbot.html",
    #         message=(
    #             "You've completed your personalized exercises. "
    #             "You're now ready to reassess your progress."
    #         ),
    #         question=None,
    #         result={
    #             "phase": "ready_for_reassessment"
    #         },
    #         state=state
    #     )

    # ========================================================
    # FALLBACK
    # ========================================================

    return render_template(
        "chatbot.html",
        message="Let's continue.",
        question=state.get("current_question"),
        state=state,
        result=None
    )
    
# ============================================================
# START EXERCISE PHASE
# ============================================================

@app.route("/chatbot/exercises", methods=["GET"])
def chatbot_exercises():

    conversation_id = session.get("conversation_id")
    state = conversation_states.get(conversation_id)

    if state is None:
        return "No active chatbot session.", 400

    # --------------------------------------------------------
    # Generate personalized exercises
    # --------------------------------------------------------

    recommendation_result = recommend_exercises(state)

    print("\n========== RECOMMENDED EXERCISES ==========")

    recommended = recommendation_result.get(
        "recommendations",
        []
    )

    for exercise in recommended:
        print(
            exercise["dimension"],
            "→",
            exercise["title"]
        )

    print("============================================\n")

    # --------------------------------------------------------
    # Start exercise phase
    # --------------------------------------------------------

    result = start_exercise_phase(state)

   

    current_exercise = None

    if state.get("recommended_exercises"):

        incomplete = [
            exercise
            for exercise in state["recommended_exercises"]
            if not exercise["completed"]
        ]

        if incomplete:
            current_exercise = incomplete[0]

    return render_template(
        "chatbot.html",
        message=result.get("message"),
        exercise=current_exercise,
        result=result,
        state=state
    )


# ============================================================
# START REASSESSMENT
# ============================================================

@app.route("/chatbot/reassessment", methods=["GET"])
def chatbot_reassessment():

    conversation_id = session.get("conversation_id")
    state = conversation_states.get(conversation_id)

    if state is None:

        return "No active chatbot session.", 400

    # Start reassessment
    start_result = start_reassessment(state)

    # Begin asking reassessment questions
    begin_result = begin_reassessment(state)

    

    question = (
        begin_result.get("question")
        or start_result.get("question")
        or state.get("current_question")
    )

    message = (
        begin_result.get("message")
        or start_result.get("message")
    )

    return render_template(
        "chatbot.html",
        message=message,
        question=question,
        result=begin_result,
        state=state
    )


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)

