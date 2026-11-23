# Social Evaluation

## 1. Purpose

Social evaluation refers to situations in which a person is concerned about how they are judged, accepted, rejected, criticized, or evaluated by other people.

Social evaluation is relevant to neuroticism-related behavioral assessment because research has found associations between trait neuroticism and responses or expectations related to social feedback.

This document provides knowledge for conversational exploration.

Social-evaluation-related evidence should not be treated as proof of high neuroticism or as a clinical diagnosis.

---

## 2. Social Evaluation and Neuroticism

Research has examined how individual differences in neuroticism relate to responses to social judgment.

In an experimental social judgment task, higher self-reported neuroticism was associated with a more negative prediction bias about whether another person would like the participant.

Neuroticism was also associated with aspects of the physiological response to social feedback.

These findings support the use of social-evaluation-related experiences as one possible source of behavioral evidence when exploring neuroticism-related patterns.

However, the relationships observed in the study were not sufficient to treat social evaluation as a direct or exclusive measure of neuroticism.

---

## 3. Negative Social Expectations

A person may develop negative expectations about how others will evaluate them before receiving actual feedback.

Relevant evidence may include:

* expecting others to dislike them
* expecting criticism
* assuming others will notice mistakes
* anticipating embarrassment
* expecting rejection
* predicting negative judgments without clear evidence

Example:

> "Before I even speak, I usually assume people will think negatively about me."

Possible representation:

```text
social_evaluation:
    negative_expectation = detected
    actual_feedback = unknown
```

The system should then determine what additional evidence is useful.

---

## 4. Perceived Social Judgment

A person may also focus on how they believe others are evaluating them.

Relevant evidence may include:

* concern about what others think
* monitoring other people's reactions
* interpreting neutral reactions negatively
* worrying about appearing incompetent
* concern about being embarrassed
* concern about being rejected

Example:

> "If someone doesn't smile while I'm talking, I start wondering whether they dislike me."

Possible evidence:

```text
social_evaluation:
    perceived_judgment = detected
    negative_interpretation = possible
```

The system should avoid assuming that the interpretation is objectively correct.

It records the person's perception and emotional response.

---

## 5. Response to Positive and Negative Feedback

Social evaluation can involve both positive and negative feedback.

Relevant evidence may include:

* emotional response to criticism
* emotional response to rejection
* relief after positive feedback
* difficulty accepting positive feedback
* strong concern about negative evaluation
* repeated checking for other people's reactions

The assessment system should distinguish:

```text
expectation
```

from:

```text
actual feedback
```

and from:

```text
emotional reaction
```

These are different forms of behavioral evidence.

---

## 6. Criticism Sensitivity

Sensitivity to criticism can provide additional evidence about reactions to social evaluation.

Relevant evidence may include:

* becoming strongly upset after criticism
* repeatedly thinking about critical comments
* interpreting criticism as evidence of personal failure
* difficulty emotionally recovering from criticism
* avoiding situations where criticism may occur

Example:

> "Even a small criticism can stay on my mind for the rest of the day."

Possible representation:

```text
criticism_sensitivity = detected
persistence = detected
emotional_reactivity = detected
```

The system should not automatically interpret this as high neuroticism.

---

## 7. Social Avoidance

Some people may respond to anticipated negative evaluation by avoiding situations involving possible judgment.

Relevant evidence may include:

* avoiding presentations
* avoiding unfamiliar social situations
* avoiding speaking because of fear of judgment
* avoiding situations where mistakes may be noticed
* reducing participation because of concern about evaluation

Avoidance is an additional behavioral indicator and should be distinguished from simply experiencing concern.

For example:

```text
concern = high
avoidance = low
```

is different from:

```text
concern = high
avoidance = high
```

---

## 8. Post-Event Processing

Social evaluation can also be followed by repetitive thinking after an interaction.

Potential evidence includes:

* replaying what was said
* thinking about mistakes
* wondering what others thought
* imagining how the interaction could have gone differently
* repeatedly evaluating one's own behavior

This can overlap with rumination.

For example:

> "After talking to someone, I sometimes replay the whole conversation and wonder if I sounded stupid."

Possible representation:

```text
social_evaluation = detected
post_event_thinking = detected
rumination = possible
self_evaluation = negative
```

The assessment controller can then determine whether persistence or controllability needs further exploration.

---

## 9. Emotional Reactivity to Social Feedback

