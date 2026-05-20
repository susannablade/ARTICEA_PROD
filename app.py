import os
import random
import re
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
import smtplib
from email.message import EmailMessage


# ---------------------------
# CONFIG
# ---------------------------
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

GMAIL_USER = os.getenv(
    "GMAIL_USER"
)

GMAIL_APP_PASSWORD = os.getenv(
    "GMAIL_APP_PASSWORD"
)

ARTIC_API_URL = (
    "https://api.artic.edu/api/v1/artworks"
)

session = requests.Session()

# ---------------------------
# SESSION STATE
# ---------------------------
DEFAULT_STATE = {
    "artwork": None,
    "description": "",
    "interpretation": "",
    "reflection_text": "",
    "user_input": "",
}

for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ---------------------------
# HELPERS
# ---------------------------
def build_image_url(image_id):

    return (
        f"https://www.artic.edu/iiif/2/"
        f"{image_id}/full/843,/0/default.jpg"
    )


def valid_email(email):

    pattern = r"^[^@]+@[^@]+\.[^@]+$"

    return re.match(pattern, email)


def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        if (
            response
            and hasattr(response, "text")
            and response.text
        ):

            return response.text.strip()

    except Exception as e:

        print(f"Gemini error: {e}")

    return "The archive remains quiet."


# ---------------------------
# ARTWORK RETRIEVAL
# ---------------------------
def get_random_artwork(retries=5):

    for _ in range(retries):

        random_page = random.randint(1, 500)

        try:

            response = session.get(
                ARTIC_API_URL,
                params={
                    "page": random_page,
                    "limit": 25,
                    "fields": (
                        "id,title,image_id,artist_title,"
                        "artist_display,date_display,"
                        "medium_display,dimensions,"
                        "description,classification_title,"
                        "style_title,theme_titles,"
                        "provenance_text,exhibition_history"
                    )
                },
                timeout=10
            )

            response.raise_for_status()

            data = response.json().get(
                "data",
                []
            )

        except Exception as e:

            print(f"ARTIC API error: {e}")

            continue

        artworks = []

        for obj in data:

            image_id = obj.get("image_id")

            if not image_id:
                continue

            has_context = any([
                obj.get("description"),
                obj.get("provenance_text"),
                obj.get("artist_display"),
                obj.get("exhibition_history")
            ])

            if not has_context:
                continue

            artworks.append({
                "id": obj.get("id"),
                "title": obj.get("title") or "Untitled",
                "artist": (
                    obj.get("artist_title")
                    or "Unknown Artist"
                ),
                "artist_display": (
                    obj.get("artist_display")
                    or ""
                ),
                "date": (
                    obj.get("date_display")
                    or "Unknown Date"
                ),
                "medium": (
                    obj.get("medium_display")
                    or "Unknown Medium"
                ),
                "dimensions": (
                    obj.get("dimensions")
                    or ""
                ),
                "description": (
                    obj.get("description")
                    or ""
                ),
                "classification": (
                    obj.get("classification_title")
                    or ""
                ),
                "style": (
                    obj.get("style_title")
                    or ""
                ),
                "themes": (
                    obj.get("theme_titles")
                    or []
                ),
                "provenance": (
                    obj.get("provenance_text")
                    or ""
                ),
                "exhibition_history": (
                    obj.get("exhibition_history")
                    or ""
                ),
                "image": build_image_url(
                    image_id
                )
            })

        if artworks:

            return random.choice(
                artworks
            )

    return None


