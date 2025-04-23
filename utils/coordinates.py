import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

def find_best_match(lieu, coord_communes, dept_code, threshold=80):
    '''Utilisation de fuzzy match pour retrouver le nom de la commune correspondante dans le fichier de coordonnees'''
    # Filtrer les communes du même département
    communes_dept = coord_communes[coord_communes["code_departement"] == dept_code].copy()
    
    # Calculer la distance de Levenshtein pour chaque commune dans le département
    communes_dept['similarity'] = communes_dept["nom_commune_postal"].apply(
        lambda x: fuzz.ratio(lieu, x)
    )
    
    # Trouver la meilleure correspondance qui dépasse le seuil
    best_match = communes_dept[communes_dept['similarity'] >= threshold]
    
    if not best_match.empty:
        # Trouver la commune avec la plus grande similarité
        best_match_row = best_match.loc[best_match['similarity'].idxmax()]
        return best_match_row
    else:
        return None

def get_coordinates(metadata):
    '''Fonction pour récupérer les coordonnées des communes, renvoie la long et la lat'''
    coord_communes = pd.read_csv("assets/coord_communes.csv")
    # Recherche exacte
    coord_course = coord_communes[
        (coord_communes["code_departement"] == metadata["dept"]) & 
        (coord_communes["nom_commune_postal"] == metadata["lieu"])
    ]
    
    if coord_course.empty:
        # Recherche partielle si aucune correspondance exacte
        coord_course = coord_communes[
            (coord_communes["code_departement"] == metadata["dept"]) & 
            (coord_communes["nom_commune_postal"].str.contains(metadata["lieu"], case=False, na=False))
        ]
    
    if coord_course.empty:
        # Recherche par distance de Levenshtein
        best_match = find_best_match(metadata["lieu"], coord_communes, metadata["dept"], threshold=80)
        
        if best_match is not None:
            # Construire un DataFrame au format attendu
            coord_course = pd.DataFrame({'lat': [best_match["latitude"]], 'lon': [best_match["longitude"]]})
        else:
            return None

    # Renommer les colonnes pour uniformiser la sortie
    coord_course = coord_course.rename(columns={'latitude': 'lat', 'longitude': 'lon'})

    # Sélectionner uniquement les colonnes utiles
    return coord_course[['lat', 'lon']]