# Doctor Reservation AI Agent

**Technologies**
Large Language Models (LLMs)
Retrieval-Augmented Generation (RAG)
Hybrid Search
Dense Vector Search
Sparse / BM25 Retrieval
Semantic Reranking
Natural Language Processing (NLP)
Structured Information Extraction
Stateful AI Agents
Human-in-the-Loop
Workflow Orchestration

**Stack**
Python
LangGraph
LangChain
Qdrant
Llama.cpp inference engine.(local LLM, Embedding and Reranker)
FastAPI
PostgreSQL
Redis
Next.js
WebSockets

---

# 1. Project Overview

From a user's perspective, the interaction might look like:

> «من دنبال دکتر مغز و اعصاب می‌گردم.»

But this single sentence does not contain everything required to make an appointment.

The system may still need to determine:

* What type of doctor the patient needs
* Who the patient is
* The patient's phone number
* The patient's city
* Which doctors match the request
* Which doctors are actually available
* Which appointment is appropriate
* How to construct the final confirmation

The challenge becomes even greater when users communicate naturally, make spelling mistakes, provide information incrementally, or change the direction of the conversation.

The goal of this project was therefore not to build a simple chatbot.

It was to build a **stateful AI agent capable of managing an end-to-end appointment workflow through natural language.**

The current implementation demonstrates doctor discovery and reservation, while the underlying architecture is designed so that additional healthcare-related workflows and capabilities can be added without fundamentally changing the system.

---

# 2. A Real Conversation with the Agent

The easiest way to understand the system is to look at an actual interaction.

The user starts with a simple request:

> **User:**
> سلام وقت بخیر

The agent recognizes this as a conversational interaction and responds naturally:

> **Assistant:**
> سلام! وقت شما بخیر؛ چطور می‌توانم در بخش پذیرش به شما کمک کنم؟

The user then makes a request containing a spelling mistake:

> **User:**
> من دنبال دکنر مغض و اعصاب می گردم.

Despite the imperfect input, the system understands the intended specialty: neurology.

Instead of immediately searching or making assumptions, the agent identifies the information still required for the workflow:

> **Assistant:**
> برای شروع، لطفاً نام کامل بیمار (که ممکن است خودتان یا فرد دیگری باشید) و شهر محل سکونت ایشان را بفرمایید. همچنین یک شماره تماس برای ارتباط آینده لازم است.

The user provides their name:

> **User:**
> محمد علی ایراندوست هستم.

The agent updates its internal state and asks only for the remaining information:

> **Assistant:**
> شماره تماس شما و شهر محل سکونتتان چیست؟

The user provides a phone number:

> **User:**
> 09380075497

The agent records it and continues collecting the missing requirement:

> **Assistant:**
> شماره تماس شما ثبت شد. لطفاً شهر محل سکونت خود را بفرمایید.

Finally:

> **User:**
> من در مشهد زندگی می کنم.

At this point, the required information has been collected and the system can execute the reservation workflow.

The resulting confirmation contains structured appointment information:

```text
✅ نوبت شما با موفقیت ثبت شد

👨‍⚕️ پزشک: دکتر مایکل چن
🧠 تخصص: متخصص مغز و اعصاب

📅 تاریخ: یکشنبه 15 شهریور 1405
🕐 ساعت: 10:00

📍 محل: مرکز علوم اعصاب پاسیفیک مشهد، بلوار وکیل‌آباد

👤 بیمار: محمد علی ایراندوست

💳 هزینه ویزیت: 300 تومان

📞 تلفن مرکز: ۰۵۱-۵۵۵۵-۰۴۵۶

🔖 کد پیگیری: AP-2-0506151000

وضعیت نوبت: تأیید شده ✅

لطفاً ۱۰ تا ۱۵ دقیقه پیش از زمان نوبت در مرکز حضور داشته باشید.
```

This interaction demonstrates the core capability of the system:

**The user does not need to understand the underlying reservation procedure.**

They simply communicate naturally, and the agent manages the workflow.

---

