# Production chatbot engine extracted from the verified notebook.
# Colab/Drive mounts and notebook test cells have been removed.

import os
import re
import uuid
from datetime import datetime

from neuroticism_module.neuroticism_model import predict_neuroticism

DIMENSIONS = ['future_worry', 'rumination', 'uncertainty', 'overthinking', 'social_evaluation', 'self_doubt', 'emotional_reactivity', 'worry_persistence']

QUESTION_BANK = {'future_worry': ['When you have something important coming up, do you usually prepare for it and move on, or keep imagining things that could go wrong?', 'How often do you find yourself worrying about what might happen in the future?', 'When you think about an upcoming event, do you expect things to go smoothly or focus on possible problems?'], 'rumination': ['When something embarrassing or unpleasant happens, what usually happens in your mind afterward?', 'Do you often keep thinking about something that happened even after it is over?', 'When you make a mistake, how long do you usually continue thinking about it?'], 'uncertainty': ['How do you usually feel when you do not know what is going to happen?', 'Do situations without clear answers make you feel uncomfortable or worried?', 'When you have to wait for an uncertain outcome, what usually goes through your mind?'], 'overthinking': ['Do you often analyze a situation repeatedly before making a decision?', 'When you have to make a choice, do you keep thinking about different possibilities even after deciding?', 'Do you sometimes find it difficult to stop your thoughts once you start analyzing something?'], 'social_evaluation': ['How much do you worry about what other people think of you?', 'After talking to someone, do you sometimes wonder whether you said or did something wrong?', 'How do you usually feel when you think other people might be judging you?'], 'self_doubt': ['How often do you question whether you are capable of doing something well?', 'When you receive a difficult task, do you usually trust yourself or worry that you might fail?', 'Do you often compare your abilities with other people and feel unsure about yourself?'], 'emotional_reactivity': ['How strongly do you usually react when something stressful or upsetting happens?', 'When something goes wrong, how difficult is it for you to calm yourself down?', 'Do small stressful events sometimes affect your mood more than you expect?'], 'worry_persistence': ['Once you start worrying about something, how difficult is it for you to stop worrying?', 'Do your worries sometimes continue even when you know there is nothing you can do about the situation?', 'How long do your worries usually stay on your mind after the stressful situation has passed?']}

RESPONSE_TYPES = {'relevant', 'unclear', 'neutral'}

MIN_EVIDENCE_PER_DIMENSION = 2

EXERCISE_BANK = {'future_worry': {'title': 'Future Worry Reset', 'description': 'Write down one thing you are worried might happen. Then separate what you can control from what you cannot control.', 'activity': 'Ask yourself: What is one realistic action I can take right now?'}, 'rumination': {'title': 'Thought Release', 'description': 'Notice a past event that keeps returning to your mind. Write down what happened and what you learned from it.', 'activity': 'After writing it down, remind yourself that the event is already over.'}, 'uncertainty': {'title': 'Uncertainty Practice', 'description': 'Choose one small situation where the outcome is unknown and practice allowing yourself to wait without repeatedly checking.', 'activity': 'Notice the uncertainty without trying to immediately solve it.'}, 'overthinking': {'title': 'Decision Stop Point', 'description': 'Choose one decision you are currently overanalyzing. List the most important facts and give yourself a reasonable time limit for deciding.', 'activity': 'When the time limit ends, make the best decision you can with the information available.'}, 'social_evaluation': {'title': 'Social Judgment Check', 'description': 'Think of a recent situation where you worried about what someone else thought of you.', 'activity': 'Ask yourself: What evidence do I actually have about their opinion?'}, 'self_doubt': {'title': 'Self-Confidence Evidence', 'description': 'Write down three things you have successfully handled, even if they seem small.', 'activity': 'Use these examples as evidence that one difficult task does not automatically mean you will fail.'}, 'emotional_reactivity': {'title': 'Pause and Calm', 'description': 'When you notice a strong emotional reaction, pause before responding.', 'activity': 'Take several slow breaths and identify the emotion you are feeling before deciding what to do next.'}, 'worry_persistence': {'title': 'Worry Time Boundary', 'description': 'When a worry keeps returning, write it down instead of repeatedly thinking about it.', 'activity': 'Set aside a short period later to review the worry, then return your attention to the present activity.'}}

TOP_N_EXERCISES = 3

def create_conversation_state():
    """
    Create a fresh state for one chatbot conversation.

    The state supports:
    - Chatbot-initiated conversation
    - Initial assessment
    - 8 assessment dimensions
    - Neutral/unclear response routing
    - Baseline results
    - Coping/healing phase
    - Reassessment
    - Before/after comparison
    """
    state = {'session_id': str(uuid.uuid4()), 'created_at': datetime.now().isoformat(), 'phase': 'initial_assessment', 'turn_count': 0, 'current_dimension': None, 'current_question': None, 'questions_asked': [], 'conversation_history': [], 'last_response_type': None, 'last_analysis': None, 'dimensions': {dimension: {'responses': [], 'probabilities': [], 'evidence_count': 0, 'score': None, 'status': 'not_started'} for dimension in DIMENSIONS}, 'baseline_results': None, 'assessment_complete': False, 'recommended_exercises': [], 'completed_exercises': [], 'reassessment_results': None, 'reassessment_complete': False, 'comparison_results': None}
    return state

# def route_response(user_response):
#     """
#     Route a user's response into one of three categories.

#     relevant -> response can be analyzed for the assessment
#     unclear  -> response needs clarification
#     neutral  -> understandable but unrelated to the assessment

