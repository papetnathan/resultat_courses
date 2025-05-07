import streamlit as st
from utils.weather import get_weather_data
from utils.coordinates import get_coordinates
from utils.data_processing import apply_filters


def display_sidebar(metadata, data):
    ''' Fonction permettant la création de la sidebaret son affichage '''
    # Coordonnées et météo
    coord_course = get_coordinates(metadata)
    if coord_course is not None:
        lat, lon = coord_course.iloc[0]['lat'], coord_course.iloc[0]['lon']
        weather_info = get_weather_data(lat, lon, metadata['date'], metadata['heure'])
    else:
        weather_info = None

    with st.sidebar:
        # Affichage météo et métadonnées
        if weather_info:
            infos_html = f"""
            <div style="background-color: var(--primary-background); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); color: var(--primary-text);">
                <div style="border-bottom: 1px solid #ccc; padding-bottom: 15px; margin-bottom: 15px;">
                    <p style="font-size: 16px; font-weight: 600;"><strong>📅 Date:</strong> {metadata['date']}</p>
                    <p style="font-size: 16px; font-weight: 600;"><strong>🏷️ Label:</strong> {metadata['label']}</p>
                </div>
                <div>
                    <p style="font-size: 16px;"><strong>🌤️ Météo:</strong> {weather_info['description']}</p>
                    <p style="font-size: 16px;"><strong>🌡️ Température:</strong> {weather_info['temperature']}°C</p>
                    <p style="font-size: 16px;"><strong>💨 Vent:</strong> {weather_info['wind_speed']} km/h</p>
                    <p style="font-size: 16px;"><strong>💧 Humidité:</strong> {weather_info['humidity']} %</p>
                </div>
            </div>
            """
        else:
            infos_html = f"""
            <div style="background-color: var(--primary-background); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); color: var(--primary-text);">
                <div style="border-bottom: 1px solid #ccc; padding-bottom: 15px; margin-bottom: 15px;">
                    <p style="font-size: 16px; font-weight: 600;"><strong>📅 Date:</strong> {metadata['date']}</p>
                    <p style="font-size: 16px; font-weight: 600;"><strong>🏷️ Label:</strong> {metadata['label']}</p>
                </div>
            </div>
            """
        st.markdown(infos_html, unsafe_allow_html=True)

        # Filtres
        st.logo("assets/logo_ffa.png", icon_image="assets/logo_ffa.png", size="large")
        st.header("📌 Filtres")

        epreuves_counts = data['epreuve'].value_counts().sort_values(ascending=False)
        epreuves_uniques = epreuves_counts.index.tolist()

        if len(epreuves_uniques) > 1:
            epreuve_selectionnee = st.radio("Choisir l'épreuve", options=epreuves_uniques, index=0)
        else:
            epreuve_selectionnee = epreuves_uniques[0]

        st.session_state.epreuve_selectionnee = epreuve_selectionnee
        data_epreuve = data[data['epreuve'] == epreuve_selectionnee]
        sexe_filter = st.multiselect("Filtrer par sexe :", options=sorted(data_epreuve['sexe'].dropna().unique()), default=[])
        categorie_filter = st.multiselect("Filtrer par catégorie", options=sorted(data_epreuve['cat'].dropna().unique()), default=[])
        club_filter = st.multiselect("Filtrer par club", options=sorted(data_epreuve['club'].dropna().unique()), default=[])
        noms_uniques = sorted(data_epreuve["nom_athlete"].dropna().unique())
        search_name = st.selectbox("Rechercher un athlète", options=[""] + noms_uniques)

    filtered_data = apply_filters(data_epreuve, search_name, club_filter, categorie_filter, sexe_filter)
    filtered_data_course = apply_filters(data_epreuve, None, club_filter, categorie_filter, sexe_filter)

    return filtered_data, filtered_data_course, data_epreuve, coord_course
