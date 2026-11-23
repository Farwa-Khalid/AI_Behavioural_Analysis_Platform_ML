# Worry, Future Threat, and Negative Thinking

## Purpose

This document summarizes research-informed concepts related to worry, future-oriented negative thinking, perceived threat, and perceived ability to cope.

The purpose is to provide behavioral knowledge for an adaptive conversational assessment system.

This information should not be used to diagnose anxiety disorders or other clinical conditions.

---

## 1. What Is Worry?

Worry involves streams of thoughts concerning possible negative outcomes, particularly outcomes that may occur in the future.

For conversational assessment, worry should not be represented simply as:

```text
worry = yes/no
```

Instead, the system should examine characteristics of the person's worry.

Potential characteristics include:

* future orientation
* negative outcome content
* repetition
* persistence
* controllability
* perceived threat
* perceived likelihood
* perceived severity or cost
* perceived ability to cope

---

## 2. Future-Oriented Negative Thinking

A person may repeatedly think about what could go wrong in the future.

Examples include concerns about:

* academic performance
* career
* relationships
* finances
* health
* social situations
* upcoming events
* uncertain outcomes

The important behavioral evidence is not simply the topic.

The system should also examine how the person thinks about the possible outcome.

For example:

> "I keep imagining that something will go wrong with my presentation."

This contains evidence of:

```text
future orientation
negative outcome
repetitive thinking
```

But it does not yet tell us:

```text
how often it occurs
how intense the concern is
how controllable it feels
how long it persists
how likely the person believes the outcome is
```

These can be investigated later if relevant.

---

## 3. Perceived Threat

Worry can involve a person's perception that a possible negative outcome represents a significant threat.

For conversational assessment, perceived threat can be represented through:

* perceived likelihood
* perceived severity
* degree of concern
* perceived consequences
* perceived ability to cope

For example:

> "I'm worried I'll fail the exam."

This identifies the negative outcome.

A follow-up response such as:

> "I feel like failing would completely ruin everything."

provides additional evidence about perceived cost or severity.

---

## 4. Perceived Likelihood

A person may differ in how likely they believe a negative outcome is.

For example:

```text
"I know it probably won't happen, but I keep thinking about it."
```

This indicates that the presence of worry does not necessarily mean the person believes the feared outcome is highly probable.

Therefore the system should distinguish:

```text
worry presence
```

from:

```text
perceived probability of the feared outcome
```

This prevents the chatbot from making unsupported assumptions.

---

## 5. Perceived Cost or Severity

The same future event can have very different perceived importance for different people.

The system can examine how bad the person expects the outcome to be.

Potential evidence includes:

* expecting serious consequences
* viewing an outcome as disastrous
* believing a mistake would have major consequences
* describing an outcome as unbearable
* expecting major personal or social consequences

Example:

> "If I make one mistake during the presentation, everyone will think I'm incompetent."

Possible evidence:

```text
negative outcome = mistake
perceived social consequence = high
perceived cost = potentially high
```

The chatbot should not assume that the person's prediction is objectively true.

It records the person's perceived threat.

---

## 6. Perceived Ability to Cope

An important distinction is:

```text
"What might happen?"
```

versus:

```text
"How capable do I feel of handling it?"
```

A person may perceive an event as likely but believe they could handle it.

Another person may perceive the same event as unlikely but feel unable to cope with it.

Therefore the assessment should separately consider:

```text
perceived threat
+
perceived coping ability
```

Examples:

> "I think I could handle it if it happened."

versus:

> "If that happened, I honestly don't think I could deal with it."

These provide different behavioral evidence.

---

## 7. Controllability of Worry

Difficulty controlling worry is an important characteristic to assess.

Potential evidence includes:

* inability to stop thinking about the concern
* thoughts returning repeatedly
* difficulty shifting attention
* continuing to worry despite trying to stop
* feeling that worry occurs automatically
* difficulty focusing on another activity

Example:

> "I try to distract myself, but the same thought keeps coming back."

Possible evidence:

```text
worry = present
repetition = present
controllability = difficult
attention_switching = difficult
```

The system should not infer poor controllability from the mere presence of worry.

It should look for explicit or strongly supported evidence.

---

## 8. Persistence

Persistence describes how long worry continues.

Potential evidence includes:

* worrying for minutes
* worrying for hours
* continuing across the day
* returning to the same concern repeatedly
* carrying worry into subsequent activities
* recurring worry across multiple days or situations

Persistence is different from frequency.

For example:

```text
high frequency + short episodes
```

and:

```text
low frequency + very long episodes
```

represent different patterns.

The assessment should preserve both when possible.

---

## 9. Repetitive Negative Thought Intrusions

Negative thoughts may continue to appear after a person has tried to move away from a worry.

Possible evidence includes:

* unwanted return of the same negative thought
* repeated mental replay
* thoughts appearing during unrelated activities
* difficulty keeping attention away from the concern
* repeated negative scenarios entering awareness

Example:

> "Even when I'm studying something else, the same possibility keeps popping into my head."

Possible evidence:

```text
negative_content = present
intrusion = present
attention_capture = present
switching_difficulty = possible
```

The system should distinguish an intentional decision to think about a problem from repeated thoughts that continue despite attempts to focus elsewhere.

---

## 10. Abstract and Generalized Thinking

Worry can involve abstract or generalized negative thinking.

For example:

> "Something bad is going to happen."