#     IMPORTANT:
#     Neutral responses NEVER contribute evidence.
#     """
#     if not isinstance(user_response, str):
#         return 'unclear'
#     response = user_response.strip()
#     if not response:
#         return 'unclear'
#     response_lower = response.lower()
#     response_lower = response_lower.replace('’', "'").replace('‘', "'")
#     normalized_response = re.sub("[^\\w\\s']", '', response_lower)
#     normalized_response = re.sub('\\s+', ' ', normalized_response).strip()
#     unclear_responses = {'idk', "i don't know", 'dont know', "don't know", 'not sure', 'maybe', 'perhaps', 'no idea', 'nothing'}
#     if normalized_response in unclear_responses:
#         return 'unclear'
#     assessment_phrases = {'worry about the future', 'worried about the future', 'worry about what might happen', 'worried about what might happen', 'what could go wrong', 'what might go wrong', 'possible problems', 'keep thinking about', 'keeps thinking about', 'think about it again', 'thinking about it again', 'replay it in my mind', 'replay it in my head', 'think about my mistakes', 'thinking about my mistakes', "don't know what will happen", 'do not know what will happen', 'uncertain about', 'uncertain situation', 'uncertain outcome', 'waiting for an outcome', 'overthink', 'overthinking', 'think about it repeatedly', 'analyze it repeatedly', 'analyze things repeatedly', 'keep analyzing', 'different possibilities', 'what other people think', 'what people think of me', 'what others think', 'people judging me', 'being judged', 'judge me', 'said something wrong', 'question whether i can', 'question if i can', 'question my ability', 'not capable', "don't think i can", 'do not think i can', 'not good enough', 'doubt myself', 'doubt my abilities', 'lack confidence', 'worried that i might fail', 'worry that i might fail', 'react strongly', 'strong emotional reaction', 'difficult to calm down', 'hard to calm down', 'get very upset', 'stress affects me', 'stressful things affect me', 'affects my mood', "can't stop worrying", 'cannot stop worrying', 'keep worrying', 'keeps worrying', 'worry stays on my mind', 'worries stay on my mind', 'worry for hours', 'worry for days', 'worry for a long time'}
#     if any((phrase in normalized_response for phrase in assessment_phrases)):
#         return 'relevant'
#     assessment_keywords = {'worry', 'worried', 'future', 'happen', 'upcoming', 'risk', 'think', 'thinking', 'thought', 'thoughts', 'mistake', 'mistakes', 'remember', 'embarrassing', 'replay', 'uncertain', 'uncertainty', 'unknown', 'unsure', 'outcome', 'waiting', 'overthink', 'overthinking', 'analyze', 'analysis', 'decision', 'decide', 'possibilities', 'options', 'people', 'others', 'judge', 'judging', 'judgment', 'opinion', 'social', 'myself', 'ability', 'abilities', 'capable', 'failure', 'fail', 'confidence', 'confident', 'compare', 'doubt', 'question', 'stress', 'stressful', 'upset', 'angry', 'anger', 'sad', 'emotion', 'emotional', 'calm', 'mood', 'continue', 'continues', 'hours', 'days', 'long'}
#     if any((keyword in normalized_response for keyword in assessment_keywords)):
#         return 'relevant'
#     return 'neutral'


def analyze_response(user_response, response_type):
    """
    Analyze a routed user response using the Neuroticism model.
    """

    result = predict_neuroticism(user_response)

    probability = result["neurotic_probability"] / 100.0
    prediction = 1 if result["prediction"] == "Neurotic" else 0

    return {
        "probability": probability,
        "prediction": prediction,
        "response_type": response_type
    }
    
FREQUENCY_RESPONSES = {
    'always',
    'usually',
    'mostly',
    'often',
    'sometimes',
    'rarely',
    'never',
    'frequently',
    'occasionally',
    'constantly',
    'hardly ever',
    'almost always',
    'almost never',
    'most of the time',
    'a lot',
    'quite often',
    'very often',
    'not often'
}


DIMENSION_RESPONSE_KEYWORDS = {

    'future_worry': {
        'future',
        'upcoming',
        'happen',
        'happens',
        'worry',
        'worried',
        'worrying',
        'problem',
        'problems',
        'wrong',
        'risk',
        'prepare',
        'preparing'
    },

    'rumination': {
        'afterward',
        'after',
        'embarrassing',
        'unpleasant',
        'mistake',
        'mistakes',
        'remember',
        'replay',
        'replaying',
        'cry',
        'crying',
        'cried',
        'sad',
        'upset',
        'regret',
        'thought',
        'thoughts',
        'thinking',
        'felt',
        'feel',
        'feeling'
    },

    'uncertainty': {
        'uncertain',
        'uncertainty',
        'unknown',
        'unsure',
        'outcome',
        'waiting',
        'wait',
        'answers',
        'answer',
        'clear',
        'worry',
        'worried',
        'uncomfortable'
    },

    'overthinking': {
        'analyze',
        'analyzing',
        'analysis',
        'decision',
        'decide',
        'possibilities',
        'options',
        'repeatedly',
        'overthink',
        'overthinking',
        'thoughts',
        'thinking',
        'choice',
        'choices'
    },

    'social_evaluation': {
        'people',
        'others',
        'judge',
        'judging',
        'judgment',
        'opinion',
        'embarrassed',
        'said',
        'wrong',
        'social',
        'think',
        'thinking'
    },

    'self_doubt': {
        'capable',
        'ability',
        'abilities',
        'fail',
        'failure',
        'confidence',
        'confident',
        'doubt',
        'compare',
        'task',
        'difficult',
        'good',
        'better',
        'worse'
    },

    'emotional_reactivity': {
        'stress',
        'stressful',
        'upset',
        'angry',
        'anger',
        'sad',
        'emotion',
        'emotional',
        'calm',
        'mood',
        'cry',
        'crying',
        'react',
        'reaction',
        'feel',
        'feeling'
    },

    'worry_persistence': {
        'worry',
        'worried',
        'worrying',
        'stop',
        'continue',
        'continues',
        'hours',
        'days',
        'long',
        'mind',
        'keep',
        'keeps'
    }
}



