# Repetitive Negative Thinking

## 1. Purpose

Repetitive Negative Thinking (RNT) is a useful higher-level concept for understanding repetitive forms of negative thought.

Research has examined RNT as a construct that includes both rumination and worry.

This document provides knowledge that can help the adaptive conversational assessment system identify and explore repetitive negative thinking.

RNT should be treated as a behavioral and cognitive pattern, not as a clinical diagnosis.

---

## 2. Relationship Between Rumination and Worry

Rumination and worry are often discussed as related forms of repetitive negative thinking.

A commonly used distinction is:

* rumination may involve repeated thinking about past or existing negative experiences;
* worry may involve repeated thinking about possible future threats or uncertainty.

However, these categories overlap.

Both may involve:

* repetitive thinking
* negative content
* persistence
* difficulty controlling thoughts
* difficulty switching attention
* continued mental engagement with an unresolved concern

Therefore, the conversational system should not rely on a rigid past-versus-future rule.

The user's actual response and context should determine which pattern is most relevant.

---

## 3. Repetition

Repetition is a central behavioral characteristic of RNT.

Relevant evidence includes:

* returning to the same thought repeatedly
* replaying the same event
* repeatedly considering the same possible outcome
* repeatedly asking the same "what if" or "why" question
* mentally revisiting a concern even after the situation has ended

The system should distinguish repeated thinking from ordinary reflection.

Thinking about an event once does not by itself provide evidence of repetitive negative thinking.

---

## 4. Negative Valence

RNT generally involves negatively oriented thought content.

Examples may include:

* perceived mistakes
* possible future problems
* threats
* failures
* criticism
* embarrassment
* uncertainty
* negative self-evaluation
* feared consequences

The system should identify the content and context instead of assuming that every repeated thought is negative.

For example:

> "I keep thinking about the presentation because I am excited about improving it."

This is repetitive thinking, but it is not necessarily repetitive negative thinking.

---

## 5. Persistence

Persistence refers to the continuation of repetitive thought over time.

Relevant evidence may include:

* thoughts continuing after the triggering event
* repeatedly returning to the same concern
* remaining mentally occupied by the issue
* difficulty moving on from the original event
* continued thinking hours or days later

Persistence should be assessed separately from frequency.

A person may experience many thoughts during a short period, while another may repeatedly return to the same concern over a much longer period.

---

## 6. Controllability

Controllability is an important assessment attribute.

The system may explore whether the person can intentionally stop or redirect the repetitive thinking.

Relevant evidence includes:

* difficulty stopping the thought
* unsuccessful attempts to redirect attention
* feeling mentally stuck
* thoughts continuing despite attempts to focus elsewhere
* inability to disengage from the concern

If repetition is already established but controllability is unknown, controllability may become an appropriate target for the next adaptive question.

---

## 7. Difficulty Switching

A related characteristic is difficulty switching from the repetitive thought to another mental task.

Relevant evidence may include:

* difficulty concentrating on another activity
* repeatedly returning to the same concern
* losing focus because of the thought
* difficulty becoming mentally engaged with something else

This can be distinguished from simple persistence.

Persistence asks:

> "Does the thought continue?"

Switching difficulty asks:

> "Can the person move their attention to something else?"

---

## 8. Open-Ended Thinking

Some repetitive negative thoughts can remain active because the person continues generating additional possibilities, explanations, or questions.

Examples include:

* "What if something goes wrong?"
* "Why did I do that?"
* "What could I have done differently?"
* "What if they think badly of me?"
* "What else could go wrong?"

The system can use this information to distinguish a single negative thought from a continuing chain of repetitive thought.

---

## 9. Rumination as RNT

Rumination can be represented as one form of repetitive negative thinking.

Possible evidence includes:

* repeatedly reviewing past events
* revisiting mistakes
* repeatedly analyzing negative experiences
* focusing on causes or consequences
* repeatedly evaluating one's own behavior

For example:

> "I keep replaying what I said yesterday and thinking about what I should have said instead."

Possible evidence:

```text
RNT = detected
rumination = likely
past-focused content = detected
repetition = detected
```

The system should still determine whether persistence, controllability, and functional impact are known.

---

## 10. Worry as RNT

Worry can also be represented as a form of repetitive negative thinking.

Possible evidence includes:

* repeatedly imagining negative future outcomes
* repeatedly considering possible threats
* repeatedly thinking about uncertain situations
* difficulty stopping future-oriented "what if" thoughts

For example:

> "I keep imagining everything that could go wrong tomorrow."

Possible evidence:

```text
RNT = detected
worry = likely
future-oriented content = detected
repetition = detected
```

The system can then determine which evidence is still missing.

---

## 11. Shared Evidence Across Rumination and Worry

Because rumination and worry can overlap, the assessment system can track shared attributes.

A useful representation is:

```text
repetitive_negative_thinking:
    detected
    negative_content
    repetition
    persistence
    controllability
    switching_difficulty
    functional_impact
```

Additional context can then be recorded:

```text
thought_context:
    past_event
    current_problem
    future_uncertainty
    social_evaluation
    personal_failure
    other
```

This allows the system to represent both shared and distinct aspects of repetitive thinking.

---

## 12. Adaptive Evidence Collection

The chatbot should not ask every user the same RNT questions.

Instead, it should identify which evidence is already present and which evidence remains unknown.

Example:

```text
User:
"I keep thinking about what might happen before my exams."

Known:
- future-oriented concern
- repetition

Unknown:
- persistence
- controllability
- switching difficulty
- functional impact
```

The controller may choose one missing attribute.

The RAG system then retrieves relevant scientific knowledge.

The language model generates a contextually appropriate follow-up question.

---

## 13. Example Adaptive Flow

```text
User response
    ↓
"I keep thinking about everything that could go wrong."
    ↓
RNT detected
    ↓
Future-oriented content detected
    ↓
Repetition detected
    ↓
Controllability unknown
    ↓
Controller selects controllability
    ↓
Retrieve RNT knowledge
    ↓
Generate follow-up
    ↓
"When those thoughts start, how easy is it for you to shift your attention away from them?"
```

If the user responds:

> "It's really difficult. Even when I try to study, I keep going back to it."

The assessment state can be updated:

```text
controllability = low
switching_difficulty = detected
functional_impact = possible
```

The next question can therefore target a different missing attribute.

---

## 14. Important Interpretation Rule

The presence of repetitive negative thinking should not automatically be interpreted as proof of high neuroticism.

RNT is a behavioral/cognitive process that can be relevant to multiple psychological phenomena.

The neuroticism prediction model remains responsible for neuroticism prediction.

The conversational system collects additional behavioral evidence.

RAG provides scientific grounding.

The assessment controller decides what information is missing.

---

## 15. Relationship to the Adaptive RAG Architecture

The knowledge from this document can support the following pipeline:

```text
User response
      ↓
Behavioral analysis
      ↓
RNT evidence
      ↓
Assessment state
      ↓
Missing evidence
      ↓
RAG retrieval
      ↓
Context + retrieved knowledge
      ↓
LLM
      ↓
Adaptive follow-up question
```

The knowledge base therefore provides scientific grounding rather than a predefined question sequence.

---

## 16. Source

Primary source:

SRC004 — Hitchcock, P. F., & Frank, M. J. (2024).

*From Tripping and Falling to Ruminating and Worrying: A Meta-Control Account of Repetitive Negative Thinking.*

Current Opinion in Behavioral Sciences, 56, 101356.

The paper describes RNT as encompassing rumination and worry and discusses their shared characteristics, including repetitive, negatively valenced, and difficult-to-control thinking. It also proposes a meta-control framework for understanding different pathways that can produce excessive RNT.

Source:

https://pmc.ncbi.nlm.nih.gov/articles/PMC11314892/
