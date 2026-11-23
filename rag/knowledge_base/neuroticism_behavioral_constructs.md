# Neuroticism Behavioral Constructs

## 1. Purpose

This document defines behavioral constructs that can be used when exploring neuroticism-related patterns in a conversational assessment system.

The constructs are informed by the International Personality Item Pool (IPIP) and related Five-Factor Model personality measures.

They are used as behavioral evidence categories rather than as diagnostic categories.

The system should not assume that one observed behavior proves high neuroticism.

Instead, it should consider patterns across multiple responses, including frequency, intensity, persistence, controllability, triggers, and functional impact.

---

## 2. IPIP Neuroticism Facets

IPIP personality measures describe Neuroticism using six narrower facets:

* Anxiety
* Anger
* Depression
* Self-Consciousness
* Immoderation
* Vulnerability

These facets provide a scientifically grounded starting point for identifying neuroticism-related behavioral evidence.

The conversational system should use these facets as conceptual guidance rather than treating them as a fixed sequence of chatbot questions.

---

## 3. Anxiety

Anxiety-related personality content includes tendencies such as:

* worrying about things
* anticipating negative outcomes
* fearing the worst
* experiencing stress easily
* feeling apprehensive about possible threats

Relevant behavioral evidence may include:

* frequency of worry
* intensity of worry
* future-oriented worry
* triggers of worry
* difficulty controlling worry
* persistence of worry
* interference with normal activities

### Example evidence

A user may describe:

> "I keep thinking about everything that could go wrong before an exam."

This provides evidence of future-oriented worry.

However, the system should not immediately conclude that the person has high neuroticism.

It should determine what additional information is still missing.

---

## 4. Anger and Irritability

Anger-related personality content includes tendencies such as:

* becoming angry easily
* becoming irritated easily
* losing one's temper
* reacting strongly to frustrating situations

Relevant behavioral evidence may include:

* frequency of irritation
* intensity of anger
* common triggers
* speed of emotional escalation
* duration of anger
* ability to recover after anger

### Example evidence

A user may say:

> "Small things annoy me and sometimes I stay irritated for hours."

This provides evidence about irritability and persistence.

The system may then determine that information about triggers or emotional recovery is still missing.

---

## 5. Depression-Related Negative Affect

The depression-related facet in personality assessment concerns negative mood and self-directed negative affect.

Potential evidence may include:

* frequent sadness
* discouragement
* negative self-evaluation
* feeling down after setbacks
* difficulty recovering from negative experiences

This construct must be handled carefully.

The conversational system should describe observed personality-related patterns rather than diagnosing depression.

For example, it may state:

> "Your responses suggest that negative self-evaluation persists after setbacks."

It should not state:

> "You have depression."

---

## 6. Self-Consciousness

Self-consciousness concerns sensitivity to social evaluation and discomfort in situations involving attention or judgment.

Relevant behavioral evidence may include:

* concern about being judged
* discomfort when receiving attention
* fear of embarrassment
* difficulty approaching unfamiliar people
* sensitivity to criticism
* replaying socially uncomfortable experiences
* avoidance of difficult social situations

### Example evidence

A user may say:

> "After I say something embarrassing, I keep thinking about what everyone thought of me."

This provides evidence about sensitivity to social evaluation and possible post-event rumination.

The system should determine whether additional information about persistence, intensity, or avoidance is needed.

---

## 7. Immoderation and Impulse Control

The IPIP Neuroticism domain also includes an immoderation facet related to difficulty resisting urges or cravings.

Potential behavioral evidence may include:

* strong urges
* difficulty resisting immediate rewards
* repeated overindulgence
* difficulty stopping once an urge begins

This construct should not automatically become a major conversational assessment category.

It may be retained as supporting personality knowledge while the system focuses primarily on constructs that are more directly relevant to the project's behavioral-analysis goals.

---

## 8. Vulnerability Under Stress

Vulnerability concerns reactions when a person experiences substantial pressure or multiple demands.