def route_response(user_response, current_dimension=None, current_question=None):
    """
    Classify the user's response.

    IMPORTANT:
    This function only decides the response TYPE.
    It does NOT decide whether the next question should be asked.

    Response types:
        relevant -> analyze with neuroticism model
        unclear  -> understandable as an answer type, but needs more detail
        neutral  -> not sufficiently related to the assessment

    Every response will still advance to the next question.
    """

    # ---------------------------------------------------------
    # 1. Invalid / empty response
    # ---------------------------------------------------------

    if not isinstance(user_response, str):
        return 'unclear'

    response = user_response.strip()

    if not response:
        return 'unclear'

    # ---------------------------------------------------------
    # 2. Normalize text
    # ---------------------------------------------------------

    response_lower = response.lower()

    response_lower = (
        response_lower
        .replace('’', "'")
        .replace('‘', "'")
    )

    normalized_response = re.sub(
        r"[^\w\s']",
        '',
        response_lower
    )

    normalized_response = re.sub(
        r'\s+',
        ' ',
        normalized_response
    ).strip()

    # ---------------------------------------------------------
    # 3. Explicit unclear responses
    # ---------------------------------------------------------

    unclear_responses = {
        'idk',
        'i dont know',
        "i don't know",
        'dont know',
        "don't know",
        'not sure',
        'no idea',
        'maybe',
        'perhaps',
        'cannot say',
        "can't say",
        'i cannot say',
        "i can't say",
        'unsure'
    }

    if normalized_response in unclear_responses:
        return 'unclear'

    # ---------------------------------------------------------
    # 4. Very common short answers
    # ---------------------------------------------------------

    # These are valid answers for many assessment questions.
    frequency_responses = {
        'always',
        'usually',
        'mostly',
        'often',
        'sometimes',
        'rarely',
        'never',
        'frequently',
        'occasionally',
        'constantly',
        'hardly ever',
        'almost always',
        'almost never',
        'most of the time',
        'a lot',
        'quite often',
        'very often',
        'not often'
    }

    if normalized_response in frequency_responses:
        return 'relevant'

    # ---------------------------------------------------------
    # 5. Yes / No answers
    # ---------------------------------------------------------

    binary_answers = {
        'yes',
        'yeah',
        'yep',
        'yup',
        'no',
        'nope',
        'not really',
        'definitely',
        'definitely not'
    }

    if normalized_response in binary_answers:

        # Yes/no is a valid answer when the question itself
        # is asking something in a yes/no form.
        if current_question:

            question_lower = current_question.lower().strip()

            binary_starters = (
                'do ',
                'does ',
                'did ',
                'can ',
                'could ',
                'is ',
                'are ',
                'was ',
                'were '
            )

            if question_lower.startswith(binary_starters):
                return 'relevant'

        # Even if the question is not perfectly binary,
        # treat a short yes/no answer as relevant rather
        # than forcing the user to write a long response.
        return 'relevant'

    # ---------------------------------------------------------
    # 6. Dimension-specific vocabulary
    # ---------------------------------------------------------

    dimension_keywords = {

        'future_worry': {
            'future',
            'upcoming',
            'happen',
            'happens',
            'happened',
            'worry',
            'worried',
            'worrying',
            'problem',
            'problems',
            'wrong',
            'risk',
            'prepare',
            'preparing',
            'event',
            'events',
            'tomorrow',
            'later'
        },

        'rumination': {
            'afterward',
            'after',
            'embarrassing',
            'unpleasant',
            'mistake',
            'mistakes',
            'remember',
            'remembering',
            'replay',
            'replaying',
            'cry',
            'crying',
            'cried',
            'sad',
            'upset',
            'regret',
            'regretting',
            'thought',
            'thoughts',
            'thinking',
            'felt',
            'feel',
            'feeling',
            'mind',
            'past',
            'again'
        },

        'uncertainty': {
            'uncertain',
            'uncertainty',
            'unknown',
            'unsure',
            'outcome',
            'waiting',
            'wait',
            'answers',
            'answer',
            'clear',
            'unclear',
            'worry',
            'worried',
            'uncomfortable',
            'confused',
            'confusion',
            'unknown'
        },

        'overthinking': {
            'analyze',
            'analyzing',
            'analysis',
            'decision',
            'decide',
            'possibilities',
            'possibility',
            'options',
            'option',
            'repeatedly',
            'overthink',
            'overthinking',
            'thoughts',
            'thinking',
            'choice',
            'choices',
            'mind',
            'consider',
            'considering'
        },

        'social_evaluation': {
            'people',
            'others',
            'judge',
            'judging',
            'judgment',
            'opinion',
            'opinions',
            'embarrassed',
            'embarrassing',
            'said',
            'say',
            'wrong',
            'social',
            'think',
            'thinking',
            'friends',
            'everyone',
            'public'
        },

        'self_doubt': {
            'capable',
            'ability',
            'abilities',
            'fail',
            'failure',
            'confidence',
            'confident',
            'doubt',
            'doubtful',
            'compare',
            'comparison',
            'task',
            'difficult',
            'good',
            'better',
            'worse',
            'myself',
            'myself',
            'believe'
        },

        'emotional_reactivity': {
            'stress',
            'stressed',
            'stressful',
            'upset',
            'angry',
            'anger',
            'sad',
            'sadness',
            'emotion',
            'emotional',
            'calm',
            'mood',
            'cry',
            'crying',
            'react',
            'reaction',
            'feel',
            'feeling',
            'feelings',
            'frustrated',
            'frustration'
        },

        'worry_persistence': {
            'worry',
            'worried',
            'worrying',
            'stop',
            'continue',
            'continues',
            'continued',
            'hours',
            'days',
            'long',
            'mind',
            'keep',
            'keeps',
            'stays',
            'stayed',
            'cannot stop',
            "can't stop"
        }
    }

    # ---------------------------------------------------------
    # 7. Use the CURRENT dimension
    # ---------------------------------------------------------

    if current_dimension in dimension_keywords:

        keywords = dimension_keywords[current_dimension]

        words = set(normalized_response.split())

        # Direct word match
        if words.intersection(keywords):
            return 'relevant'

        # Phrase match
        for keyword in keywords:
            if ' ' in keyword and keyword in normalized_response:
                return 'relevant'

    # ---------------------------------------------------------
    # 8. General meaningful assessment vocabulary
    # ---------------------------------------------------------

    general_keywords = {
        'feel',
        'feeling',
        'felt',
        'think',
        'thinking',
        'thought',
        'thoughts',
        'mind',
        'worry',
        'worried',
        'stress',
        'stressed',
        'upset',
        'sad',
        'angry',
        'calm',
        'problem',
        'problems',
        'often',
        'usually',
        'sometimes',
        'mostly',
        'always',
        'never',
        'rarely',
        'frequently',
        'yes',
        'no',
        'good',
        'bad',
        'difficult',
        'easy',
        'hard',
        'comfortable',
        'uncomfortable'
    }

    words = set(normalized_response.split())

    if words.intersection(general_keywords):
        return 'relevant'

    # ---------------------------------------------------------
    # 9. Fallback
    # ---------------------------------------------------------

    return 'neutral'


def add_response(state, dimension, user_response, analysis_result):
    """
    Store a response as evidence for a specific dimension.

    Only relevant responses are stored.
    Neutral and unclear responses never increase evidence.
    """
    if dimension not in state['dimensions']:
        raise ValueError(f'Unknown dimension: {dimension}')
    response_type = analysis_result['response_type']
    if response_type != 'relevant':
        return False
    probability = analysis_result['probability']
    dimension_data = state['dimensions'][dimension]
    dimension_data['responses'].append(user_response)
    dimension_data['probabilities'].append(probability)
    dimension_data['evidence_count'] += 1
    dimension_data['status'] = 'in_progress'
    return True

def update_dimension_score(state, dimension):
    """
    Calculate the current score for a dimension.

    IMPORTANT:
    A dimension is NOT considered complete because it has
    two relevant answers.

    Completion is controlled by the question flow:
    all questions for the dimension must be asked.

    Score:
        average of probabilities from relevant responses only.

    If there are no relevant responses:
        score = None
    """

    if dimension not in state['dimensions']:
        raise ValueError(f'Unknown dimension: {dimension}')

    dimension_data = state['dimensions'][dimension]

    probabilities = dimension_data['probabilities']

    # ---------------------------------------------------------
    # No relevant responses
    # ---------------------------------------------------------

    if not probabilities:

        dimension_data['score'] = None

        # Keep track of whether questions have started.
        if dimension_data['responses']:
            dimension_data['status'] = 'in_progress'
        else:
            dimension_data['status'] = 'not_started'

        return None

    # ---------------------------------------------------------
    # Calculate average probability
    # ---------------------------------------------------------

    score = sum(probabilities) / len(probabilities)

    dimension_data['score'] = float(score)

    # The dimension remains in progress until ALL questions
    # have been asked.
    dimension_data['status'] = 'in_progress'

    return float(score)

