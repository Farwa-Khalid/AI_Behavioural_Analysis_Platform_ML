Behavioral Evidence Schema

1. Purpose

This document defines the behavioral evidence representation used by the adaptive neuroticism assessment chatbot.

The purpose of the schema is to represent observable evidence from a user's text response without treating any single behavior as proof of neuroticism.

The schema separates:

scientific knowledge

behavioral evidence

neuroticism model prediction

adaptive assessment logic

RAG retrieval

question generation

The schema is an engineering representation informed by the project's curated literature. It is not an official replacement for established personality inventories or diagnostic criteria.

2. Core Design Principles

2.1 Neuroticism is a trait, not a binary diagnosis

The system should treat neuroticism as a dimensional personality trait.

The existing ML model produces the project's model-based neuroticism prediction.

The behavioral chatbot provides additional behavioral evidence and context.

The chatbot must not claim that one behavioral pattern proves neuroticism.

2.2 Behavioral constructs are not official Neuroticism dimensions

The constructs in this schema are engineered behavioral representations derived from the project's literature.

They should not be described as official Big Five or IPIP dimensions.

IPIP provides established Neuroticism-related facets including Anxiety, Angry Hostility, Depression, Self-Consciousness, Impulsiveness, and Vulnerability. These are used as a scientific reference layer, while this project converts relevant concepts into observable evidence categories.

2.3 Do not use a fixed question sequence

The previous chatbot followed a manually defined sequence of questions.

The new system does not define:

Question 1 -> Question 2 -> Question 3 -> ... -> Question 24

Instead:

User response
    -> evidence extraction
    -> assessment state
    -> missing evidence
    -> controller target
    -> RAG retrieval
    -> LLM question generation

2.4 Never infer missing evidence

If a user response does not provide evidence for an attribute, the value must remain:

unknown

The system must not fill missing information using assumptions.

2.5 Separate evidence from interpretation

For example:

User: "I keep thinking about failing."

Valid evidence:

worry.detected = true
worry.negative_outcome = "failure"
worry.temporal_orientation = "future"

Not valid:

neuroticism = high

The latter requires model-level evidence and should not be inferred directly from one statement.

3. Evidence States

Every evidence attribute should support one of the following states:

known

There is sufficient evidence in the conversation to assign a value.

Example:

persistence = "several hours"

unknown

The conversation has not provided enough information.

Example:

controllability = unknown

uncertain

The response contains ambiguous or conflicting evidence.

Example:

User: "Sometimes I can stop worrying, but sometimes I really can't."

Possible representation:

controllability = uncertain

Unknown and uncertain are intentionally different.

unknown = information has not been collected

uncertain = information exists but is ambiguous

4. Universal Evidence Attributes

These attributes can be reused across multiple behavioral constructs.

Attribute

Meaning

detected

Whether evidence for the construct is present

trigger

What initiated the thought/emotional response

context

Situation in which it occurs

content

Topic or subject of the thought/experience

frequency

How often it occurs

intensity

Strength of the experience

persistence

How long it continues

repetition

Whether the same type of thought/response recurs

controllability

Ability to control or stop it

switching_difficulty

Difficulty shifting attention away

recovery

How quickly the person returns toward baseline

functional_impact

Whether it interferes with normal functioning

repeated_pattern

Whether it appears repeatedly across situations

5. Behavioral Constructs

5.1 Repetitive Negative Thinking

Purpose

Represents a broad pattern of repetitive, negatively oriented thinking.

Worry and rumination can be represented as contextually different forms of repetitive negative thinking.

Evidence schema

repetitive_negative_thinking:
    detected
    negative_content
    repetition
    persistence
    controllability
    switching_difficulty
    functional_impact
    context
    content

Example

User:

"I keep going over what happened and I can't get my mind off it."

Possible evidence:

repetitive_negative_thinking:
    detected = true
    negative_content = true
    repetition = true
    persistence = unknown
    controllability = unknown
    switching_difficulty = true
    functional_impact = unknown
    context = "past event"

5.2 Worry

Purpose

Represents future-oriented negative thinking involving possible negative outcomes and related appraisals.

Evidence schema

