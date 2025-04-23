import pandas as pd
import streamlit as st
from utils.graph import donut_categorie_chart

def format_time(seconds):
            ''' Formattage des temps en heure minute seconde '''
            if pd.isna(seconds):
                return "N/A"
            td = pd.to_timedelta(seconds, unit="s")
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours}:{minutes:02}:{seconds:02}" if hours > 0 else f"{minutes}:{seconds:02}"

def calculate_gender_metrics(data):
    ''' Calcul des métriques en fonction du sexe (nb hommes femmes et temps moyen hommes femmes) '''
    nb_hommes = data[data["categorie"].str.endswith("M", na=False)].shape[0]
    nb_femmes = data[data["categorie"].str.endswith("F", na=False)].shape[0]

    avg_time_hommes = data[data["categorie"].str.endswith("M", na=False)]["duration"].mean()
    avg_time_femmes = data[data["categorie"].str.endswith("F", na=False)]["duration"].mean()

    avg_time_hommes = format_time(avg_time_hommes)
    avg_time_femmes = format_time(avg_time_femmes)

    return {
        "nb_hommes": nb_hommes,
        "nb_femmes": nb_femmes,
        "avg_time_hommes": avg_time_hommes,
        "avg_time_femmes": avg_time_femmes
    }

def display_general_metrics(filtered_data, data):
    ''' Affichage des metrics dans 3 colonnes '''
    if len(filtered_data) > 1:
        gender_metrics = calculate_gender_metrics(filtered_data)
        st.session_state.nb_hommes = gender_metrics["nb_hommes"]
        st.session_state.nb_femmes = gender_metrics["nb_femmes"]
        st.session_state.avg_time_hommes_str = gender_metrics["avg_time_hommes"]
        st.session_state.avg_time_femmes_str = gender_metrics["avg_time_femmes"]
        data_donut = filtered_data
    else:
        data_donut = data

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.image("assets/homme.png", width=100)
        st.metric(label="Nombre d'hommes", value=st.session_state.nb_hommes)
        st.metric(label="Temps moyen hommes", value=st.session_state.avg_time_hommes_str)

    with col2:
        st.image("assets/femme.png", width=100)
        st.metric(label="Nombre de femmes", value=st.session_state.nb_femmes)
        st.metric(label="Temps moyen femmes", value=st.session_state.avg_time_femmes_str)

    with col3:
        fig = donut_categorie_chart(data_donut)
        st.plotly_chart(fig, use_container_width=True)
