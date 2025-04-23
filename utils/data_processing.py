import pandas as pd
import re
from urllib.parse import unquote

def filter_rows_by_distance(rows, selected_distance):
    """Filtre les résultats en fonction de la distance sélectionnée."""
    filtered = []
    current_distance = None
    for row in rows:
        if "subheaders" in str(row):
            current_distance = row.text.strip()
        if current_distance == selected_distance:
            filtered.append(row)
    return filtered

def define_categories():
    '''Création des bons libellés de catégorie en fonction du sexe'''
    cat = {
        'M10': 'Masters 10', 'M9': 'Masters 9', 'M8': 'Masters 8', 'M7': 'Masters 7', 'M6': 'Masters 6',
        'M5': 'Masters 5', 'M4': 'Masters 4', 'M3': 'Masters 3', 'M2': 'Masters 2', 'M1': 'Masters 1', 'M0': 'Masters 0',
        'SE': 'Seniors', 'ES': 'Espoirs', 'JU': 'Juniors', 'CA': 'Cadet.te.s', 'MI': 'Minimes',
        'BE': 'Benjamin.e.s', 'PO': 'Poussins', 'EA': "École d'Athlétisme", 'BB': 'Baby Athlé'
    }
    categoriesF = [c + 'F' for c in cat.keys()]
    categoriesM = [c + 'M' for c in cat.keys()]
    return categoriesF + categoriesM

def extract_athletes_data(rows):
    ''' Extraction des données de l'athlete'''
    categories = define_categories()
    re_cat = re.compile(r"[A-Z]{3}(?=<)|[A-Z]\d[A-Z]")
    athletes_results = []
    
    for row in rows:
        columns = row.find_all('td')
        
        if len(columns) > 5:
            nom_athlete = columns[4].text.strip() if len(columns) > 4 else ''
            temps = columns[2].text.strip().split(" ")[0] if len(columns) > 2 else ''
            matches = re_cat.findall(str(row))
            valid_matches = [match for match in matches if match in categories]
            categorie = valid_matches[0] if valid_matches else None
            club = columns[6].text.strip() if len(columns) > 6 else ''
            
            # Extraction de l'épreuve depuis l'URL dans le href
            epreuve = None
            epreuve_link = row.find('a', href=re.compile(r"frmepreuve="))
            if epreuve_link and 'href' in epreuve_link.attrs:
                # Extraction du paramètre frmepreuve de l'URL
                href = epreuve_link.attrs['href']
                epreuve_match = re.search(r"frmepreuve=([^&]+)", href)
                if epreuve_match:
                    epreuve = unquote(epreuve_match.group(1))  # Décoder l'URL et extraire l'épreuve
                
            athletes_results.append({
                'nom_athlete': nom_athlete,
                'temps': temps,
                'categorie': categorie,
                'club': club,
                'epreuve': epreuve  # Ajout de l'épreuve dans les résultats
            })
    
    return pd.DataFrame(athletes_results)


def convert_chrono(x):
    '''Formattage du temps de course'''
    x = str(x)
    if len(x) == 5:
        return pd.to_datetime('00:' + x, format='%H:%M:%S', errors='coerce')
    elif len(x) in [7, 8]:
        return pd.to_datetime(x, format='%H:%M:%S', errors='coerce')
    elif len(x) == 2:
        return pd.to_datetime(x, format='%S', errors='coerce')
    return None

def split_nom_prenom(athlete):
    '''Fonction pour separer le nom et le prenom de l'athlete'''
    words = athlete.split()
    nom = ' '.join([word for word in words if word.isupper()])
    prenom = ' '.join([word for word in words if not word.isupper()]).split('(')[0].strip()
    return nom, prenom

def process_athlete_data(rows):
    '''Data prep sur le dataframe des resultats'''
    data = extract_athletes_data(rows)
    
    data['temps'] = data['temps'].str.replace('h', ':', regex=False).str.replace("'", ':', regex=False).str.replace("::", '', regex=False)
    data['temps'] = data['temps'].apply(convert_chrono)
    data[['Nom', 'Prénom']] = data['nom_athlete'].apply(lambda x: pd.Series(split_nom_prenom(x)))
    data['time_delta'] = data['temps'] - pd.to_datetime("1900-01-01", format="%Y-%m-%d")
    data = data.sort_values(['epreuve', 'time_delta']).reset_index(drop=True)
    data['classement'] = data.groupby('epreuve').cumcount() + 1
    data['time_gap'] = (data["temps"] - data['temps'].iloc[0]).dt.total_seconds()
    data['duration'] = data['time_delta'].dt.total_seconds()
    data['h_duration'] = data['duration'].apply(lambda x: str(pd.to_timedelta(x, unit="s")).split(' ')[-1] if pd.notna(x) else None)
    data['club'] = data['club'].str.upper()
    data['cat'] = data["categorie"].str.slice(0,2)
    data = data.set_index('classement')
    return data.drop(columns=["temps", "time_delta"], errors='ignore')

def apply_filters(data, search_name="", club_filter=None, categorie_filter=None):
    ''' Fonction pour filtrer le dataframe sur les filtres selectionnés'''
    filtered_data = data.copy()
    if search_name:
        filtered_data = filtered_data[
            filtered_data['nom_athlete'].str.contains(search_name, case=False, na=False)
        ]
    
    if club_filter:
        if isinstance(club_filter, list) and len(club_filter) > 0:
            filtered_data = filtered_data[filtered_data['club'].isin(club_filter)]

    if categorie_filter:
        if isinstance(categorie_filter, list) and len(categorie_filter) > 0:
            filtered_data = filtered_data[filtered_data['categorie'].isin(categorie_filter)]

    return filtered_data


def nettoyer_nom_course(nom_course):
    ''' Fonction pour uniformiser les noms de course '''
    nom_course = nom_course.strip('"').strip()
    # Liste des motifs à supprimer (incluant toutes les combinaisons)
    motifs_a_supprimer = [
        r"\b\d+\s?(?:ieres|iere|ières|ière|iemes|ieme|ièmes|ième|èmes|ème|emes|eme|émes|éme|mes|me|ères|ère|eres|ere|ers|er|é|e|°)\s?(?:édition|edition)?\s?(?:-)?\s?(?:des)?\b",
        r"\b\d+\s?(?:édition|edition)\s?(?:des)?\b"
    ]

    # Supprimer chaque motif
    for motif in motifs_a_supprimer:
        nom_course = re.sub(motif, "", nom_course)
    
    # Supprimer les années de 2017 à 2030
    nom_course = re.sub(r"\b(20[1-9]\d|2030)\b", "", nom_course)
    
    # Uniformiser la distance : ajouter un espace avant "km" si nécessaire
    nom_course = re.sub(r"(\d+)\s?km\b", r"\1 km", nom_course, flags=re.IGNORECASE)

    # Supprimer les espaces inutiles qui pourraient apparaître après la suppression
    nom_course = re.sub(r"\s+", " ", nom_course).strip()

    # Supprimer les tirets en début ou en fin de chaîne
    nom_course = nom_course.strip('-').strip()

    nom_course = nom_course.capitalize()
    
    return nom_course

