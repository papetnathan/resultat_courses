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

    avg_pace_hommes = data[data["categorie"].str.endswith("M", na=False)]["allure_decimal"].mean()
    avg_pace_femmes = data[data["categorie"].str.endswith("F", na=False)]["allure_decimal"].mean()
    pace_hommes_str = f"{int(avg_pace_hommes)}:{int((avg_pace_hommes % 1) * 60):02d}/km"
    pace_femmes_str = f"{int(avg_pace_femmes)}:{int((avg_pace_femmes % 1) * 60):02d}/km"

    return {
        "nb_hommes": nb_hommes,
        "nb_femmes": nb_femmes,
        "avg_time_hommes": avg_time_hommes,
        "avg_time_femmes": avg_time_femmes,
        "pace_hommes_str": pace_hommes_str,
        "pace_femmes_str": pace_femmes_str
    }

def display_general_metrics(filtered_data, data):
    ''' Affichage des metrics dans 3 colonnes '''
    if len(filtered_data) > 1:
        gender_metrics = calculate_gender_metrics(filtered_data)
        st.session_state.nb_hommes = gender_metrics["nb_hommes"]
        st.session_state.nb_femmes = gender_metrics["nb_femmes"]
        st.session_state.avg_time_hommes_str = gender_metrics["avg_time_hommes"]
        st.session_state.avg_time_femmes_str = gender_metrics["avg_time_femmes"]
        st.session_state.pace_hommes_str = gender_metrics["pace_hommes_str"]
        st.session_state.pace_femmes_str = gender_metrics["pace_femmes_str"]
        data_donut = filtered_data
    else:
        data_donut = data

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.image("assets/homme.png", width=80)
        st.metric(label="Nombre d'hommes", value=st.session_state.nb_hommes)
        st.markdown(
            """
            <div style=" font-size: 14px; margin-bottom: 4px;">
                Temps moyen hommes
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="font-size: 24px; font-weight: bold;">
                {st.session_state.avg_time_hommes_str}
                <span style="font-size: 16px; color: gray;">({st.session_state.pace_hommes_str})</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.image("assets/femme.png", width=80)
        st.metric(label="Nombre de femmes", value=st.session_state.nb_femmes)
        st.markdown(
            """
            <div style=" font-size: 14px; margin-bottom: 4px;">
                Temps moyen femmes
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="font-size: 24px; font-weight: bold;">
                {st.session_state.avg_time_femmes_str}
                <span style="font-size: 16px; color: gray;">({st.session_state.pace_femmes_str})</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        fig = donut_categorie_chart(data_donut)
        st.plotly_chart(fig, use_container_width=True)
