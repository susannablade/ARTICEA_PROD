# Echo Archive

Echo Archive is an AI-assisted interpretive art experience built with Streamlit, Gemini 2.5 Flash, and the Art Institute of Chicago API.

The project explores how generative systems can mediate encounters between users and archival artwork while preserving ambiguity, interpretation, and human authorship. Rather than replacing interpretation, Echo Archive is designed to augment it — allowing users to bring their own concepts, tensions, and associations into conversation with artwork pulled from the archive.

---

## Using AI to Support Human Interpretation

Echo Archive is designed to bring users closer to artwork by intertwining their own ideas with archival material from the Art Institute of Chicago, supported by text-based generative AI.

The application intentionally positions AI as an interpretive layer rather than a companion, authority, or emotional surrogate. The goal is to create space for reflection, ambiguity, and personal connection while exploring how generative systems shape encounters with cultural archives.

---

## Tech Stack

* Streamlit
* Python
* Google Gemini 2.5 Flash
* Art Institute of Chicago API
* Resend Email API
* python-dotenv

---

## System Architecture

```text
User Concepts / Reflection Input
        ↓
Artwork Retrieval + Metadata Filtering
        ↓
Streamlit Artwork Display
        ↓
[Gemini 2.5 Flash]
Concise Visual Description
        ↓
Optional AI Interpretation Layer
        ↓
Optional User Reflection
        ↓
Email Archival System
```

---

## Key Design Decisions Across User Workflow

### 1. User Input

User first inputs a concept(s) they’ve been thinking of, then selects “Find an Artwork”

Why: Having the user define concepts before viewing the work forces their own intelligence or supportive intelligence (AI) to draw connections between their real world and the art.


### 2. Artwork Retrieval

A random artwork is selected through the use of randomized pagination and metadata filtering. 

Why: "Surprise & Delight"; Allows users to have one of a kind experience.

To note: Artwork is filtered to prioritize pieces with richer contextual metadata so that later interpretive layers have stronger archival grounding.

### 3. AI-Assisted Descriptions

Gemini 2.5 Flash is prompted to generate concise curatorial descriptions using metadata retrieved from the archive.

Why: My goal is to make the work feel alive to the viewer. Rich descriptions achieve that goal. 

Descriptions are intentionally constrained to remain concise, observational, and aesthetically attentive.


### 4. Concept Connections

User can opt-in for Gemini to connect the work to their input

Why:
* the environmental impact of generative AI
* concerns around outsourcing human interpretation
* the tendency for AI systems to force coherence where none exists

To note: If connections between the artwork and user input are weak, contradictory, or unexpected, the model is prompted to acknowledge tension or contrast rather than forcing symbolic agreement.


### 5. User Reflection

User can input a personal reflection of the work, with or without Gemini connecting concepts

Why: Making space for the human thought and connection within the UI, pushing for a balance in a world of artificial thinking.


### 6. Email Archival System

Users can choose to have the details of the encounter sent to their email.

The archive includes:

* artwork information
* generated descriptions
* concept connections
* user reflections

The intention is to allow users to create small personal archives of interpretive encounters rather than simply bookmarking a museum object.

---

## Gemini Prompt Decisions

### Separation of Description and Interpretation

Visual description and conceptual interpretation are handled independently in order to avoid redundancy and maintain clearer distinctions between observation and interpretation.

The application uses separate prompting layers for:

* visual description
* conceptual interpretation
* user reflection

---

### Interpretation Without Persona Simulation

The application intentionally avoids:

* therapist-style AI behavior
* emotional roleplay
* mystical narration
* companion-style interaction

Instead, Gemini functions as an interpretive layer that connects user concepts to artwork in an analytical, observational, and historically attentive manner.

---

## Considerations During Development

This iteration of Echo Archive was developed alongside ongoing questions surrounding:

* Environmental impact of generative AI
* Outsourcing human interpretation to generative systems
* Preserving ambiguity within AI-assisted experiences
* The tension between computational interpretation and personal meaning
* How archival material changes when mediated through generative interfaces

---

## Known Issues

### UI

* The button currently states “Connect my concepts to this artwork” even though the interpretation layer is prompted not to force weak connections between concepts and artwork
* Certain flows within the reflection and email interaction still need refinement

### Email System

* Resend API is not currently connected to DNS records
* Reflection state can reset during email submission under certain conditions
* User input is not yet included in archival emails

### Artwork Retrieval

* Some ARTIC objects contain placeholder or non-art reference imagery despite image filtering
* Metadata quality varies significantly across the archive

---

## Things I Learned the Hard Way

* Always maintain a sandbox environment before deploying changes live
* Double check `git remote -v` before pushing from local repositories
* Run debugging and testing before deployment
* Manage API keys carefully across `.env`, deployment environments, and repository settings
* Metadata quality matters just as much as prompt engineering in generative systems

---

## Future Directions

* Change UI so that "Connect my Concepts" follows the user reflection rather than preceeds it 
* Develop phrasing to more accurately walk user through process
* Find ways to QA descriptions and interpretations; further manage AI prompts
* Incorporate a chatbot so the user can interact with the “interpretation”
* Develop a small database mapping modern motifs to ancient artwork (250 images max)
* Alternative Project: Focus on Greek myths and statues; develop database, set gemini as translator connecting user input to specific storie

---

# Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Create a `.env` file with:

```env
GEMINI_API_KEY=your_key_here
RESEND_API_KEY=your_key_here
```