# def select_next_dimension(state):
#     """
#     Select the next dimension that still needs evidence.

#     During the initial assessment, dimensions are processed
#     in the predefined DIMENSIONS order.

#     Returns:
#         dimension name if more assessment is needed
#         None if all dimensions are complete
#     """
#     for dimension in DIMENSIONS:
#         dimension_data = state['dimensions'][dimension]
#         if dimension_data['status'] != 'complete':
#             return dimension
#     state['assessment_complete'] = True
#     state['phase'] = 'assessment_complete'
#     return None

def select_next_dimension(state):
    """
    Select the next dimension in the predefined order.

    A dimension is considered finished only when its
    questions have all been asked.

    The actual completion is handled by process_chat_turn()
    after select_question() returns None.
    """

    for dimension in DIMENSIONS:

        dimension_data = state['dimensions'][dimension]

        if dimension_data['status'] != 'complete':
            return dimension

    # ---------------------------------------------------------
    # All dimensions have been completed
    # ---------------------------------------------------------

    state['assessment_complete'] = True
    state['phase'] = 'assessment_complete'
    state['current_dimension'] = None
    state['current_question'] = None

    return None


def select_question(state, dimension):
    """
    Select the next unused question for a given dimension.

    Returns:
        The selected question, or None if all questions
        for the dimension have already been asked.
    """
    if dimension not in QUESTION_BANK:
        raise ValueError(f'Unknown dimension: {dimension}')
    asked_questions = set(state['questions_asked'])
    for question in QUESTION_BANK[dimension]:
        if question not in asked_questions:
            state['current_dimension'] = dimension
            state['current_question'] = question
            state['questions_asked'].append(question)
            return question
    return None

# def process_chat_turn(state, user_response):
#     """
#     Process one user response during the assessment.

#     Flow:
#         1. Route response
#         2. Handle unclear / neutral responses
#         3. Analyze relevant responses
#         4. Store evidence
#         5. Update dimension score
#         6. Decide whether to continue or move forward

#     Returns a consistent response dictionary.
#     """
#     if state['phase'] != 'initial_assessment':
#         return {'response_type': 'system', 'message': 'The initial assessment is not currently active.', 'analysis': None, 'dimension': state['current_dimension'], 'next_dimension': None, 'next_question': None}
#     current_dimension = state['current_dimension']
#     if current_dimension is None:
#         current_dimension = select_next_dimension(state)
#         if current_dimension is None:
#             return {'response_type': 'system', 'message': 'The initial assessment is complete.', 'analysis': None, 'dimension': None, 'next_dimension': None, 'next_question': None}
#         state['current_dimension'] = current_dimension
#     state['turn_count'] += 1
#     # response_type = route_response(user_response)
#     response_type = route_response(
#     user_response,
#     current_dimension=current_dimension,
#     current_question=state['current_question']
# )
#     state['last_response_type'] = response_type
#     state['conversation_history'].append({'turn': state['turn_count'], 'dimension': current_dimension, 'question': state['current_question'], 'user_response': user_response, 'response_type': response_type})
#     if response_type == 'unclear':
#         return {'response_type': 'unclear', 'message': 'Could you tell me a little more about that?', 'analysis': None, 'dimension': current_dimension, 'next_dimension': current_dimension, 'next_question': state['current_question']}
#     if response_type == 'neutral':
#         return {'response_type': 'neutral', 'message': "That's okay. Let's continue with the assessment.", 'analysis': None, 'dimension': current_dimension, 'next_dimension': current_dimension, 'next_question': state['current_question']}
#     analysis = analyze_response(user_response, response_type)
#     state['last_analysis'] = analysis
#     add_response(state, current_dimension, user_response, analysis)
#     dimension_score = update_dimension_score(state, current_dimension)
#     dimension_complete = state['dimensions'][current_dimension]['status'] == 'complete'
#     if not dimension_complete:
#         next_question = select_question(state, current_dimension)
#         return {'response_type': 'relevant', 'message': "Thank you. Let's continue.", 'analysis': analysis, 'dimension': current_dimension, 'dimension_score': dimension_score, 'dimension_complete': False, 'next_dimension': current_dimension, 'next_question': next_question}
#     next_dimension = select_next_dimension(state)
#     if next_dimension is None:
#         return {'response_type': 'relevant', 'message': 'Thank you. The initial assessment is complete.', 'analysis': analysis, 'dimension': current_dimension, 'dimension_score': dimension_score, 'dimension_complete': True, 'next_dimension': None, 'next_question': None}
#     next_question = select_question(state, next_dimension)
#     return {'response_type': 'relevant', 'message': "Thank you. Let's explore another area.", 'analysis': analysis, 'dimension': current_dimension, 'dimension_score': dimension_score, 'dimension_complete': True, 'next_dimension': next_dimension, 'next_question': next_question}