# 3. From Chatbot to Agent

A traditional chatbot primarily performs:

```text
User Message
     ↓
LLM
     ↓
Response
```

That architecture is insufficient for appointment booking.

The reservation system instead behaves more like:

```text
User Message
     ↓
Understand Intent
     ↓
Extract Information
     ↓
Update State
     ↓
Determine Missing Requirements
     ↓
Ask for Missing Information
     ↓
Search / Retrieve
     ↓
Filter Candidates
     ↓
Rerank
     ↓
Check Availability
     ↓
Book Appointment
     ↓
Generate Confirmation
```

The LLM is therefore only one component of the system.

It acts as the language and reasoning layer that coordinates a collection of deterministic and machine-learning components.

---

# 4. Stateful Requirement Collection

One of the most important components is the appointment state.

The system maintains structured requirements such as:

```python
appointment_requirements = [
    {"doctor": None},
    {"date": None},
    {"time": None},
    {"address": None},
    {"patient": None},
    {"phone_number": None},
]
```

The state changes as the conversation progresses.

For example:

```text
Initial State

doctor       = None
date         = None
time         = None
address      = None
patient      = None
phone_number = None
```

After the user provides their name:

```text
patient      = "محمد علی ایراندوست"
```

After providing their phone number:

```text
phone_number = "09380075497"
```

After providing their city:

```text
address      = "مشهد"
```

The agent can therefore determine what is known and what is missing at every point in the conversation.

This prevents the system from repeatedly asking questions that the patient has already answered.

---

# 5. The Agent Understands Incremental Input

Users rarely provide all required information in one message.

A user might say:

> «یه متخصص مغز و اعصاب میخوام.»

Then:

> «محمد علی هستم.»

Then:

> «مشهد.»

Then:

> «فردا صبح.»

The system needs to understand that each message is not an independent request.

Each message modifies the same underlying workflow state.

This creates a fundamental distinction between:

**conversation history**

and

**structured application state**.

The conversation provides context.

The structured state provides reliable information that the application can actually operate on.

---

# 6. Intent Classification and Routing

Before performing expensive operations, the system determines what the user is trying to accomplish.

The current intent structure includes categories such as:

```text
casual
looking_for_doctor
partial_input
book_appointment
```

This allows the system to route different types of messages into different parts of the workflow.

For example:

```text
"سلام"
    ↓
casual
```

```text
"یه متخصص مغز و اعصاب میخوام"
    ↓
looking_for_doctor
```

```text
"مشهد"
    ↓
partial_input
```

```text
"همین دکتر رو رزرو کن"
    ↓
book_appointment
```

The classifier therefore acts as an entry point into the agentic workflow.

---

# 7. Handling Imperfect Human Language

Real users do not always write cleanly.

The example conversation contains:

> «دکنر مغض و اعصاب»

instead of:

> «دکتر مغز و اعصاب»

The system still needs to infer the intended meaning.

This is one of the areas where an LLM has an advantage over a purely rule-based system.

The agent can reason over:

* Spelling mistakes
* Informal language
* Missing information
* Persian conversational patterns
* Different ways of expressing the same requirement

The objective is not simply to classify perfectly formatted text.

The objective is to understand **what the patient means**.

---

# 8. Finding the Right Doctor

Once the system understands the patient's request and has enough information to begin searching, it needs to identify appropriate doctors.

Doctor records can contain structured and descriptive information such as:

* Name
* Specialty
* Profession
* Title
* Description
* Location
* Availability
* Patient acceptance status

The user's request is transformed into a retrieval query.

The system then searches the doctor knowledge base.

---

# 9. Hybrid Retrieval

A single retrieval technique is not always sufficient.

Semantic retrieval is useful for understanding meaning.

Lexical retrieval is useful when exact words, names, locations, or specialty terms matter.

The system therefore combines dense retrieval with sparse/BM25 retrieval.

