import json
import random
import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Huiswerk Overhoor Tool", page_icon="📚")

st.title("📚 Woordjes Overhoren met AI")
st.write(
    "Upload een foto van een woordenlijst en laat je dochter direct oefenen!"
)

# 1. API Sleutel invoeren (gratis op te halen via Google AI Studio)
api_key = st.sidebar.text_input(
    "Google Gemini API Key", type="password", help="Plak hier je gratis API-key"
)

if not api_key:
  st.warning(
      "Vul aan de linkerkant je Google Gemini API-key in om te beginnen. (Je"
      " haalt deze gratis op bij Google AI Studio)."
  )
else:
  client = genai.Client(api_key=api_key)

  # 2. Foto uploaden
  uploaded_file = st.file_uploader(
      "Kies een foto van de woordenlijst", type=["jpg", "jpeg", "png"]
  )

  if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(
        image, caption="Geüploade woordenlijst", use_container_width=True
    )

    if st.button("Start met overhoren!"):
      with st.spinner(
          "Even geduld, de AI leest de woorden van de foto..."
      ):
        prompt = (
            "Lees alle woordparen van deze foto. Zet ze om in een"
            ' JSON-formaat dat een lijst is van objecten met de sleutels "vreemd"'
            ' (de te leren taal) en "nederlands" (de vertaling). Geef ALLEEN'
            " de geldige JSON terug zonder extra tekst."
        )

        try:
          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=[image, prompt]
          )
          # Ruim eventuele markdown code-blocks op uit de output
          clean_text = (
              response.text.replace("```json", "")
              .replace("```", "")
              .strip()
          )
          woordenlijst = json.loads(clean_text)

          # Sla de lijst op in de sessie zodat deze onthouden wordt
          st.session_state["woorden"] = woordenlijst
          random.shuffle(st.session_state["woorden"])
          st.session_state["index"] = 0
          st.session_state["score"] = 0
          st.success(
              f"Helemaal gelukt! Er zijn {len(woordenlijst)} woorden gevonden."
          )
        except Exception as e:
          st.error(
              "Er ging iets mis bij het uitlezen van de foto. Probeer het"
              f" opnieuw. Foutmelding: {e}"
          )

  # 3. Het overhoor-proces
  if "woorden" in st.session_state and len(st.session_state["woorden"]) > 0:
    index = st.session_state["index"]
    woorden = st.session_state["woorden"]

    if index < len(woorden):
      huidig_item = woorden[index]
      st.divider()
      st.subheader(f"Vraag {index + 1} van {len(woorden)}")

      # Vraag het vreemde woord, vraag om de Nederlandse vertaling
      st.markdown(f"### Wat is de vertaling van: **{huidig_item['vreemd']}**?")

      # Formulier voor het antwoord
      with st.form(key=f"antwoord_form_{index}"):
        antwoord = st.text_input("Jouw antwoord:")
        submit = st.form_submit_button("Controleren")

        if submit:
          if (
              antwoord.strip().lower()
              == huidig_item["nederlands"].strip().lower()
          ):
            st.success("Goed zo! Dat is correct! 🎉")
            st.session_state["score"] += 1
          else:
            st.error(
                f"Niet helemaal. Het juiste antwoord is:"
                f" **{huidig_item['nederlands']}**"
            )

          st.session_state["index"] += 1
          st.rerun()
    else:
      st.divider()
      st.success("Klaar met oefenen! 🏆")
      st.write(
          f"Je hebt **{st.session_state['score']}** van de"
          f" **{len(woorden)}** woorden goed beantwoord."
      )
      if st.button("Opnieuw oefenen"):
        random.shuffle(st.session_state["woorden"])
        st.session_state["index"] = 0
        st.session_state["score"] = 0
        st.rerun()