# ---------------------------
# DESCRIPTION
# ---------------------------
def generate_description(artwork):

    prompt = f"""
    You are writing a concise curatorial
    description for a museum visitor. Your goal is 
    to make art more relatbale to the public.
    Always reference principles of art and design
    present in the work, but make it accesible to layman.
    

    Artwork Information:

    Title: {artwork['title']}
    Artist: {artwork['artist']}
    Artist Bio: {artwork['artist_display']}
    Date: {artwork['date']}
    Medium: {artwork['medium']}
    Classification: {artwork['classification']}
    Style: {artwork['style']}

    Themes:
    {
        ', '.join(artwork['themes'])
        if artwork['themes']
        else 'None listed'
    }

    Museum Description:
    {artwork['description']}

    Provenance:
    {artwork['provenance']}

    Exhibition History:
    {artwork['exhibition_history']}


    Guidelines:
    - Maximum 4 sentences
    - Use the archival context when relevant
    - Note the date for historical context
    - Connect visual qualities to material,
      historical, or atmospheric details
    - Allow subtle aesthetic language
    - Do not address the viewer directly
    - Do not over-explain symbolism
    - Avoid academic stiffness
    - Don't be too forceful

    Output only the description.
    """

    return ask_gemini(prompt)


# ---------------------------
# INTERPRETATION
# ---------------------------
def generate_interpretation(
    user_input,
    artwork,
    description
):

    prompt = f"""
    A user entered the following concept,
    thought, or tension:

    "{user_input}"

    Artwork:
    {artwork['title']}
    by {artwork['artist']}

    Visual Description:
    "{description}"

    Artwork Context:
    - Date: {artwork['date']}
    - Style: {artwork['style']}
    - Classification: {artwork['classification']}

    Themes:
    {
        ', '.join(artwork['themes'])
        if artwork['themes']
        else 'None listed'
    }

    Write a concise curatorial interpretation
    connecting the user's idea to the artwork. 
    If the connection is loose or unexpected,
    acknowledge the contrast or coincidence 
    rather than forcing coherence. Always end on a question
    that invites the user to reflect on the artwork.

    Guidelines:
    - Use both visual and historical contex
    - Consider artistic movements,
      tensions, and cultural atmosphere
    - Connections may be indirect,
      historical, atmospheric,
      material, or contrasting
    - Allow the artwork to resist,
      complicate, or soften
      the user's concept
    - The relationship does not need
      to be literal
    - Do not force symbolic agreement
      between the artwork and
      the user's idea
    - Do not overstate weak connections.
    - Avoid therapy-like language
    - Avoid mystical narration
    - Sound perceptive, historically aware,
      and aesthetically attentive
    - Maximum 4 sentences

    Output only the interpretation.
    """

    return ask_gemini(prompt)


# ---------------------------
# EMAIL
# ---------------------------
def send_archive_email(
    recipient_email,
    artwork,
    user_input,
    description,
    interpretation,
    reflection
):

    subject = (
        f"Echo Archive — "
        f"{artwork['title']}"
    )

    html_body = f"""
    <h2> Reflection Record </h2>

    <h3><a href="{artwork['image']}">
    View Artwork Here
    </a></h3>

    <p>
    <strong>{artwork['title']}</strong><br>
    {artwork['artist']}<br>
    {artwork['date']}<br>
    {artwork['medium']}

    </p>

    <h3>Visual Description</h3>

    <p>{description}</p>
    
    <h3>Your Original Input</h3>

    <p>{user_input}</p>

    <h3>Concept Connections</h3>

    <p>{interpretation}</p>

    <h3>Your Reflection</h3>

    <p>{reflection}</p>

    <a href="https://echoarchive.streamlit.app" target="_blank">
    Try Echo Archive Again!
    </a>
    """

    try:

        msg = EmailMessage()

        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = recipient_email

        msg.set_content(
            "Your email client does not support HTML."
        )

        msg.add_alternative(
            html_body,
            subtype="html"
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                GMAIL_USER,
                GMAIL_APP_PASSWORD
            )

            smtp.send_message(msg)

        return True

    except Exception as e:

        st.error(f"Email error: {e}")

        print(f"Email error: {e}")

        return False

# ---------------------------
# UI
# ---------------------------
st.title("Echo Archive")

st.write(
    "Bring your own thoughts "
    "to the archive and discover artworks " 
    "that are "
    "unexpectedly in conversation with your ideas. " 
)