```text
                    User Query
                        │
              ┌─────────┴─────────┐
              ↓                   ↓
       Dense Retrieval       Sparse Retrieval
              │                  (BM25)
              │                   │
              └─────────┬─────────┘
                        ↓
                   RRF Fusion
                        ↓
                Candidate Doctors
```

The dense retriever captures semantic relationships.

BM25 provides lexical matching.

The resulting candidates are then combined using Reciprocal Rank Fusion.

The retrieval layer is implemented using **Qdrant**.

---

# 10. Retrieval Is Only Candidate Generation

Retrieval should not be confused with the final decision.

The retriever answers:

> "Which doctors might be relevant?"

It does not necessarily answer:

> "Which doctor should actually be used?"

For example, a retrieved doctor could be semantically very relevant but:

* Located in another city
* Not accepting patients
* Unavailable
* Incompatible with the requested appointment constraints

Therefore the system introduces additional processing stages.

```text
Query
  ↓
Hybrid Retrieval
  ↓
Candidate Doctors
  ↓
Hard Filtering
  ↓
Reranking
  ↓
Eligible Doctors
```

---

# 11. Deterministic Filtering

Some decisions should not be left to an LLM.

If a patient requires a doctor in Mashhad, a doctor located in Tehran should not become eligible simply because their profile is semantically similar.

Similarly, a doctor who is not accepting patients should not be selected.

These are deterministic business rules.

For example:

```python
candidate_doctors = []

for doctor in doctors:
    if (
        doctor["is_accepting_patients"]
        and patient_city in doctor["location"]
    ):
        candidate_doctors.append(doctor)
```

This separation is fundamental to the architecture.

**The model handles ambiguity.**

**The application handles hard constraints.**

---

# 12. Neural Reranking

After initial retrieval and filtering, the remaining candidates can be reranked using a dedicated reranker.

The retriever is optimized for efficiently finding a relatively small candidate set.

The reranker performs a more precise relevance comparison between:

```text
Patient Query
        +
Doctor Document
```

The resulting architecture is:

```text
User Query
    ↓
Hybrid Retrieval
    ↓
Top-K Candidates
    ↓
Reranker
    ↓
Ranked Candidates
```

This allows the system to use relatively inexpensive retrieval for candidate generation and a more computationally expensive model only where it provides value.

---

# 13. Relevance vs. Eligibility

A critical architectural distinction is the difference between **relevance** and **eligibility**.

Consider:

```text
Doctor A
Specialty: Neurology
Location: Tehran
Relevance: 0.95
Eligible: NO
```

and:

```text
Doctor B
Specialty: Neurology
Location: Mashhad
Relevance: 0.90
Eligible: YES
```

Doctor A may be the better semantic match but still cannot satisfy the patient's requirements.

The system therefore does not simply select the highest model score.

Instead:

```text
Semantic Relevance
        +
Business Constraints
        +
Availability
        ↓
Final Candidate
```

This makes the system substantially more reliable than an LLM-only approach.

---

# 14. Availability and Appointment Selection

Finding a doctor is only part of the problem.

The system must also identify an actual appointment.

The booking workflow therefore moves from:

```text
Doctor Discovery
```

to:

```text
Appointment Availability
```

The system can evaluate available appointment slots according to the patient's requirements.

For example:

```text
Doctor:
Dr. Michael Chen

Specialty:
Neurology

Location:
Mashhad

Available:
Sunday
10:00
```

The system can then use this structured information to construct the final appointment.

---

# 15. Booking as a Controlled Action

There is an important architectural boundary between **recommending an appointment** and **actually booking one**.

Searching and ranking are informational operations.

Booking creates a real-world side effect.

The system therefore treats the booking operation as a distinct workflow stage.

Conceptually:

```text
Understand
    ↓
Search
    ↓
Filter
    ↓
Rank
    ↓
Validate
    ↓
Book
    ↓
Confirm
```

This separation makes it possible to introduce additional safeguards later, such as:

* Explicit user confirmation
* Human review
* Double-checking appointment availability
* Revalidating patient information
* Preventing duplicate bookings

The architecture supports these controls without requiring the conversational layer to be redesigned.