def process_chat_turn(state, user_response):
    """
    Process one user response during the initial assessment.

    IMPORTANT DESIGN:

    Every question is asked exactly once.

    For every answer:

        relevant
            -> analyze with neuroticism model
            -> store probability
            -> update dimension score
            -> move to next question

        unclear
            -> record response type
            -> no neuroticism score
            -> move to next question

        neutral
            -> record response type
            -> no neuroticism score
            -> move to next question

    The chatbot asks ALL questions from ALL dimensions.
    """

    # =========================================================
    # 1. CHECK PHASE
    # =========================================================

    if state['phase'] != 'initial_assessment':

        return {
            'response_type': 'system',
            'message': (
                'The initial assessment is not currently active.'
            ),
            'analysis': None,
            'dimension': state['current_dimension'],
            'next_dimension': None,
            'next_question': None
        }

    # =========================================================
    # 2. GET CURRENT DIMENSION
    # =========================================================

    current_dimension = state['current_dimension']

    if current_dimension is None:

        current_dimension = select_next_dimension(state)

        if current_dimension is None:

            return {
                'response_type': 'system',
                'message': (
                    'The initial assessment is complete.'
                ),
                'analysis': None,
                'dimension': None,
                'next_dimension': None,
                'next_question': None
            }

    # =========================================================
    # 3. GET CURRENT QUESTION
    # =========================================================

    current_question = state['current_question']

    if current_question is None:

        current_question = select_question(
            state,
            current_dimension
        )

        if current_question is None:

            # No questions remain in this dimension.
            state['dimensions'][current_dimension]['status'] = 'complete'

            next_dimension = select_next_dimension(state)

            if next_dimension is None:

                return {
                    'response_type': 'system',
                    'message': (
                        'The initial assessment is complete.'
                    ),
                    'analysis': None,
                    'dimension': current_dimension,
                    'next_dimension': None,
                    'next_question': None
                }

            next_question = select_question(
                state,
                next_dimension
            )

            return {
                'response_type': 'system',
                'message': (
                    "Let's continue with another area "
                    "of the assessment."
                ),
                'analysis': None,
                'dimension': current_dimension,
                'next_dimension': next_dimension,
                'next_question': next_question
            }

    # =========================================================
    # 4. INCREASE TURN COUNT
    # =========================================================

    state['turn_count'] += 1

    # =========================================================
    # 5. CLASSIFY RESPONSE
    # =========================================================

    response_type = route_response(
        user_response,
        current_dimension=current_dimension,
        current_question=current_question
    )

    state['last_response_type'] = response_type

    # =========================================================
    # 6. SAVE RESPONSE HISTORY
    # =========================================================

    state['conversation_history'].append({
        'turn': state['turn_count'],
        'speaker': 'user',
        'dimension': current_dimension,
        'question': current_question,
        'user_response': user_response,
        'response_type': response_type
    })

    # =========================================================
    # 7. RELEVANT RESPONSE
    # =========================================================

    analysis = None
    dimension_score = state['dimensions'][current_dimension]['score']

    if response_type == 'relevant':

        # -----------------------------------------------------
        # Run neuroticism model
        # -----------------------------------------------------

        analysis = analyze_response(
            user_response,
            response_type='relevant'
        )

        state['last_analysis'] = analysis

        # -----------------------------------------------------
        # Store relevant response
        # -----------------------------------------------------

        add_response(
            state,
            current_dimension,
            user_response,
            analysis
        )

        # -----------------------------------------------------
        # Update dimension score
        # -----------------------------------------------------

        dimension_score = update_dimension_score(
            state,
            current_dimension
        )

    # =========================================================
    # 8. UNCLEAR / NEUTRAL RESPONSE
    # =========================================================

    elif response_type in ('unclear', 'neutral'):

        # -----------------------------------------------------
        # Do NOT run the neuroticism model.
        # Do NOT add probability.
        #
        # But the question IS considered answered and
        # the chatbot MUST move forward.
        # -----------------------------------------------------

        state['last_analysis'] = None

    # =========================================================
    # 9. CHECK FOR ANOTHER QUESTION IN SAME DIMENSION
    # =========================================================

    next_question = select_question(
        state,
        current_dimension
    )

    if next_question is not None:

        return {
            'response_type': response_type,
            'message': (
                "Thank you. Let's continue."
            ),
            'analysis': analysis,
            'dimension': current_dimension,
            'dimension_score': dimension_score,
            'dimension_complete': False,
            'next_dimension': current_dimension,
            'next_question': next_question
        }

    # =========================================================
    # 10. ALL QUESTIONS FOR CURRENT DIMENSION ARE DONE
    # =========================================================

    state['dimensions'][current_dimension]['status'] = 'complete'

    # =========================================================
    # 11. MOVE TO NEXT DIMENSION
    # =========================================================

    next_dimension = select_next_dimension(state)

    # =========================================================
    # 12. ALL 8 DIMENSIONS ARE DONE
    # =========================================================

    if next_dimension is None:

        return {
            'response_type': response_type,
            'message': (
                'Thank you. The initial assessment is complete.'
            ),
            'analysis': analysis,
            'dimension': current_dimension,
            'dimension_score': dimension_score,
            'dimension_complete': True,
            'next_dimension': None,
            'next_question': None
        }

    # =========================================================
    # 13. START NEXT DIMENSION
    # =========================================================

    next_question = select_question(
        state,
        next_dimension
    )

    return {
        'response_type': response_type,
        'message': (
            "Thank you. Let's explore another area."
        ),
        'analysis': analysis,
        'dimension': current_dimension,
        'dimension_score': dimension_score,
        'dimension_complete': True,
        'next_dimension': next_dimension,
        'next_question': next_question
    }

def start_conversation(state):
    """
    Start a new chatbot assessment.

    The chatbot initiates the conversation by providing
    a greeting and the first assessment question.
    """
    if state['phase'] != 'initial_assessment':
        raise ValueError('Conversation cannot be started in the current phase.')
    first_dimension = select_next_dimension(state)
    if first_dimension is None:
        state['assessment_complete'] = True
        state['phase'] = 'assessment_complete'
        return {'message': 'The assessment is already complete.', 'dimension': None, 'question': None}
    first_question = select_question(state, first_dimension)
    state['conversation_history'].append({'turn': 0, 'speaker': 'chatbot', 'dimension': first_dimension, 'question': first_question, 'message': "Hi! I'd like to understand how you usually experience different situations. There are no right or wrong answers. Just answer as honestly as you can."})
    return {'message': "Hi! I'd like to understand how you usually experience different situations. There are no right or wrong answers. Just answer as honestly as you can.", 'dimension': first_dimension, 'question': first_question}

def generate_baseline_results(state):
    """
    Generate baseline results after all 24 questions
    have been answered.

    Each dimension score is the average neuroticism
    probability from its relevant responses.

    Dimensions without relevant evidence have score=None.

    The overall score is calculated from dimensions
    that have a valid numeric score.
    """

    if not state['assessment_complete']:

        return {
            'status': 'incomplete',
            'message': (
                'The initial assessment is not complete yet.'
            ),
            'results': None
        }

    results = {}

    valid_dimension_scores = []

    for dimension in DIMENSIONS:

        dimension_data = state['dimensions'][dimension]

        score = dimension_data.get('score')

        results[dimension] = {
            'score': score,
            'evidence_count': dimension_data['evidence_count'],
            'status': dimension_data['status'],
            'responses': dimension_data['responses'],
            'probabilities': dimension_data['probabilities']
        }

        if score is not None:
            valid_dimension_scores.append(
                float(score)
            )

    # --------------------------------------------------
    # Overall neuroticism score
    # --------------------------------------------------

    if valid_dimension_scores:

        overall_score = (
            sum(valid_dimension_scores)
            / len(valid_dimension_scores)
        )

    else:

        overall_score = None

    results['overall_neuroticism'] = {
        'score': overall_score,
        'dimensions_used': len(valid_dimension_scores),
        'total_dimensions': len(DIMENSIONS)
    }

    state['baseline_results'] = results

    return {
        'status': 'complete',
        'message': (
            'Baseline assessment results generated.'
        ),
        'results': results
    }

