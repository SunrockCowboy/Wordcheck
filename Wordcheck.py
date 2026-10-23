import json
import random
import time
from google import genai
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Huiswerk Overhoor Tool", page_icon="📚")

st.title("📚 Woordjes Overhoren met AI")
st.write(
    "Upload een foto van een woordenlijst en laat je dochter direct oefenen!"
)

# 1. API-sleutel invoeren via de zijbalk
api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    type="password",
    help="Plak hier je gratis API-key van https://aistudio.google.com/",
)

if not api_key:
  st.warning(
      "Vul aan de linkerkant je Google Gemini API-key in om te beginnen."
  )
  st.stop()

try:
  client = genai.Client(api_key=api_key)
except Exception as e:
  st.error(f"Fout bij het maken van verbinding: {e}")
  st.stop()

# 2. Foto uploaden
uploaded_file = st.file_uploader(
    "Kies een foto van de woordenlijst", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  image = Image.open(uploaded_file)
  st.image(image, caption="Geüploade woordenlijst", use_container_width=True)

  if st.button("Start met overhoren!"):
    with st.spinner("Even geduld, de AI leest de woorden van de foto..."):
      prompt = (
          "Lees alle woordparen van deze foto. Zet ze om in een JSON-formaat"
          ' dat een lijst is van objecten met de sleutels "vreemd" (de te'
          ' leren taal) en "nederlands" (de vertaling). Geef ALLEEN de geldige'
          " JSON terug zonder extra tekst."
      )

      max_pogingen = 3
      gelukt = False
      response = None

      for poging in range(max_pogingen):
        try:
          response = client.models.generate_content(
              model="gemini-3.8-flash", contents=[image, prompt]
          )
          gelukt = True
          break
        except Exception as e:
          if poging < max_pogingen - 1:
            time.sleep(2)
          else:
            st.error(f"Er ging iets mis bij het uitlezen: {e}")

      if gelukt and response:
        try:
          clean_text = (
              response.text.replace("```json", "").replace("```", "").strip()
          )
          woordenlijst = json.loads(clean_text)

          st.session_state["woorden"] = woordenlijst
          random.shuffle(st.session_state["woorden"])
          st.session_state["index"] = 0
          st.session_state["score"] = 0
          st.session_state["gecontroleerd"] = False
          st.success(
              f"Helemaal gelukt! Er zijn {len(woordenlijst)} woorden gevonden."
          )
        except Exception:
          st.error(
              "De AI kon de tekst niet goed omzetten. Probeer een scherpere"
              " foto."
          )

# 3. Het directe overhoor-proces
if "woorden" in st.session_state and len(st.session_state["woorden"]) > 0:
  index = st.session_state["index"]
  woorden = st.session_state["woorden"]

  if index < len(woorden):
    huidig_item = woorden[index]
    st.divider()
    st.subheader(f"Vraag {index + 1} van {len(woorden)}")

    st.markdown(f"### Wat is de vertaling van: **{huidig_item['vreemd']}**?")

    # Los invoerveld reageert direct op Enter
    antwoord = st.text_input("Jouw antwoord (druk op Enter):", key=f"input_{index}")

    if antwoord:
      juiste_antwoord = huidig_item["nederlands"].strip().lower()
      gegeven_antwoord = antwoord.strip().lower()

      # Directe feedback geven
      if gegeven_antwoord == juiste_antwoord:
        st.success("Goed zo! Dat is helemaal correct! 🎉")
      else:
        st.error(
            f"Niet helemaal. Het juiste antwoord is:"
            f" **{huidig_item['nederlands']}**"
        )

      # Knop om door te gaan naar de volgende vraag
      if st.button("Volgend woord ➡️"):
        if gegeven_antwoord == juiste_antwoord:
          st.session_state["score"] += 1
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