---

# 16. Human-in-the-Loop

The project also supports a human-in-the-loop architecture.

This is particularly useful when the system needs to make a decision that has a real-world consequence.

A possible workflow is:

```text
Search
  ↓
Filter
  ↓
Rerank
  ↓
Candidate Doctor
  ↓
Human Review / Confirmation
  ↓
Appointment Selection
  ↓
Booking
```

The important point is that human intervention does not replace the AI.

Instead, it creates a controllable boundary around high-impact actions.

The same architecture can later support different policies:

```text
Low-risk operation
      ↓
Fully automated

High-confidence booking
      ↓
Automatic booking

Low-confidence / ambiguous case
      ↓
Human review
```

---

# 17. Stateful Agent Architecture with LangGraph

The workflow is naturally represented as a graph rather than a single LLM call.

A simplified version is:

```text
                 ┌────────────────────┐
                 │ Intent Classifier  │
                 └──────────┬─────────┘
                            ↓
                 ┌────────────────────┐
                 │ Requirement        │
                 │ Extraction         │
                 └──────────┬─────────┘
                            ↓
                 ┌────────────────────┐
                 │ State Update       │
                 └──────────┬─────────┘
                            ↓
                 ┌────────────────────┐
                 │ Missing Data?      │
                 └───────┬─────┬──────┘
                         │     │
                       YES      NO
                         │     │
                         ↓     ↓
                    Ask User   Search
                               ↓
                       Hybrid Retrieval
                               ↓
                           Filtering
                               ↓
                           Reranking
                               ↓
                         Availability
                               ↓
                            Booking
                               ↓
                         Confirmation
```

**LangGraph** provides the stateful orchestration layer required for this type of workflow.

Each node performs a focused task instead of asking one model to control the entire application.

---

# 18. Separation of Responsibilities

The architecture deliberately distributes responsibility across different components.

### LLM

Responsible for:

* Natural-language understanding
* Intent interpretation
* Information extraction
* Handling ambiguous language
* Conversational interaction
* Workflow decisions

### Retrieval System

Responsible for:

* Candidate discovery
* Semantic search
* Lexical search

### Reranker

Responsible for:

* Fine-grained relevance scoring
* Ordering retrieved candidates

### Application Logic

Responsible for:

* Hard constraints
* Patient state
* Availability validation
* Booking logic
* Data integrity

### Agent Framework

Responsible for:

* Workflow orchestration
* State transitions
* Conditional routing
* Interrupts / human review

This separation is one of the central engineering decisions of the project.

---

# 19. The System Is Not Limited to Doctor Booking

Although doctor reservation is the current implemented workflow, the architecture is intentionally broader.

The same agentic infrastructure can support related functionality such as:

### Doctor Discovery

> "I need a cardiologist in Mashhad."

### Appointment Search

> "Does Dr. Chen have anything available tomorrow morning?"

### Appointment Booking

> "Book the earliest available appointment."

### Rescheduling

> "Move my appointment to next week."

### Cancellation

> "Cancel my appointment."

### Doctor Comparison

> "Which neurologist is better for stroke rehabilitation?"

### Location-Based Search

> "Find a neurologist near me."

### Availability Queries

> "Which doctors have appointments this weekend?"

### Patient Management

The same stateful architecture can be extended to manage additional patient information and workflows.

The important point is that these are **new capabilities on top of the same agent infrastructure**, rather than entirely separate systems.

---

# 20. Extensible Workflow Architecture

The system can therefore evolve from:

```text
Doctor Reservation Agent
```

into:

```text
Healthcare AI Agent
        │
        ├── Doctor Discovery
        ├── Appointment Booking
        ├── Appointment Rescheduling
        ├── Cancellation
        ├── Availability Search
        ├── Doctor Comparison
        ├── Patient Information
        └── Additional Healthcare Workflows
```

New capabilities can be introduced as additional states, nodes, tools, or sub-workflows.

This is one of the major benefits of designing the system as an agentic workflow rather than as a single-purpose chatbot.

