import streamlit as st
import pandas as pd
from utils.data_loader import load_data_from_url, extract_metadata, update_courses_data, initialize_session_state
from utils.data_processing import process_athlete_data, nettoyer_nom_course
from utils.metrics import display_general_metrics
from utils.graph import plot_time_distribution
from streamlit_lottie import st_lottie
from utils.lottie_loader import load_lottiefile
import time
from utils.chat import display_chat
from utils.sidebar import display_sidebar
from utils.ranking_calcul import display_ranking_calcul

st.set_page_config(layout="wide")

lottie_loading = load_lottiefile("assets/chargement.json")
initialize_session_state()
display_chat()

courses_df = pd.read_csv("assets/courses_url.csv")
courses_df['Nom de la course'] = courses_df['Nom de la course'].apply(nettoyer_nom_course)

with st.expander("🔗 Sélectionnez votre course", expanded=st.session_state.expander_open):
    selected_departement = st.selectbox(
        "Département",
        options=[""] + sorted(courses_df['Département'].dropna().unique().astype(int))
    )

    if selected_departement:
        filtered_courses = courses_df[courses_df['Département'] == selected_departement]
        selected_course = st.selectbox("Nom de la course", options=[""] + sorted(filtered_courses['Nom de la course'].unique()))

        if selected_course:
            filtered_courses = filtered_courses[filtered_courses['Nom de la course'] == selected_course]
            available_years = sorted(filtered_courses['Année'].unique())
            selected_year = st.selectbox("Année", options=available_years)

            filtered_courses = filtered_courses[filtered_courses['Année'] == selected_year]

            if not filtered_courses.empty:
                url = filtered_courses.iloc[0]['URL']
                if st.button("Valider"):
                    st.session_state.url = url
                    st.session_state.expander_open = False
                    st.session_state["message_displayed"] = True
                    st.rerun()

loading_container = st.empty()

if st.session_state.url:
    with loading_container:
        st_lottie(lottie_loading, speed=1, height=300, key="loading")

    time.sleep(1)

    page, rows = load_data_from_url(st.session_state.url)
    
    if page is None:
        loading_container.empty()
        st.error(f"Erreur lors de la récupération des données: {rows}")
    else:
        st.session_state.metadata = extract_metadata(page)
        st.session_state.data = process_athlete_data(rows)

    loading_container.empty()

if st.session_state.metadata and st.session_state.data is not None:
    metadata = st.session_state.metadata
    data = st.session_state.data.copy()

    filtered_data, filtered_data_course, data_epreuve, coord_course = display_sidebar(metadata, data)

    st.markdown(f"<h1 style='text-align: center; color: gray;'>{metadata['nom']}</h1>", unsafe_allow_html=True)

    if coord_course is not None:
        st.map(coord_course, use_container_width=True, height=200)

    display_general_metrics(data_epreuve)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📋 Résultats détaillés")
    data_to_display = filtered_data[['nom_athlete', 'categorie', 'club', 'h_duration','allure']]
    data_to_display.columns = ['Nom Prénom', 'Catégorie', 'Club', 'Temps','Allure']
    st.dataframe(data_to_display, use_container_width=True)

    if filtered_data.empty:
        st.warning("❌ Aucun athlète ne correspond aux filtres sélectionnés.")
        fig = None
    elif len(filtered_data['duration']) > 1:
        fig = plot_time_distribution(filtered_data['duration'])
    else:
        athlete_time = filtered_data['duration'].iloc[0]
        fig = plot_time_distribution(filtered_data_course['duration'], athlete_time)

    if fig:
        st.plotly_chart(fig, use_container_width=True)

    display_ranking_calcul(filtered_data,filtered_data['distance_m'].iloc[0])
