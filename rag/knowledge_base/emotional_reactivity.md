# Emotional Reactivity and Neuroticism

## Purpose

This document summarizes research-informed concepts about emotional reactivity that can be used as behavioral knowledge for the AI Behavioural Analysis Platform.

The purpose is not to diagnose a mental disorder.

The purpose is to help the adaptive chatbot identify conversational evidence related to emotional reactivity and determine what information may still be missing.

---

## 1. What Is Emotional Reactivity?

Emotional reactivity refers to how a person responds when something emotionally meaningful happens.

For conversational assessment, emotional reactivity can be understood through several observable components:

* sensitivity to emotional events
* intensity of the emotional response
* persistence or duration of the response
* difficulty returning to baseline
* perceived impact of the event
* context or trigger of the response

Therefore, emotional reactivity should not be treated as a single yes/no characteristic.

A person may react strongly to an event but recover quickly.

Another person may react moderately but remain emotionally affected for a long time.

These represent different patterns of emotional reactivity.

---

## 2. Sensitivity to Emotional Triggers

Sensitivity concerns how easily an emotionally meaningful event produces a noticeable emotional response.

Potential conversational evidence includes:

* becoming upset over relatively small events
* feeling strongly affected by criticism
* reacting strongly to interpersonal conflict
* becoming emotionally affected by uncertainty
* describing frequent emotional responses to stressful situations

Examples of evidence:

> "Even small comments can really bother me."

> "I don't know why, but little things sometimes affect me for the whole day."

The chatbot should not assume that sensitivity automatically indicates high neuroticism.

It should treat sensitivity as one behavioral signal among multiple pieces of evidence.

---

## 3. Emotional Intensity

Intensity describes how strongly the person experiences the emotional response after a trigger.

Potential evidence includes:

* strong fear or worry
* intense frustration
* feeling overwhelmed
* strong embarrassment
* unusually strong emotional reactions to criticism
* describing an event as emotionally overwhelming

The system should distinguish between:

* the occurrence of an emotion
* the strength of the emotion

For example:

> "I was a little nervous."

and

> "I was extremely anxious and couldn't think clearly."

contain different information about emotional intensity.

---

## 4. Emotional Persistence

Persistence describes how long the emotional response continues after the triggering event.

Potential evidence includes:

* remaining upset long after an event
* continuing to think about an upsetting situation
* difficulty emotionally letting go
* carrying negative feelings into later activities
* repeatedly experiencing the same emotional reaction

Persistence is particularly useful when combined with repetitive thinking.

For example:

> "The situation happened in the morning, but I was still upset about it at night."

This provides evidence about duration/persistence rather than merely intensity.

---

## 5. Recovery After Emotional Events

Recovery concerns how easily the person returns to their normal emotional state after an upsetting or stressful event.

Potential evidence includes:

* recovering quickly
* needing considerable time to calm down
* remaining emotionally affected after the event has ended
* difficulty returning to normal activities
* describing emotional "spillover" into later situations

Recovery should be treated as a separate attribute from intensity.

A highly intense emotional reaction does not necessarily mean poor recovery.

Similarly, a moderate reaction may persist for a long time.

---

## 6. Emotional Reactivity to Stressors

Research on daily emotional processes has found that neuroticism is associated with differences in negative affect and emotional reactivity to stressors.

This supports examining not only whether stressful events occur, but also how strongly the person reacts to them.

For conversational assessment, useful evidence includes:

* type of stressor
* emotional response
* intensity
* duration
* recovery
* repeated effects across situations

The system should avoid interpreting a single stressful event as sufficient evidence of a stable personality trait.

Repeated patterns across contexts provide stronger behavioral information.

---

## 7. Negative Emotional Reactivity

Neuroticism is particularly relevant to patterns involving negative emotional experiences.

Potential conversational evidence includes repeated reactions involving:

* worry
* fear
* frustration
* sadness
* embarrassment
* self-consciousness
* feeling overwhelmed
* sensitivity to criticism

However, the chatbot must not treat these individual emotions as diagnostic indicators.

The goal is to identify patterns of emotional response that may be relevant to personality assessment.

---

## 8. Emotional Variability

Emotional variability refers to changes in emotional state across situations or over time.

Potential evidence includes:

* emotions changing substantially in response to events
* repeated shifts in emotional intensity
* different levels of emotional response to similar situations
* describing emotional reactions as unpredictable

The system should distinguish:

```text
emotional_intensity
```

from:

```text
emotional_variability
```

A person can experience consistently strong emotions without large variation.

---

## 9. Trigger and Context

Emotional reactions should always be interpreted in relation to their context.

Possible triggers include:

* criticism
* interpersonal conflict
* uncertainty
* perceived failure
* social evaluation
* unexpected changes
* stressful responsibilities
* negative feedback
* personal mistakes
* future-related uncertainty

The chatbot should identify the trigger before interpreting the emotional response.

For example:

```text
Trigger:
negative feedback

Response:
strong embarrassment

Intensity:
high

Persistence:
several hours

Recovery:
difficult
```

This is more useful than storing only:

```text
emotion = embarrassment
```

---

## 10. Subjective Emotional Experience

The chatbot receives text rather than physiological measurements.

Therefore, the system should primarily use the person's own description of their experience.

Useful evidence includes statements about:

