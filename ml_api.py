"""
JSON API wrapper for the ML modules.
Runs on port 5000. Called by the main FastAPI backend.
Original app.py (HTML UI) is untouched.
"""
import uuid
from flask import Flask, request, jsonify

from shared_utils.preprocessing import preprocess_text
from neuroticism_module.neuroticism_model import predict_neuroticism

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
)

app = Flask(__name__)
conversation_states = {}


def _next_question(result):
    """Her engine puts the next question under 'question' or 'next_question'."""
    return result.get("question") or result.get("next_question")


# ================= TEXT ANALYSIS =================

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    return jsonify({"neuroticism": predict_neuroticism(text)})


# ================= CHATBOT =================

@app.route("/api/chatbot/start", methods=["POST"])
def api_chatbot_start():
    state = create_conversation_state()
    start_result = start_conversation(state)
    conversation_id = str(uuid.uuid4())
    conversation_states[conversation_id] = state

    return jsonify({
        "conversation_id": conversation_id,
        "message": start_result.get("message"),
        "question": _next_question(start_result),
        "phase": state.get("phase"),
    })


@app.route("/api/chatbot/message", methods=["POST"])
def api_chatbot_message():
    data = request.get_json(silent=True) or {}
    conversation_id = data.get("conversation_id")
    user_message = (data.get("message") or "").strip()

    state = conversation_states.get(conversation_id)
    if not state:
        return jsonify({"error": "Conversation not found"}), 404
    if not user_message:
        return jsonify({"error": "Missing message"}), 400

    # Only these phases accept text input
    if state["phase"] not in ("initial_assessment", "reassessment"):
        return jsonify({"error": f"Cannot send text in phase '{state['phase']}'"}), 400

    result = chatbot_turn(state, user_response=user_message)

    # ===== If initial assessment JUST finished, generate baseline =====
    baseline_results = None
    if state["phase"] == "assessment_complete":
        # Trigger a follow-up turn to populate state['baseline_results']
        if not state.get("baseline_results"):
            chatbot_turn(state)

        raw = state.get("baseline_results")
        if raw:
            # Wrap so frontend can do `baseline_results.results`
            baseline_results = {"results": raw}

    # ===== If reassessment JUST finished, generate comparison + summary =====
    comparison = None
    summary = None
    progress_message = None
    if state["phase"] == "reassessment_complete":
        followup = chatbot_turn(state)
        comparison = followup.get("comparison") or state.get("comparison_results")
        summary = followup.get("summary") or state.get("progress_summary")
        progress_message = followup.get("progress_message") or state.get("progress_message")

    return jsonify({
        "conversation_id": conversation_id,
        "phase": state.get("phase"),
        "message": result.get("message"),
        "question": _next_question(result),
        "baseline_results": baseline_results,
        "comparison": comparison,
        "summary": summary,
        "progress_message": progress_message,
        "result": result,
    })


@app.route("/api/chatbot/action", methods=["POST"])
def api_chatbot_action():
    """
    Handle button actions:
      - start_exercises
      - complete_exercise (needs `dimension`)
      - finish_exercises
      - start_reassessment
    """
    data = request.get_json(silent=True) or {}
    conversation_id = data.get("conversation_id")
    action = data.get("action")
    dimension = data.get("dimension")

    if not conversation_id:
        return jsonify({"error": "Missing conversation_id"}), 400
    if not action:
        return jsonify({"error": "Missing action"}), 400

    state = conversation_states.get(conversation_id)
    if not state:
        return jsonify({"error": "Conversation not found"}), 404

    result = chatbot_turn(state, action=action, dimension=dimension)

    return jsonify({
        "conversation_id": conversation_id,
        "phase": state.get("phase"),
        "status": result.get("status"),
        "message": result.get("message"),
        "question": _next_question(result),
        "recommendations": result.get("recommendations") or state.get("recommended_exercises", []),
        "completed_exercises": state.get("completed_exercises", []),
        "total_exercises": len(state.get("recommended_exercises", [])),
        "comparison": result.get("comparison") or state.get("comparison_results"),
        "summary": result.get("summary") or state.get("progress_summary"),
        "progress_message": result.get("progress_message") or state.get("progress_message"),
        "result": result,
    })


# ================= HEALTH =================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ml-api"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)