---

# 21. Technology Stack

## AI / NLP

* Large Language Model
* Embedding model
* BM25 / sparse retrieval
* Neural reranker

## Agent Orchestration

* LangGraph
* LangChain

## Retrieval

* Qdrant
* Dense vectors
* Sparse vectors
* Reciprocal Rank Fusion

## Backend

* Python
* FastAPI
* PostgreSQL
* Redis

## Frontend

* Next.js
* WebSocket communication

## Infrastructure

* Docker Compose
* GPU-based inference
* Local model serving

---

# 22. What Makes the System Different?

The interesting part of the project is not simply that an LLM can answer:

> "Which neurologists are available?"

The interesting part is that the system can manage the **entire interaction required to reach that answer**.

It can begin with incomplete and imperfect information:

```text
"من دنبال دکنر مغض و اعصاب می گردم"
```

and progressively transform the conversation into structured application state:

```text
Specialty:
Neurology

Patient:
محمد علی ایراندوست

Phone:
09380075497

City:
Mashhad
```

That structured state can then drive the actual application workflow:

```text
Natural Language
       ↓
Intent
       ↓
Requirements
       ↓
State
       ↓
Retrieval
       ↓
Filtering
       ↓
Reranking
       ↓
Availability
       ↓
Booking
       ↓
Confirmation
```

This is the difference between a conversational AI and an AI agent integrated into a real application.

---

# 23. The Core Engineering Principle

The most important lesson from the project is the separation of responsibilities.

An LLM is powerful at dealing with uncertainty.

Software is powerful at enforcing certainty.

Therefore:

> **Let the model handle language and ambiguity. Let deterministic software handle constraints, data, and actions.**

Retrieval narrows the search space.

Reranking improves relevance.

Business logic enforces constraints.

State management maintains the workflow.

And the agent orchestrates everything.

The result is not an LLM wrapped around a database.

It is a **composable AI system in which the LLM is one component of a larger deterministic workflow.**

---

# 24. Final Architecture

The current system can be summarized as:

```text
                         USER
                           │
                           ↓
                  Natural Language
                           │
                           ↓
                  ┌─────────────────┐
                  │ Intent / LLM    │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Requirement     │
                  │ Extraction      │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Stateful        │
                  │ Conversation    │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Missing Data?   │
                  └───────┬─────────┘
                          YES
                           │
                           ↓
                     Ask Patient
                           │
                           └───────────────┐
                                           │
                                          NO
                                           ↓
                              ┌─────────────────────┐
                              │ Query Construction  │
                              └──────────┬──────────┘
                                         ↓
                              ┌─────────────────────┐
                              │ Hybrid Retrieval    │
                              │ Dense + BM25        │
                              └──────────┬──────────┘
                                         ↓
                              ┌─────────────────────┐
                              │ Hard Filtering      │
                              └──────────┬──────────┘
                                         ↓
                              ┌─────────────────────┐
                              │ Neural Reranker     │
                              └──────────┬──────────┘
                                         ↓
                              ┌─────────────────────┐
                              │ Availability        │
                              └──────────┬──────────┘
                                         ↓
                              ┌─────────────────────┐
                              │ Booking Workflow    │
                              └──────────┬──────────┘
                                         ↓
                              ┌─────────────────────┐
                              │ Confirmation        │
                              └──────────┬──────────┘
                                         ↓
                                        USER
```

---

# 25. Final Result

The final product is an AI-powered appointment agent capable of taking a patient from an informal conversational request to a structured appointment confirmation.

The user does not need to know:

* Which information is required
* How doctors are indexed
* How retrieval works
* How candidates are ranked
* How availability is checked
* How the booking workflow is executed

They simply communicate with the system.

Behind the conversation, a multi-stage AI and software architecture handles the complexity.

And because the architecture is modular, the current doctor-reservation capability is only the beginning.

The same foundation can be extended into a much broader healthcare-agent platform where new workflows, tools, data sources, business rules, and AI capabilities can be added as the system evolves.
