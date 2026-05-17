# Echo Archive

Echo Archive is an AI-assisted interpretive art experience built with Streamlit, Gemini 2.5 Flash, and the Art Institute of Chicago API.

Users submit a concept or reflection and are paired with a randomly selected archival artwork. The system uses generative AI to produce a concise description of the artwork and an optional interpretation connecting user input to museum metadata.

The goal is to study how generative systems mediate interpretation of structured cultural data.

---

## Tech Stack

* Python
* Streamlit
* Google Gemini 2.5 Flash
* Art Institute of Chicago API
* Resend Email API
* python-dotenv
* requests

---

## System Architecture

```text
User Input (concept / reflection)
        ↓
Random Artwork Sampling (ARTIC API)
        ↓
Metadata Filtering (image + contextual fields required)
        ↓
Streamlit UI Display
        ↓
Gemini 2.5 Flash
→ Curatorial Description (metadata-grounded)
        ↓
Optional Interpretation Layer (user input + artwork context)
        ↓
User Reflection
        ↓
Email Export (Resend API)
```

---

## Core Features

* Random artwork retrieval via Art Institute of Chicago API
* Metadata filtering to ensure usable records (image + context required)
* AI-generated curatorial descriptions grounded in metadata
* Optional AI interpretation connecting user input to artwork
* User reflection input capture
* Email export of full session archive
* Session persistence using Streamlit state

---

## Data / System Design Notes

* Artwork selection uses random page sampling over a paginated API

* Each response is filtered for:

  * valid image availability (`image_id`)
  * contextual metadata (description, provenance, artist info, etc.)

* One artwork is randomly selected per session

* Streamlit `session_state` is used to persist:

  * selected artwork
  * generated outputs
  * user inputs and reflection data

---

## AI Components

### Curatorial Description

Generates a concise, metadata-grounded description of the artwork. Output is constrained to be:

* observational
* non-interpretive
* concise (≤4 sentences)

### Interpretation Layer

Connects user input to artwork context using Gemini.

Design constraints:
* allows indirect or non-literal relationships
* avoids forced symbolic alignment
* acknowledges weak or ambiguous connections when appropriate
* * concise (≤4 sentences) which prevents contrived language

---

## Limitations

* No QA to evaluate GenAI 
* No error logs for ARTIC API 
* No persistent storage for previously shown artworks
* Random sampling may result in repeated or similar works across sessions
* Metadata quality varies across Art Institute dataset
* Session state is limited to individual user sessions
* AI outputs are generated in real time (no caching layer)

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_key_here
RESEND_API_KEY=your_key_here
```

---