A person's emotional response to social evaluation can provide additional behavioral information.

Relevant evidence may include:

* strong distress after criticism
* strong emotional response to rejection
* difficulty calming after negative feedback
* prolonged emotional effects
* increased worry after receiving negative feedback

Example:

> "When someone criticizes me, I keep feeling upset even after the conversation ends."

Possible evidence:

```text
social_feedback = negative
emotional_reactivity = elevated
persistence = detected
```

This can overlap with the emotional-reactivity construct identified in other parts of the knowledge base.

---

## 10. Distinguishing Different Social-Evaluation Patterns

The system should distinguish several stages:

### Before evaluation

```text
negative expectation
```

Example:

> "I expect people won't like what I say."

### During evaluation

```text
sensitivity to feedback
```

Example:

> "I watch their expressions closely while I'm talking."

### After evaluation

```text
emotional reaction
```

Example:

> "Their criticism makes me very upset."

### After the event

```text
post-event repetitive thinking
```

Example:

> "I keep replaying the conversation afterward."

These patterns may occur together, but they should not automatically be treated as the same behavioral construct.

---

## 11. Behavioral Evidence Representation

A social-evaluation state may contain:

```text
social_evaluation:
    context
    negative_expectation
    perceived_judgment
    feedback_type
    criticism_sensitivity
    emotional_reactivity
    avoidance
    post_event_thinking
    persistence
    controllability
```

Not every field needs to be known.

Unknown fields represent potential targets for future adaptive questioning.

---

## 12. Example

User:

> "Before presentations I always think everyone will notice my mistakes."

Possible evidence:

```text
social_evaluation = detected
context = presentation
negative_expectation = detected
fear_of_negative_evaluation = possible
actual_feedback = unknown
emotional_reactivity = unknown
avoidance = unknown
post_event_thinking = unknown
```

The controller should not ask a predetermined next question.

Instead, it should identify the most useful missing evidence.

---

## 13. Example Adaptive Flow

```text
User response
    ↓
"Before presentations I assume people will notice my mistakes."
    ↓
Negative social expectation detected
    ↓
Known:
    context = presentation
    negative expectation = yes
    fear of evaluation = possible
    ↓
Unknown:
    emotional response
    avoidance
    persistence
    ↓
Controller selects a missing evidence target
    ↓
RAG retrieves relevant social-evaluation knowledge
    ↓
LLM generates a context-aware question
```

For example, if emotional response is selected:

> "When you have that thought before a presentation, how strongly does it affect how you feel or behave?"

The exact wording should be generated dynamically.

---

## 14. Relationship to Rumination

Social evaluation and rumination can interact.

For example:

```text
Social event
    ↓
Perceived negative evaluation
    ↓
Emotional reaction
    ↓
Post-event repetitive thinking
```

Therefore, the assessment system should allow more than one behavioral construct to be active for the same response.

A single user response can provide evidence about:

* social evaluation
* self-consciousness
* emotional reactivity
* rumination
* persistence

The system should not force every response into exactly one category.

---

## 15. Interpretation

Social-evaluation-related behavior is one source of behavioral evidence relevant to neuroticism.

It should not be treated as a diagnostic indicator.

The system should describe observed patterns rather than making clinical conclusions.

Appropriate:

> "Your responses indicate strong concern about how others may evaluate you."

Avoid:

> "You have social anxiety."

---

## 16. Relationship to Adaptive RAG

The knowledge in this document supports the following process:

```text
User response
      ↓
Identify social-evaluation evidence
      ↓
Update assessment state
      ↓
Determine missing information
      ↓
Retrieve relevant scientific knowledge
      ↓
Generate one context-aware follow-up question
```

The knowledge base therefore provides scientific grounding.

It does not contain a fixed sequence of questions.

---

## 17. Source

Primary source:

SRC006 — van der Veen, F. M., van der Molen, M. J. W., van der Molen, M. W., & Franken, I. H. A.

*Effects of neuroticism and depressive symptoms on psychophysiological responses to social evaluation in healthy students.*

Cognitive, Affective, & Behavioral Neuroscience, 16, 836–847 (2016).

The study examined responses to social judgment and found that self-reported neuroticism was related to social evaluative predictions and some physiological responses to social feedback.

The study was published as open access under a Creative Commons Attribution 4.0 license.

Source:

https://pmc.ncbi.nlm.nih.gov/articles/PMC5018028/
