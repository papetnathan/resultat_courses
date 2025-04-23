import time
import streamlit as st
from utils.data_loader import update_courses_data


def stream_message(message):
    ''' Fonction pour afficher un message en simulant une écriture progressive'''
    for char in message:
        yield char
        time.sleep(0.02)

def display_chat():
    ''' Affichage d’un message d’accueil dynamique selon si les données sont à jour ou non '''
    message_loading = "Salut 👋 ! Bienvenue sur mon application d'analyse de résultats de courses à pied !  \nLaisse-moi juste un instant pour vérifier les dernières courses..."
    message_updated = "C'est bon, j'ai chargé les toutes dernières courses 🏃‍♂️💨 ! Tu peux maintenant sélectionner celle que tu veux pour voir les résultats de manière visuelle et interactive !"
    message_up_to_date = "Bonne nouvelle, les données sont déjà à jour ! Sélectionne une course pour voir les résultats de manière visuelle et interactive."

    if "message_displayed" not in st.session_state:
        with st.chat_message("user"):
            st.write_stream(stream_message(message_loading))
        _, updated = update_courses_data()
        st.session_state["data_updated"] = updated

        with st.chat_message("user"):
            if updated:
                st.write_stream(stream_message(message_updated))
            else:
                st.write_stream(stream_message(message_up_to_date))
        st.session_state["message_displayed"] = True
    else:
        updated = st.session_state.get("data_updated", False)
        if "url" not in st.session_state or not st.session_state.url:
            with st.chat_message("user"):
                st.write(message_loading)
            with st.chat_message("user"):
                st.write(message_updated if updated else message_up_to_date)