worry:
    detected
    temporal_orientation
    negative_outcome
    content
    repetition
    persistence
    controllability
    switching_difficulty
    perceived_likelihood
    perceived_severity
    perceived_coping
    functional_impact

Example

User:

"I keep thinking that I might fail my presentation."

Possible evidence:

worry:
    detected = true
    temporal_orientation = "future"
    negative_outcome = "presentation failure"
    content = "presentation"
    repetition = true
    persistence = unknown
    controllability = unknown
    switching_difficulty = unknown
    perceived_likelihood = unknown
    perceived_severity = unknown
    perceived_coping = unknown
    functional_impact = unknown

5.3 Rumination

Purpose

Represents repetitive thinking about negative experiences, events, self-related concerns, or their causes/consequences.

Evidence schema

rumination:
    detected
    temporal_orientation
    content
    trigger
    repetition
    persistence
    controllability
    switching_difficulty
    self_focus
    post_event_thinking
    functional_impact

Example

User:

"After I make a mistake, I keep replaying it and thinking about why I did it."

Possible evidence:

rumination:
    detected = true
    temporal_orientation = "past"
    content = "personal mistake"
    trigger = "mistake"
    repetition = true
    persistence = unknown
    controllability = unknown
    switching_difficulty = unknown
    self_focus = true
    post_event_thinking = true
    functional_impact = unknown

5.4 Emotional Reactivity

Purpose

Represents how a person reacts emotionally to a trigger, including strength, persistence, recovery, and perceived control.

Evidence schema

emotional_reactivity:
    detected
    trigger
    sensitivity
    intensity
    persistence
    recovery
    controllability
    functional_impact
    repeated_pattern

Example

User:

"When someone criticizes me, I get upset immediately and stay upset for hours."

Possible evidence:

emotional_reactivity:
    detected = true
    trigger = "criticism"
    sensitivity = "high"
    intensity = "high"
    persistence = "hours"
    recovery = "slow"
    controllability = unknown
    functional_impact = unknown
    repeated_pattern = unknown

5.5 Social Evaluation

Purpose

Represents behavioral evidence related to being judged, criticized, evaluated, accepted, or rejected by other people.

Evidence schema

social_evaluation:
    detected
    context
    negative_expectation
    perceived_judgment
    criticism_sensitivity
    emotional_reactivity
    avoidance
    post_event_thinking
    persistence
    controllability

Example

User:

"Before speaking in front of people, I keep thinking they will notice my mistakes."

Possible evidence:

social_evaluation:
    detected = true
    context = "public speaking"
    negative_expectation = true
    perceived_judgment = true
    criticism_sensitivity = unknown
    emotional_reactivity = unknown
    avoidance = unknown
    post_event_thinking = unknown
    persistence = unknown
    controllability = unknown

5.6 Stress Vulnerability

Purpose

Represents difficulty coping or feeling overwhelmed under stress.

This construct is informed particularly by the vulnerability-related literature and is used as behavioral evidence rather than a diagnostic label.

Evidence schema

stress_vulnerability:
    detected
    trigger
    perceived_stress
    feeling_overwhelmed
    perceived_coping
    coping_difficulty
    recovery
    persistence
    functional_impact
    repeated_pattern

Example

User:

"When several deadlines come together, I feel like I can't handle anything."

Possible evidence:

stress_vulnerability:
    detected = true
    trigger = "multiple deadlines"
    perceived_stress = "high"
    feeling_overwhelmed = true
    perceived_coping = "low"
    coping_difficulty = "high"
    recovery = unknown
    persistence = unknown
    functional_impact = unknown
    repeated_pattern = unknown

5.7 Negative Self-Evaluation

Purpose

Represents self-doubt, self-criticism, perceived inadequacy, and negative interpretations of personal performance.

Evidence schema

negative_self_evaluation:
    detected
    trigger
    self_doubt
    self_criticism
    perceived_failure
    perceived_inadequacy
    persistence
    controllability
    emotional_reactivity
    functional_impact

Example

User:

"Whenever I make a small mistake, I immediately think I'm not good enough."

Possible evidence:

