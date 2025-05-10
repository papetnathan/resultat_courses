import streamlit as st
import pandas as pd
import time

# Fonction d'écriture progressive
def stream_message(message):
    ''' Fonction pour afficher un message en simulant une écriture progressive'''
    for char in message:
        yield char
        time.sleep(0.02)

# Fonction de conversion
def time_to_seconds(h, m, s):
    return int(h) * 3600 + int(m) * 60 + int(s)

def display_ranking_calcul(course, distance):
    st.markdown("## 🏆 Estimez votre classement")
    st.markdown(f"Entrez votre temps estimé sur ces **{round(distance/1000, 2)} km**")

    # Formulaire pour aligner parfaitement les champs et le bouton
    with st.form(key="temps_form", clear_on_submit=False):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
        with col1:
            h = st.number_input("Heures", min_value=0, max_value=23, value=0)
        with col2:
            m = st.number_input("Minutes", min_value=0, max_value=59, value=0)
        with col3:
            s = st.number_input("Secondes", min_value=0, max_value=59, value=0)
        with col4:
            submit = st.form_submit_button("🔍 Estimer mon classement")

    # Si bouton cliqué
    if submit:
        user_time_seconds = time_to_seconds(h, m, s)
        if h == 0:
            formatted_time = f"{int(m):02}:{int(s):02}"
        else:
            formatted_time = f"{int(h):02}:{int(m):02}:{int(s):02}"

        def parse_time(t):
            try:
                hh, mm, ss = map(int, t.split(":"))
                return hh * 3600 + mm * 60 + ss
            except:
                return None

        course['time_seconds'] = course['h_duration'].apply(parse_time)
        course = course.dropna(subset=['time_seconds'])
        course['classement'] = course['time_seconds'].rank(method='min').astype(int)

        if user_time_seconds > course['time_seconds'].max():
            user_ranking = len(course)
            percentage = 100.0
        else:
            user_ranking = course[course['time_seconds'] <= user_time_seconds].shape[0] + 1
            percentage = (user_ranking / len(course)) * 100

        percentage = (user_ranking / len(course)) * 100
        pace_sec_per_km = user_time_seconds / (distance / 1000)
        pace_min = int(pace_sec_per_km // 60)
        pace_sec = int(pace_sec_per_km % 60)
        formatted_pace = f"{pace_min}:{pace_sec:02d}/km"

        if distance > 4500 and pace_sec_per_km < 120:
            st.warning("On a dit à pieds, pas en vélo ! 🚴")
        elif pace_sec_per_km > 1200:
            st.warning("Vous vous êtes sûrement trompé(e) dans le temps saisi... 😅")
        else:
            with st.chat_message("assistant"):
                st.write_stream(stream_message(
                    f"Avec un temps de **{formatted_time}** (soit une allure de {formatted_pace}), "
                    f"vous seriez classé **{user_ranking}ᵉ** sur cette course de {round(distance/1000, 2)} km.  \n"
                    f"Vous seriez dans le top **{round(percentage, 2)}%** des coureurs sur cette course. 🏅"
                ))