# ---------------------------
# INPUT FORM
# ---------------------------
with st.form("archive_form"):

    user_input = st.text_area(
        "Share a concept that's been on your mind. " \
        " Draw a random artwork from the Art Institute of Chicago." \
        " Reflect on the connections or tensions that emerge.",
        placeholder=(
            "A concept, memory, tension, idea, or feeling..."
        ),
        height=80
    )

    submitted = st.form_submit_button(
        "Discover Artwork"
    )

# ---------------------------
# SUBMISSION
# ---------------------------
if submitted:

    if not user_input.strip():

        st.warning(
            "Please enter a thought first."
        )

        st.stop()

    st.session_state.user_input = (
        user_input
    )

    st.session_state.description = ""
    st.session_state.interpretation = ""
    st.session_state.reflection_text = ""

    with st.spinner(
        "Searching the archive..."
    ):

        artwork = get_random_artwork()

    if artwork is None:

        st.error(
            "The archive returned nothing."
        )

        st.stop()

    st.session_state.artwork = artwork

# ---------------------------
# DISPLAY
# ---------------------------
if st.session_state.artwork:

    art = st.session_state.artwork

    st.image(
        art["image"],
        use_container_width=True
    )

    st.markdown(
        f"### {art['title']}"
    )

    st.caption(
        f"{art['artist']} · {art['date']}"
    )

    st.caption(
        art["medium"]
    )

    # ---------------------------
    # DESCRIPTION
    # ---------------------------
    if not st.session_state.description:

        with st.spinner(
            "Analyzing the artwork..."
        ):

            st.session_state.description = (
                generate_description(art)
            )

    with st.expander(
        "About this work",
        expanded=True
    ):

        st.write(
            st.session_state.description
        )

        if art["provenance"]:

            st.markdown(
                "#### Provenance"
            )

            st.write(
                art["provenance"]
            )

    st.divider()

    # ---------------------------
    # INTERPRET BUTTON
    # ---------------------------
    st.markdown(
        "### Reflect with the Archive"
    )
    interpret = st.button(
        "Connect my Concept to the Artwork"
    )

    if (
        interpret
        and not st.session_state.interpretation
    ):

        with st.spinner(
            "Connecting concepts to the artwork..."
        ):

            st.session_state.interpretation = (
                generate_interpretation(
                    st.session_state.user_input,
                    art,
                    st.session_state.description
                )
            )

    # ---------------------------
    # DISPLAY INTERPRETATION
    # ---------------------------
    if st.session_state.interpretation:

        st.write(
            st.session_state.interpretation
        )
    
    # ---------------------------
    # USER REFLECTION
    # ---------------------------
    reflection_text = st.text_area(
        "Reflect independently here:",
        value=(
            st.session_state.reflection_text
        ),
        height=140,
    )

    st.session_state.reflection_text = (
        reflection_text
    )

    st.divider()

    # ---------------------------
    # EMAIL ARCHIVE
    # ---------------------------
    st.markdown(
        "### Create a personal Archive"
    )
    email_input = st.text_input(
         "Archive this encounter by sending the details to your email.",
    placeholder="email@example.com")
    send = st.button(
        "Send Archive to My Email"
    )

    if send:

        if not valid_email(
            email_input
        ):

            st.warning(
                "Please enter a valid email."
            )

        else:

            with st.spinner(
                "Archiving reflection..."
            ):

                success = send_archive_email(
                    recipient_email=email_input,
                    artwork=art,
                    user_input=(
                        st.session_state.user_input
                    ),
                    description=(
                        st.session_state.description
                    ),
                    interpretation=(
                        st.session_state.interpretation
                    ),
                    reflection=(
                        st.session_state.reflection_text
                    )
                )

            if success:

                st.success(
                    "All details have been sent."
                )

            else:

                st.error(
                    "Unable to send email."
                )