def recommend_exercises(state, top_n=TOP_N_EXERCISES):
    """
    Recommend exercises based on dimensions that have
    an actual calculated score.

    Dimensions with no relevant responses are not used
    for exercise ranking.
    """

    if not state['baseline_results']:

        return {
            'status': 'unavailable',
            'message': (
                'Baseline results are not available yet.'
            ),
            'recommendations': []
        }

    # ---------------------------------------------------------
    # Only use dimensions that have a numeric score
    # ---------------------------------------------------------

    scored_dimensions = [
        item
        for item in state['baseline_results'].items()
        if item[1]['score'] is not None
    ]

    # ---------------------------------------------------------
    # Sort by score
    # ---------------------------------------------------------

    ranked_dimensions = sorted(
        scored_dimensions,
        key=lambda item: item[1]['score'],
        reverse=True
    )

    recommendations = []

    for dimension, result in ranked_dimensions[:top_n]:

        exercise = EXERCISE_BANK[dimension]

        recommendations.append({
            'dimension': dimension,
            'score': result['score'],
            'title': exercise['title'],
            'description': exercise['description'],
            'activity': exercise['activity'],
            'completed': False
        })

    state['recommended_exercises'] = recommendations

    return {
        'status': 'complete',
        'message': (
            'Personalized exercises generated.'
        ),
        'recommendations': recommendations
    }

def complete_exercise(state, dimension):
    """
    Mark a recommended exercise as completed.
    """
    if not state['recommended_exercises']:
        return {'status': 'unavailable', 'message': 'No recommended exercises are available.'}
    for exercise in state['recommended_exercises']:
        if exercise['dimension'] == dimension:
            if exercise['completed']:
                return {'status': 'already_completed', 'message': 'This exercise has already been completed.'}
            exercise['completed'] = True
            if dimension not in state['completed_exercises']:
                state['completed_exercises'].append(dimension)
            return {'status': 'complete', 'message': f"Exercise '{exercise['title']}' marked as completed.", 'dimension': dimension, 'title': exercise['title']}
    return {'status': 'not_found', 'message': 'No recommended exercise found for this dimension.'}

def start_reassessment(state):
    """
    Prepare the chatbot for a second assessment while
    preserving the original baseline results.
    """
    if not state['assessment_complete']:
        return {'status': 'unavailable', 'message': 'Complete the initial assessment first.'}
    if not state['baseline_results']:
        return {'status': 'unavailable', 'message': 'Baseline results are not available.'}
    state['phase'] = 'reassessment'
    state['reassessment_complete'] = False
    state['reassessment_results'] = None
    state['current_dimension'] = None
    state['current_question'] = None
    state['reassessment_dimensions'] = {dimension: {'responses': [], 'probabilities': [], 'evidence_count': 0, 'score': None, 'status': 'not_started'} for dimension in DIMENSIONS}
    return {'status': 'ready', 'message': 'Reassessment is ready to begin.', 'phase': state['phase'], 'dimensions': state['reassessment_dimensions']}

def begin_reassessment(state):
    """
    Start the reassessment conversation after the
    reassessment state has been prepared.
    """
    if state['phase'] != 'reassessment':
        return {'status': 'unavailable', 'message': 'Reassessment has not been prepared yet.'}
    state['questions_asked'] = []
    first_dimension = DIMENSIONS[0]
    question = select_question(state, first_dimension)
    return {'status': 'started', 'message': "Welcome back. Let's check how things have changed since your initial assessment.", 'dimension': first_dimension, 'question': question}

def process_reassessment_turn(state, user_response):
    """
    Process one user response during reassessment.

    Reassessment follows the EXACT same question-flow logic
    as the initial assessment.

    For every question:
        relevant
            -> analyze with neuroticism model
            -> store probability
            -> update score
            -> move to next question

        unclear
            -> record response type
            -> no neuroticism score
            -> move to next question

        neutral
            -> record response type
            -> no neuroticism score
            -> move to next question

    IMPORTANT:
        Every question is asked exactly once.
        All 24 questions must be asked:
            8 dimensions × 3 questions.
    """

    # =========================================================
    # 1. CHECK PHASE
    # =========================================================

    if state['phase'] != 'reassessment':
        return {
            'status': 'unavailable',
            'message': 'The chatbot is not currently in reassessment.'
        }

    # =========================================================
    # 2. GET CURRENT DIMENSION
    # =========================================================

    current_dimension = state['current_dimension']

    if current_dimension is None:
        return {
            'status': 'complete',
            'message': 'Reassessment is already complete.'
        }

    # =========================================================
    # 3. GET CURRENT QUESTION
    # =========================================================

    current_question = state['current_question']

    if current_question is None:

        current_question = select_question(
            state,
            current_dimension
        )

        if current_question is None:

            # All questions for this dimension are complete.
            state['reassessment_dimensions'][
                current_dimension
            ]['status'] = 'complete'

            current_index = DIMENSIONS.index(
                current_dimension
            )

            # -------------------------------------------------
            # All dimensions completed
            # -------------------------------------------------

            if current_index == len(DIMENSIONS) - 1:

                state['reassessment_complete'] = True
                state['phase'] = 'reassessment_complete'
                state['current_dimension'] = None
                state['current_question'] = None

                return {
                    'status': 'reassessment_complete',
                    'message': (
                        'Thank you. The reassessment is now complete.'
                    )
                }

            # -------------------------------------------------
            # Move to next dimension
            # -------------------------------------------------

            next_dimension = DIMENSIONS[current_index + 1]

            state['current_dimension'] = next_dimension

            next_question = select_question(
                state,
                next_dimension
            )

            return {
                'status': 'next_dimension',
                'message': (
                    "Thank you. Let's explore another area."
                ),
                'dimension': next_dimension,
                'next_dimension': next_dimension,
                'question': next_question
            }

    # =========================================================
    # 4. CLASSIFY RESPONSE
    # =========================================================

    response_type = route_response(
        user_response,
        current_dimension=current_dimension,
        current_question=current_question
    )

    # =========================================================
    # 5. SAVE REASSESSMENT HISTORY
    # =========================================================

    state.setdefault(
        'reassessment_history',
        []
    )

    state['reassessment_history'].append({
        'turn': len(state['reassessment_history']) + 1,
        'dimension': current_dimension,
        'question': current_question,
        'user_response': user_response,
        'response_type': response_type
    })

    # =========================================================
    # 6. RELEVANT RESPONSE
    # =========================================================

    analysis = None
    probability = None

    if response_type == 'relevant':

        analysis = analyze_response(
            user_response,
            response_type='relevant'
        )

        probability = analysis['probability']

        dimension_data = (
            state['reassessment_dimensions']
            [current_dimension]
        )

        dimension_data['responses'].append(
            user_response
        )

        dimension_data['probabilities'].append(
            probability
        )

        dimension_data['evidence_count'] += 1

        # Calculate score from relevant responses only.
        dimension_data['score'] = (
            sum(dimension_data['probabilities'])
            /
            len(dimension_data['probabilities'])
        )

    # =========================================================
    # 7. UNCLEAR / NEUTRAL
    # =========================================================

    elif response_type in ('unclear', 'neutral'):

        # Do NOT run the neuroticism model.
        # Do NOT add probability.
        #
        # BUT the question has been answered.
        # Therefore we MUST move to the next question.

        analysis = None

    # =========================================================
    # 8. ASK NEXT QUESTION IN SAME DIMENSION
    # =========================================================

    next_question = select_question(
        state,
        current_dimension
    )

    if next_question is not None:

        return {
            'status': 'continue',
            'response_type': response_type,
            'analysis': analysis,
            'dimension': current_dimension,
            'probability': probability,
            'score': (
                state['reassessment_dimensions']
                [current_dimension]['score']
            ),
            'evidence_count': (
                state['reassessment_dimensions']
                [current_dimension]['evidence_count']
            ),
            'next_dimension': current_dimension,
            'question': next_question
        }

    # =========================================================
    # 9. ALL 3 QUESTIONS FOR CURRENT DIMENSION ARE DONE
    # =========================================================

    dimension_data = (
        state['reassessment_dimensions']
        [current_dimension]
    )

    dimension_data['status'] = 'complete'

    # =========================================================
    # 10. CHECK WHETHER ALL 8 DIMENSIONS ARE DONE
    # =========================================================

    current_index = DIMENSIONS.index(
        current_dimension
    )

    if current_index == len(DIMENSIONS) - 1:

        state['reassessment_complete'] = True
        state['phase'] = 'reassessment_complete'
        state['current_dimension'] = None
        state['current_question'] = None

        return {
            'status': 'reassessment_complete',
            'response_type': response_type,
            'analysis': analysis,
            'dimension': current_dimension,
            'probability': probability,
            'score': dimension_data['score'],
            'message': (
                'Thank you. The reassessment is now complete.'
            ),
            'question': None
        }

    # =========================================================
    # 11. MOVE TO NEXT DIMENSION
    # =========================================================

    next_dimension = DIMENSIONS[
        current_index + 1
    ]

    state['current_dimension'] = next_dimension

    next_question = select_question(
        state,
        next_dimension
    )

    return {
        'status': 'next_dimension',
        'response_type': response_type,
        'analysis': analysis,
        'dimension': current_dimension,
        'probability': probability,
        'score': dimension_data['score'],
        'next_dimension': next_dimension,
        'question': next_question
    }