negative_self_evaluation:
    detected = true
    trigger = "mistake"
    self_doubt = true
    self_criticism = true
    perceived_failure = true
    perceived_inadequacy = true
    persistence = unknown
    controllability = unknown
    emotional_reactivity = unknown
    functional_impact = unknown

6. Construct Hierarchy

The constructs should not be treated as seven unrelated categories.

The intended hierarchy is:

Behavioral Evidence
|
+-- Repetitive Negative Thinking
|   |
|   +-- Worry
|   |
|   +-- Rumination
|
+-- Emotional Reactivity
|
+-- Social Evaluation
|
+-- Stress Vulnerability
|
+-- Negative Self-Evaluation

Repetitive Negative Thinking is a cross-cutting process.

Worry and rumination are contextual forms of that process.

Some evidence attributes intentionally overlap across constructs. This is expected because the underlying behavioral phenomena can overlap.

7. Source Mapping

The curated literature contributes different parts of the schema.

Source

Contribution to schema

OpenStax Psychology

Personality, Big Five, dimensional understanding of neuroticism

IPIP

Neuroticism-related reference facets

Rumination review

Repetitive thinking, persistence, controllability, post-event thinking

RNT research

Repetition, negative content, persistence, controllability, switching difficulty

Neuroticism and repetitive thought

Exposure/frequency versus affective reactivity

Social evaluation research

Judgment, criticism sensitivity, negative expectations, social feedback

Emotional reactivity research

Sensitivity, intensity, persistence, recovery

Worry/future-threat research

Future orientation, likelihood, severity, coping, controllability

The sources therefore justify the evidence attributes, rather than defining a fixed set of chatbot questions.

8. IPIP Reference Layer

The IPIP/NEO comparison identifies six Neuroticism-related facets:

Anxiety
Angry Hostility
Depression
Self-Consciousness
Impulsiveness
Vulnerability

These should remain a reference layer.

They should NOT become:

Question group 1
Question group 2
...
Question group 6

Instead, relevant behavioral evidence can map to them conceptually.

Example:

IPIP reference facet:
    Anxiety

Possible behavioral evidence:
    worry
    future threat
    perceived likelihood
    perceived coping
    repetitive negative thinking

Another example:

IPIP reference facet:
    Self-Consciousness

Possible behavioral evidence:
    social evaluation
    perceived judgment
    criticism sensitivity
    post-event thinking

This preserves the scientific reference without recreating a fixed questionnaire.

9. Evidence Provenance

Every extracted evidence item should eventually store where it came from.

Recommended representation:

evidence_item:
    construct
    attribute
    value
    state
    source_turn
    confidence

Example:

{
  "construct": "worry",
  "attribute": "temporal_orientation",
  "value": "future",
  "state": "known",
  "source_turn": 3,
  "confidence": 0.94
}

This allows the system to answer:

"Why does the assessment state believe this?"

It also makes debugging much easier.

10. Assessment State

The complete conversation should eventually maintain an assessment state similar to:

assessment_state:
    constructs:
        repetitive_negative_thinking:
            ...
        worry:
            ...
        rumination:
            ...
        emotional_reactivity:
            ...
        social_evaluation:
            ...
        stress_vulnerability:
            ...
        negative_self_evaluation:
            ...

    conversation:
        turn_count
        recent_responses

    model_output:
        neurotic_probability
        non_neurotic_probability
        confidence

The model output must remain separate from behavioral evidence.

11. Relationship With the Neuroticism ML Model

The existing neuroticism model answers:

"Based on the model's learned representation, what is the predicted neuroticism class/probability?"

The behavioral evidence layer answers:

"What behavioral patterns are supported by the user's conversation?"

These are related but different.

The system must not replace the ML prediction with manually calculated behavioral scores unless a separate validated scoring model is explicitly developed.

12. Relationship With the Controller

The controller answers:

"What useful behavioral information is still missing?"

Example:

Known:
    worry.detected = true
    worry.temporal_orientation = future
    worry.negative_outcome = "failure"

Unknown:
    worry.controllability
    worry.persistence
    worry.perceived_coping

The controller selects one high-value target.

Example:

target:
    construct = "worry"
    attribute = "perceived_coping"

The controller should not select:

question = "Question 7"

because questions are generated dynamically.

13. Relationship With RAG