* what they felt
* how strong it felt
* how long it lasted
* what caused it
* whether they could control it
* whether it affected later activities
* how they recovered

The system should not infer physiological states that cannot be observed from text.

For example, it should not claim:

> "Your heart rate increased."

unless physiological data actually exists.

---

## 11. Behavioral Evidence Representation

For the adaptive chatbot, emotional reactivity can be represented as:

```yaml
emotional_reactivity:
    detected: true/false/unknown

    trigger:
        type: known/unknown
        context: text/unknown

    sensitivity:
        level: low/moderate/high/unknown

    intensity:
        level: low/moderate/high/unknown

    persistence:
        level: low/moderate/high/unknown

    recovery:
        level: quick/moderate/difficult/unknown

    controllability:
        level: easy/moderate/difficult/unknown

    functional_impact:
        level: none/mild/moderate/high/unknown

    repeated_pattern:
        present/absent/unknown
```

Unknown values are important.

The chatbot should not invent information that the user has not provided.

---

## 12. Why Multiple Attributes Matter

Consider these two responses:

### Response A

> "I got nervous before the presentation, but after it was over I felt fine."

Possible evidence:

```yaml
sensitivity: moderate
intensity: moderate
persistence: low
recovery: quick
```

### Response B

> "I kept thinking about the presentation for hours afterward and couldn't calm myself down."

Possible evidence:

```yaml
sensitivity: present
intensity: potentially high
persistence: high
recovery: difficult
repetitive_thought: present
```

The second response contains substantially more information about persistence and recovery.

Therefore, the chatbot should ask about the missing attributes instead of repeatedly asking general questions about emotions.

---

## 13. Relationship With Repetitive Negative Thinking

Emotional reactivity can interact with repetitive negative thinking.

For example:

```text
stressful event
      ↓
strong emotional reaction
      ↓
continued negative thinking
      ↓
emotion remains active
      ↓
difficulty recovering
```

This does not mean that every case follows this sequence.

Instead, the adaptive chatbot can investigate whether such a pattern exists for a particular user.

If the user has already provided strong evidence about emotional intensity but nothing about persistence, the controller can prioritize persistence or recovery.

---

## 14. Relationship With Social Evaluation

Social situations can also produce emotionally meaningful reactions.

Possible evidence includes:

* strong reaction to criticism
* embarrassment after social mistakes
* worry about how others perceive the person
* prolonged emotional response after negative feedback
* avoiding situations because of anticipated emotional discomfort

This can overlap with:

* social evaluation
* self-consciousness
* rumination
* emotional reactivity

The controller should therefore avoid treating these categories as completely independent.

Evidence can contribute to multiple behavioral constructs when appropriate.

---

## 15. Relationship With Neuroticism

Research indicates that personality, including neuroticism, is associated with individual differences in emotional processes and reactivity.

However, emotional reactivity is not identical to neuroticism.

Therefore:

```text
emotional_reactivity
        ≠
neuroticism
```

Instead:

```text
emotional_reactivity
        +
other behavioral evidence
        ↓
neuroticism-related evidence
```

The neuroticism prediction model remains responsible for producing the model-based neuroticism estimate.

The behavioral assessment layer provides interpretable conversational evidence.

---

## 16. Role in the Adaptive RAG Chatbot

The emotional reactivity knowledge should not be converted into a fixed list of questions.

Instead, it informs the adaptive controller.

Example:

```text
User response:
"I get really upset when someone criticizes my work."

Known evidence:
trigger = criticism
emotion = upset
intensity = high

Missing evidence:
persistence
recovery
controllability
functional impact
```

The controller may therefore decide that the next question should investigate persistence or recovery.

The RAG system retrieves relevant scientific knowledge about emotional reactivity.

The language model then generates one natural follow-up question.

Conceptually:

```text
User response
      ↓
Behavioral evidence extraction
      ↓
Assessment state
      ↓
Identify missing evidence
      ↓
Retrieve emotional-reactivity knowledge
      ↓
Generate one context-aware question
```

---

## 17. What RAG Should and Should Not Do

### RAG should:

* provide scientifically grounded context
* explain behavioral constructs to the generation system
* support evidence-based question generation
* help the system distinguish related constructs
* provide source attribution internally

### RAG should not:

* directly diagnose the user
* replace the neuroticism prediction model
* decide that a user is neurotic based on one response
* generate a predetermined 24-question sequence
* invent evidence that the user did not provide

---

## 18. Safety and Interpretation

The chatbot is a behavioral assessment/research system, not a clinical diagnostic system.

Statements about emotional reactivity should therefore use cautious language.

Preferred:

> "This response contains evidence of a strong emotional reaction to criticism."

Avoid:

> "You have an emotional regulation disorder."

Preferred:

> "This pattern may be relevant to neuroticism-related behavioral assessment."

Avoid:

> "This proves that you have high neuroticism."

The system should distinguish personality-related behavioral evidence from clinical diagnosis.

---

## 19. Main Design Principle

The central design principle is:

> Assess the pattern of emotional response, not simply the presence of an emotion.

The system should therefore consider:

```text
trigger
+
sensitivity
+
intensity
+
persistence
+
controllability
+
recovery
+
functional impact
+
repeated pattern
```

This multidimensional representation makes the chatbot more suitable for adaptive behavioral assessment than a simple fixed question sequence.