def compare_baseline_reassessment(state):
    """
    Compare baseline scores with reassessment scores
    for all eight neuroticism dimensions.

    If a dimension has no valid score in either assessment,
    no numerical change is calculated for that dimension.
    """

    if not state.get('baseline_results'):
        return {
            'status': 'unavailable',
            'message': 'Baseline results are not available.',
            'comparison': []
        }

    if not state.get('reassessment_complete'):
        return {
            'status': 'unavailable',
            'message': 'Reassessment is not complete yet.',
            'comparison': []
        }

    comparison = []

    for dimension in DIMENSIONS:

        baseline_score = (
            state['baseline_results']
            [dimension]
            .get('score')
        )

        reassessment_score = (
            state['reassessment_dimensions']
            [dimension]
            .get('score')
        )

        # --------------------------------------------------
        # No valid score for this dimension
        # --------------------------------------------------

        if baseline_score is None or reassessment_score is None:

            comparison.append({
                'dimension': dimension,
                'baseline_score': baseline_score,
                'reassessment_score': reassessment_score,
                'change': None,
                'interpretation': 'insufficient_evidence'
            })

            continue

        # --------------------------------------------------
        # Both scores are valid
        # --------------------------------------------------

        change = (
            float(reassessment_score)
            - float(baseline_score)
        )

        if change < -0.05:
            interpretation = 'improved'

        elif change > 0.05:
            interpretation = 'increased'

        else:
            interpretation = 'stable'

        comparison.append({
            'dimension': dimension,
            'baseline_score': float(baseline_score),
            'reassessment_score': float(reassessment_score),
            'change': float(change),
            'interpretation': interpretation
        })

    state['comparison_results'] = comparison

    return {
        'status': 'complete',
        'message': (
            'Baseline and reassessment comparison generated.'
        ),
        'comparison': comparison
    }
def generate_progress_summary(state):
    """
    Generate an overall summary from valid baseline vs
    reassessment comparisons.

    Dimensions without scores are excluded from numerical
    change calculations.
    """

    if not state.get('comparison_results'):
        return {
            'status': 'unavailable',
            'message': 'Comparison results are not available.',
            'summary': None
        }

    valid_comparisons = [
        item
        for item in state['comparison_results']
        if item.get('change') is not None
    ]

    improved = [
        item
        for item in valid_comparisons
        if item['interpretation'] == 'improved'
    ]

    increased = [
        item
        for item in valid_comparisons
        if item['interpretation'] == 'increased'
    ]

    stable = [
        item
        for item in valid_comparisons
        if item['interpretation'] == 'stable'
    ]

    insufficient = [
        item
        for item in state['comparison_results']
        if item['interpretation'] == 'insufficient_evidence'
    ]

    # --------------------------------------------------
    # No dimensions have valid comparison scores
    # --------------------------------------------------

    if not valid_comparisons:

        summary = {
            'overall_status': 'insufficient_evidence',
            'average_change': None,
            'improved_dimensions': [],
            'increased_dimensions': [],
            'stable_dimensions': [],
            'insufficient_dimensions': [
                item['dimension']
                for item in insufficient
            ],
            'message': (
                'There was not enough comparable evidence '
                'to calculate an overall change.'
            )
        }

        state['progress_summary'] = summary

        return {
            'status': 'complete',
            'message': 'Overall progress summary generated.',
            'summary': summary
        }

    # --------------------------------------------------
    # Calculate average change from valid dimensions only
    # --------------------------------------------------

    total_change = sum(
        item['change']
        for item in valid_comparisons
    )

    average_change = (
        total_change / len(valid_comparisons)
    )

    if average_change < -0.05:
        overall = 'improved'
        message = (
            'Your overall scores show a decrease compared '
            'with your initial assessment.'
        )

    elif average_change > 0.05:
        overall = 'increased'
        message = (
            'Your overall scores are higher compared '
            'with your initial assessment.'
        )

    else:
        overall = 'stable'
        message = (
            'Your overall scores are relatively stable '
            'compared with your initial assessment.'
        )

    summary = {
        'overall_status': overall,
        'average_change': average_change,

        'improved_dimensions': [
            item['dimension']
            for item in improved
        ],

        'increased_dimensions': [
            item['dimension']
            for item in increased
        ],

        'stable_dimensions': [
            item['dimension']
            for item in stable
        ],

        'insufficient_dimensions': [
            item['dimension']
            for item in insufficient
        ],

        'message': message
    }

    state['progress_summary'] = summary

    return {
        'status': 'complete',
        'message': 'Overall progress summary generated.',
        'summary': summary
    }