This is different from:

> "I am worried that I will miss tomorrow's 9 AM presentation because my transport may be delayed."

The first is broad and unspecified.

The second contains a more concrete scenario.

This distinction can help the behavioral analyzer identify whether the user's worry is:

```text
generalized/abstract
```

or:

```text
specific/concrete
```

The chatbot should not assume that abstract thinking is automatically pathological.

It is simply another useful characteristic of the person's reported thought process.

---

## 11. Negative Outcome Chains

People may describe worry as a chain of possible negative outcomes.

Example:

> "If I fail this exam, I won't get the grade I need, then I won't get into the program, and then everything will be ruined."

Possible structure:

```text
event
  ↓
negative outcome 1
  ↓
negative outcome 2
  ↓
negative outcome 3
```

This can provide evidence about:

* future-oriented thinking
* negative outcome generation
* perceived consequences
* perceived threat
* repetitive thinking

The system should record the chain without assuming that the predicted outcomes are objectively likely.

---

## 12. Worry and Rumination

Worry and rumination overlap because both can involve repetitive negative thinking.

A useful contextual distinction is:

```text
Worry:
primarily concerns possible future outcomes
```

```text
Rumination:
often involves repeated thinking about negative experiences,
feelings, or events that have already occurred
```

This distinction is not absolute.

The same conversation may contain both.

For example:

```text
Past:
"I keep thinking about what I said yesterday."

Future:
"Now I'm worried about what people will think tomorrow."
```

The behavioral analyzer can therefore assign evidence to both relevant constructs.

---

## 13. Relationship With Neuroticism

Worry-related behavior can provide evidence relevant to neuroticism assessment, but worry itself is not equivalent to neuroticism.

Therefore:

```text
worry
    ≠
neuroticism
```

Instead:

```text
worry
+
emotional reactivity
+
repetitive thinking
+
other behavioral evidence
        ↓
neuroticism-related behavioral evidence
```

The neuroticism model remains responsible for producing the model-based prediction.

The RAG system provides scientific grounding for interpretation and question generation.

---

## 14. Behavioral Evidence Representation

For the adaptive chatbot, worry can be represented as:

```yaml
worry:
    detected: true/false/unknown

    temporal_orientation:
        past/current/future/mixed/unknown

    negative_outcome:
        present/absent/unknown

    content:
        text/unknown

    repetition:
        low/moderate/high/unknown

    persistence:
        low/moderate/high/unknown

    controllability:
        easy/moderate/difficult/unknown

    switching_difficulty:
        low/moderate/high/unknown

    perceived_likelihood:
        low/moderate/high/unknown

    perceived_severity:
        low/moderate/high/unknown

    perceived_coping:
        low/moderate/high/unknown

    functional_impact:
        none/mild/moderate/high/unknown
```

The use of `unknown` is important.

The system must not fill missing information with assumptions.

---

## 15. Example of Adaptive Assessment

User:

> "I keep worrying that I won't get the job."

Known evidence:

```text
future_orientation = future
negative_outcome = present
worry = present
```

Unknown:

```text
repetition
persistence
controllability
perceived_likelihood
perceived_severity
perceived_coping
functional_impact
```

The controller should not ask all seven questions.

It should select the most useful missing evidence based on the current assessment state.

For example, if repetition is already known from previous responses but coping ability is unknown, the next question could explore coping.

---

## 16. Adaptive Question Generation

The knowledge in this document should not become a fixed question bank.

Instead:

```text
user response
      ↓
extract behavioral evidence
      ↓
update assessment state
      ↓
identify highest-value missing attribute
      ↓
retrieve relevant knowledge
      ↓
LLM generates one question
```

Example:

Known:

```text
future worry = present
negative outcome = present
high perceived severity = present
```

Unknown:

```text
coping ability
controllability
persistence
```

The controller may choose:

```text
coping ability
```

as the next target.

The LLM can then generate a natural question appropriate to the user's previous response.

The exact wording is generated dynamically rather than selected from a fixed 24-question sequence.

---

## 17. RAG Grounding

RAG should retrieve information about concepts such as:

* worry
* future negative outcomes
* perceived threat
* controllability
* perceived coping
* negative thought intrusions
* repetitive thinking

The retrieved knowledge provides grounding for the question-generation model.

RAG should not directly decide:

```text
"User is neurotic."
```

Nor should it replace the trained neuroticism classifier.

---

## 18. Safety and Interpretation

The system should distinguish behavioral assessment from clinical diagnosis.

Preferred:

> "Your response suggests repeated concern about a possible future negative outcome."

Avoid:

> "You have an anxiety disorder."

Preferred:

> "Difficulty disengaging from repeated worry is behavioral evidence that may be relevant to the assessment."

Avoid:

> "Your inability to stop worrying proves high neuroticism."

The system should describe observed patterns rather than make clinical diagnoses.

---

## 19. Main Design Principle

The main principle is:

> Do not assess worry only by asking whether worry exists. Assess what the person worries about, how the thought behaves, how threatening the outcome feels, and how capable the person feels of coping with it.

Useful evidence includes:

```text
future orientation
+
negative outcome
+
repetition
+
persistence
+
controllability
+
switching difficulty
+
perceived likelihood
+
perceived severity
+
perceived coping
+
functional impact
```

This allows the adaptive chatbot to ask targeted questions about missing behavioral evidence rather than following a predetermined question sequence.
