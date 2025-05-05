import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, date
from tqdm import tqdm

def initialize_session_state():
    ''' Fonction pour initialiser les différents st.session.state '''
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'metadata' not in st.session_state:
        st.session_state.metadata = None
    if 'url' not in st.session_state:
        st.session_state.url = ""
    if 'epreuve_selectionnee' not in st.session_state:
        st.session_state.epreuve_selectionnee = ""
    if 'expander_open' not in st.session_state:
        st.session_state.expander_open = True
    if 'data_updated' not in st.session_state:
        st.session_state.data_updated = None

def load_data_from_url(url):
    """Fonction pour récupérer les données de l'URL spécifiée."""
    try:
        request_text = requests.get(url).text
        page = BeautifulSoup(request_text, "lxml")

        pagination_select = None
        for select in page.find_all("select", {"class": "barSelect"}):
            if any("Page" in option.text for option in select.find_all("option")):
                pagination_select = select
                break
        
        if pagination_select:
            options = [option for option in pagination_select.find_all("option") if "Page" in option.text]
            nb_pages = len(options)
        else:
            nb_pages = 1

        rows = []
        for i in range(nb_pages):
            url_i = f"{url}&frmposition={i}"
            request_text = requests.get(url_i).text
            page = BeautifulSoup(request_text, "lxml")

            for row in page.find_all('tr'):
                if all(keyword not in str(row) for keyword in ["groups", "mainheaders", "barButtons", "subheaderscom"]):
                    rows.append(row)

        return page, rows

    except Exception as e:
        return None, str(e)

def extract_metadata(page):
    """Extraction des métadonnées de la page (nom, date, lieu, etc.)."""
    try:
        header = page.find('div', {'class': "mainheaders"})
        header_str = str(header)
        
        nom = re.search("(?<=\- )(.*?)(?=\<)", header_str)
        nom = nom.group(0) if nom else "Non trouvé"
        
        date = re.search("[0-9]{2}/[0-9]{2}/[0-9]{2}", header_str)
        date = date.group(0) if date else "Non trouvée"
        
        lieu = re.search("(?<=\>)(\D*?)(?=\ -)", header_str)
        lieu = lieu.group(0) if lieu else "Non trouvé"
        lieu = re.sub(r"[^A-ZÀ-Ÿ0-9]", " ", lieu.upper())
        
        sous_titre = header.text if header else ""
        dept = re.search("[0-9]{3}", sous_titre)
        dept = dept.group(0).lstrip('0') if dept else "Non trouvé"
        
        label = re.search("(?<=Label ).*(?<!')", sous_titre)
        label = label.group(0) if label else "Aucun"

        subheader = page.find('div', {'class': "subheaders"})
        subheader_text = subheader.text if subheader else ""
        heure = re.search(r"\d{1,2}:\d{2}", subheader_text)
        heure = heure.group(0).split(":")[0] if heure else "10"
        
        return {"nom": nom, "date": date, "lieu": lieu, "label": label, "dept": dept, "heure": heure}
    
    except Exception as e:
        return str(e)

def load_recent_data():
    ''' Chargement de données plus fraiches '''
    courses_url = pd.read_csv("assets/courses_url.csv")
    url_ligue = 'https://bases.athle.fr/asp.net/liste.aspx?frmpostback=true&frmbase=resultats&frmmode=2&frmespace=0&frmsaison={}&frmtype1=Hors+Stade&frmtype2=&frmtype3=&frmtype4=&frmniveau=&frmniveaulab=&frmligue={}&frmdepartement=&frmeprrch=&frmclub=&frmdate_j1={}&frmdate_m1={}&frmdate_a1={}&frmdate_j2={}&frmdate_m2={}&frmdate_a2={}'

    ligues = ['ARA', 'BFC', 'BRE', 'CEN', 'COR', 'G-E', 'GUA', 'GUY', 'H-F', 'I-F', 'MAR', 'MAY', 'N-A', 'N-C', 'NOR', 'OCC', 'PCA', 'P-F', 'P-L', 'REU', 'W-F']
    today_annee = date.today().year
    today_month = date.today().month
    today_day = date.today().day

    courses_url['Date'] = courses_url['Date'].astype(str).str[-10:]
    courses_url['Date'] = pd.to_datetime(courses_url['Date'], format="%d/%m/%Y", errors='coerce')

    # Récupération de la date la plus récente
    date_course = courses_url['Date'].max()
    last_day = str(date_course.day).zfill(2)
    last_month = str(date_course.month).zfill(2)
    last_annee = date_course.year

    if last_annee == today_annee :
        annees = [last_annee]
    else :
        annees = [last_annee,today_annee]

    data = []

    total_steps = len(annees) * len(ligues)
    progress_bar = st.progress(0)
    step = 0

    for annee in annees:
        for ligue in tqdm(ligues, desc=f"Ligue {annee}", leave=False):
            step += 1
            progress_bar.progress(step / total_steps)
            
            url = url_ligue.format(annee, ligue,last_day,last_month,last_annee,today_day,today_month,today_annee)

            response = requests.get(url)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            pagination_select = None
            for select in soup.find_all("select", {"class": "barSelect"}):
                if any("Page" in option.text for option in select.find_all("option")):
                    pagination_select = select
                    break

            if pagination_select:
                options = [option for option in pagination_select.find_all("option") if "Page" in option.text]
                nb_pages = len(options)
            else:
                nb_pages = 1

            for i in range(nb_pages):
                url_i = f"{url}&frmposition={i}"

                response = requests.get(url_i)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                table = soup.find("table", id="ctnResultats")
                if not table:
                    continue

                rows = table.find_all("tr")[2:]  # Ignorer les deux premières lignes (titres)

                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 15:  # Vérification pour éviter les lignes incomplètes
                        continue

                    date_course_str = f"{cols[4].text.strip()}/{annee}"
                    date_course_str = date_course_str[-10:]
                    nom_course = cols[8].text.strip()
                    departement = cols[14].text.strip()

                    course_link = cols[8].find("a")
                    course_url = "https://bases.athle.fr" + course_link["href"] if course_link else ""

                    data.append([nom_course, date_course_str, ligue, departement, course_url, annee])

    df_new = pd.DataFrame(data, columns=["Nom de la course","Date", "Ligue", "Département", "URL", "Année"])
    df_new = df_new[~df_new['Nom de la course'].str.contains('Libellé', na=False)]
    progress_bar.empty()
    return df_new


def update_courses_data():
    ''' Chargement des données plus fraîches et mise à jour du fichier contenant les URL des courses '''
    existing_df = pd.read_csv("assets/courses_url.csv")

    existing_df['Date'] = pd.to_datetime(existing_df['Date'], format="%d/%m/%Y", errors='coerce')
    last_update = pd.to_datetime(existing_df["last_update"].iloc[0]).date()

    if last_update == date.today():
        return existing_df, False

    new_df = load_recent_data()

    if new_df is None or new_df.empty:
        existing_df["last_update"] = date.today()
        existing_df.to_csv("assets/courses_url.csv", index=False)
        return existing_df, False

    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["URL"])
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], format="%d/%m/%Y", errors='coerce')
    combined_df['Date'] = combined_df['Date'].dt.strftime('%d/%m/%Y')
    combined_df["last_update"] = date.today()
    combined_df.to_csv("assets/courses_url.csv", index=False)

    return combined_df, True