def generate_progress_message(state):
    """
    Convert the technical progress summary into
    a supportive chatbot message.
    """
    summary = state.get('progress_summary')
    if not summary:
        return {'status': 'unavailable', 'message': 'Progress summary is not available.'}
    overall_status = summary['overall_status']
    improved = summary['improved_dimensions']
    increased = summary['increased_dimensions']
    stable = summary['stable_dimensions']
    if overall_status == 'improved':
        opening = "You've completed your reassessment, and your overall results show improvement compared with your initial assessment."
    elif overall_status == 'increased':
        opening = "You've completed your reassessment. Your overall scores are higher than they were in your initial assessment."
    else:
        opening = "You've completed your reassessment, and your overall results are relatively stable compared with your initial assessment."
    message_parts = [opening]
    if improved:
        improved_text = ', '.join(improved)
        message_parts.append(f'You showed positive change in: {improved_text}.')
    if stable:
        stable_text = ', '.join(stable)
        message_parts.append(f'These areas remained relatively stable: {stable_text}.')
    if increased:
        increased_text = ', '.join(increased)
        message_parts.append(f'Some areas may benefit from continued practice: {increased_text}.')
    message_parts.append('Remember that these results are indicators of patterns, not a diagnosis.')
    final_message = ' '.join(message_parts)
    state['progress_message'] = final_message
    return {'status': 'complete', 'message': final_message}

def start_exercise_phase(state):
    """
    Start the coping/healing exercise phase after
    the initial assessment has been completed.
    """
    if not state['assessment_complete']:
        return {'status': 'unavailable', 'message': 'Complete the initial assessment first.'}
    if not state.get('baseline_results'):
        baseline_result = generate_baseline_results(state)
        if baseline_result['status'] != 'complete':
            return baseline_result
    if not state.get('recommended_exercises'):
        exercise_result = recommend_exercises(state)
        if exercise_result['status'] != 'complete':
            return exercise_result
    state['phase'] = 'exercises'
    return {'status': 'started', 'phase': 'exercises', 'message': 'Your initial assessment is complete. Based on your responses, here are some exercises you can practice.', 'recommendations': state['recommended_exercises']}

def finish_exercise_phase(state):
    """
    Finish the exercise phase and make reassessment available.
    """
    if state['phase'] != 'exercises':
        return {'status': 'unavailable', 'message': 'The chatbot is not currently in the exercise phase.'}
    completed = len(state.get('completed_exercises', []))
    total = len(state.get('recommended_exercises', []))
    return {'status': 'ready_for_reassessment', 'phase': state['phase'], 'completed_exercises': completed, 'total_exercises': total, 'message': "You've completed the exercise phase. When you're ready, we can reassess your responses and compare them with your initial assessment."}

def chatbot_turn(state, user_response=None, action=None, dimension=None):
    """
    Single master controller for the complete chatbot lifecycle.

    Lifecycle:
        initial_assessment
            ↓
        assessment_complete
            ↓
        exercises
            ↓
        reassessment
            ↓
        reassessment_complete

    Parameters:
        state         : current chatbot conversation state
        user_response : user's text response
        action        : optional system/user action
                        ("start_exercises",
                         "complete_exercise",
                         "finish_exercises",
                         "start_reassessment")
        dimension     : exercise dimension when completing an exercise
    """
    phase = state['phase']
    if phase == 'initial_assessment':
        if user_response is None:
            return {'status': 'started', 'phase': phase, 'message': "Let's begin with a few questions to understand some of the patterns you may experience.", 'dimension': state['current_dimension'], 'question': state['current_question']}
        return process_chat_turn(state, user_response)
    if phase == 'assessment_complete':
        if not state.get('baseline_results'):
            baseline_result = generate_baseline_results(state)
            if baseline_result['status'] != 'complete':
                return baseline_result
        if action == 'start_exercises':
            return start_exercise_phase(state)
        return {'status': 'assessment_complete', 'phase': phase, 'message': 'Your initial assessment is complete. You can now review your results and practice some personalized exercises.', 'baseline_results': state['baseline_results']}
    if phase == 'exercises':
        if action == 'complete_exercise':
            if dimension is None:
                return {'status': 'error', 'phase': phase, 'message': 'A dimension is required to complete an exercise.'}
            return complete_exercise(state, dimension)
        if action == 'finish_exercises':
            return finish_exercise_phase(state)
        if action == 'start_reassessment':
            reassessment_result = start_reassessment(state)
            if reassessment_result['status'] != 'ready':
                return reassessment_result
            return begin_reassessment(state)
        return {'status': 'exercise_phase', 'phase': phase, 'message': "You can practice the recommended exercises and mark an exercise as completed when you're ready.", 'recommendations': state['recommended_exercises'], 'completed_exercises': state['completed_exercises'], 'total_exercises': len(state['recommended_exercises'])}
    if phase == 'reassessment':
        if state['current_dimension'] is None and user_response is None:
            return begin_reassessment(state)
        if user_response is None:
            return {'status': 'reassessment_started', 'phase': phase, 'message': "Welcome back. Let's check how things have changed since your initial assessment.", 'dimension': state['current_dimension'], 'question': state['current_question']}
        return process_reassessment_turn(state, user_response)
    if phase == 'reassessment_complete':
        if not state.get('comparison_results'):
            comparison_result = compare_baseline_reassessment(state)
            if comparison_result['status'] != 'complete':
                return comparison_result
        if not state.get('progress_summary'):
            progress_result = generate_progress_summary(state)
            if progress_result['status'] != 'complete':
                return progress_result
        if not state.get('progress_message'):
            message_result = generate_progress_message(state)
            if message_result['status'] != 'complete':
                return message_result
        return {'status': 'complete', 'phase': phase, 'message': state['progress_message'], 'comparison': state['comparison_results'], 'summary': state['progress_summary']}
    return {'status': 'error', 'phase': phase, 'message': f'Unknown chatbot phase: {phase}'}