Relevant behavioral evidence may include:

* becoming overwhelmed under pressure
* difficulty thinking clearly during stressful situations
* panic-like reactions to high pressure
* difficulty coping when several problems occur simultaneously
* reduced ability to manage tasks during emotional overload
* difficulty recovering after stressful situations

### Example evidence

A user may say:

> "When several assignments and problems happen at once, I get overwhelmed and can't think properly."

This provides evidence about stress-related vulnerability.

The system should investigate additional evidence such as frequency, intensity, triggers, and recovery.

---

## 9. Behavioral Evidence Is Not the Same as a Facet Score

The chatbot should not assume:

```text
Anxiety detected = high Neuroticism
```

Instead:

```text
User response
    ↓
Behavioral evidence
    ↓
Evidence strength
    ↓
Assessment state
    ↓
Additional missing evidence
```

For example:

```text
future worry = detected
frequency = known
intensity = unknown
persistence = unknown
controllability = unknown
functional impact = unknown
```

The system can then decide which missing information is most useful to obtain next.

---

## 10. Evidence Attributes

For each relevant behavioral pattern, the assessment system may track:

### Frequency

How often does the experience occur?

### Intensity

How strong is the emotional or cognitive response?

### Duration

How long does the experience last?

### Persistence

Does the experience continue after the original trigger?

### Controllability

How difficult is it to stop, redirect, or regulate the experience?

### Trigger

What situations or events tend to produce the response?

### Functional Impact

Does the experience interfere with studying, working, relationships, or other normal activities?

### Recovery

How quickly does the person return to their usual emotional state?

---

## 11. Relationship to the Adaptive Chatbot

These constructs are not a fixed question sequence.

The chatbot should use them to determine what behavioral evidence has already been collected and what evidence is still missing.

For example:

```text
User response
    ↓
Future-oriented worry detected
    ↓
Frequency known
    ↓
Persistence unknown
    ↓
Controller selects persistence as missing evidence
    ↓
RAG retrieves knowledge related to worry persistence
    ↓
LLM generates an appropriate follow-up question
```

A different user response may produce a different next question.

Therefore, the conversation is adaptive rather than a predefined sequence of questions.

---

## 12. Relationship to the Neuroticism Prediction Model

The neuroticism prediction model and the conversational system have different responsibilities.

### Neuroticism model

The ML model predicts neuroticism-related classification/probability from text.

### Behavioral assessment

The conversational system collects additional behavioral evidence from the user's responses.

### Assessment controller

The controller determines what information is missing and what should be explored next.

### RAG

RAG retrieves relevant scientific knowledge from the knowledge base.

### Language model

The language model converts the retrieved knowledge and assessment state into a natural-language follow-up question.

Therefore:

> RAG does not replace the neuroticism prediction model.

RAG provides scientific grounding for the adaptive conversation.

---

## 13. Safety and Interpretation

Neuroticism is a personality trait and should not be treated as a clinical diagnosis.

The system should avoid statements such as:

* "You have anxiety."
* "You have depression."
* "You have a mental disorder."
* "You are clinically neurotic."

Instead, it should describe behavioral patterns observed in the conversation.

Examples include:

* "Your responses indicate frequent future-oriented worry."
* "You described difficulty disengaging from negative thoughts."
* "You reported strong emotional reactions under pressure."
* "Your responses suggest sensitivity to social evaluation."

These statements describe observed conversational evidence without making a clinical diagnosis.

---

## 14. Source

Primary source:

SRC002 — International Personality Item Pool (IPIP)

Official IPIP resources describe six Neuroticism facets:

* Anxiety
* Anger
* Depression
* Self-Consciousness
* Immoderation
* Vulnerability

Source registry:

`rag/sources/sources.json`

Additional research sources will be used to provide deeper knowledge about specific behavioral phenomena such as worry, rumination, repetitive negative thinking, social evaluation, and emotional reactivity.
