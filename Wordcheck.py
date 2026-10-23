import json
import random
from google import genai
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Huiswerk Overhoor Tool", page_icon="📚")

st.title("📚 Woordjes Overhoren met AI")
st.write(
    "Upload een foto van een woordenlijst en laat je dochter direct oefenen!"
)

# Verbinding maken via de veilige Streamlit Secrets
try:
  client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
  st.error(
      "API-key is niet gevonden in de Streamlit Secrets. Stel deze eerst in!"
  )
  st.stop()

# Foto uploaden
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

      try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=[image, prompt]
        )
        clean_text = (
            response.text.replace("```json", "").replace("```", "").strip()
        )
        woordenlijst = json.loads(clean_text)

        st.session_state["woorden"] = woordenlijst
        random.shuffle(st.session_state["woorden"])
        st.session_state["index"] = 0
        st.session_state["score"] = 0
        st.success(
            f"Helemaal gelukt! Er zijn {len(woordenlijst)} woorden gevonden."
        )
      except Exception as e:
        st.error(
            "Er ging iets mis bij het uitlezen van de foto. Probeer het opnieuw."
            f" Foutmelding: {e}"
        )

# Het overhoor-proces
if "woorden" in st.session_state and len(st.session_state["woorden"]) > 0:
  index = st.session_state["index"]
  woorden = st.session_state["woorden"]

  if index < len(woorden):
    huidig_item = woorden[index]
    st.divider()
    st.subheader(f"Vraag {index + 1} van {len(woorden)}")

    st.markdown(f"### Wat is de vertaling van: **{huidig_item['vreemd']}**?")

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