RAG answers:

"What scientifically grounded knowledge is relevant to the controller's current target?"

Example:

controller target:
    worry.perceived_coping

RAG retrieves relevant knowledge from:

worry_future_threat.md
repetitive_negative_thinking.md
neuroticism_repetitive_thought.md

RAG does NOT:

diagnose the user

directly calculate neuroticism

decide the final neuroticism class

contain a fixed question sequence

14. Relationship With the LLM

The LLM receives:

user's recent response
+
current assessment state
+
controller target
+
retrieved scientific knowledge

It generates:

ONE appropriate follow-up question.

The question should:

target the selected missing attribute

be understandable

avoid asking several unrelated questions at once

avoid assuming an answer

avoid diagnostic language

avoid unnecessarily repeating previous questions

remain grounded in retrieved knowledge

15. Adaptive Question Example

User response

"I keep worrying that I'll fail my presentation."

Evidence extracted

worry:
    detected = true
    temporal_orientation = future
    negative_outcome = "presentation failure"
    repetition = true

    persistence = unknown
    controllability = unknown
    perceived_likelihood = unknown
    perceived_severity = unknown
    perceived_coping = unknown

Controller

Selects:

target:
    construct = worry
    attribute = perceived_coping

RAG

Retrieves knowledge related to:

future-oriented worry
perceived threat
coping ability
controllability

LLM

Generates one question such as:

"When you imagine failing, do you usually feel that you could handle the situation, or does it feel difficult to cope with?"

That question was not stored as Question 1, Question 2, or Question 24.

It was generated because the assessment state identified a missing piece of evidence.

16. Unknown-Evidence Rule

The system must never convert absence of evidence into negative evidence.

Incorrect:

User did not mention avoidance.

Therefore:
    avoidance = false

Correct:

User did not mention avoidance.

Therefore:
    avoidance = unknown

Only an explicit response can change it to a known value.

17. Uncertainty Rule

If the language model/evidence extractor is unsure, it should preserve uncertainty.

Example:

"I guess I sometimes avoid those situations."

Possible state:

avoidance:
    state = uncertain
    value = "possible"

The controller can later ask a clarifying question.

This prevents the system from treating weak NLP interpretations as facts.

18. Safety and Interpretation Rules

The system is a behavioral assessment/research prototype.

It must not:

diagnose mental disorders

claim that a behavioral pattern proves neuroticism

claim that RAG retrieval is a clinical assessment

infer medical conditions from text

present a probability as a clinical diagnosis

make unsupported causal claims

Preferred wording:

"This response provides behavioral evidence relevant to the assessment."

Avoid:

"This proves that you are neurotic."

The existing ML prediction should also be presented as a model prediction, not a clinical diagnosis.

19. Final System Boundary

The complete responsibility separation is:

                 USER RESPONSE
                       |
                       v
              +------------------+
              | Evidence         |
              | Extraction       |
              +------------------+
                       |
                       v
              +------------------+
              | Assessment State |
              +------------------+
                       |
                       v
              +------------------+
              | Controller       |
              | What is missing? |
              +------------------+
                       |
             +---------+---------+
             |                   |
             v                   v
       Existing ML          RAG Retrieval
       Neuroticism          Scientific
       Prediction           Knowledge
             |                   |
             +---------+---------+
                       |
                       v
              +------------------+
              | LLM Question     |
              | Generation       |
              +------------------+
                       |
                       v
                 NEXT QUESTION
                       |
                       +--------> USER

20. What Comes Next

This schema is the contract for the next implementation stages.

The implementation order is:

1. behavioral_evidence_schema.md       <- THIS FILE
2. behavioral_evidence_schema.json
3. assessment_state.py
4. evidence_extractor.py
5. adaptive_controller.py
6. controller tests
7. knowledge-base chunking
8. embeddings
9. vector store
10. retrieval
11. LLM question generation
12. end-to-end adaptive chatbot

Do not build the vector database before the schema and controller logic are working.

The primary goal is not simply to make a chatbot that can retrieve documents. The goal is to make a chatbot that can identify missing behavioral evidence, retrieve scientifically relevant knowledge, and generate an adaptive follow-up question based on that evidence.