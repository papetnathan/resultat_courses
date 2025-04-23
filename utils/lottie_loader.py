import json
import time
import streamlit as st
from streamlit_lottie import st_lottie

def load_lottiefile(filepath: str):
    ''' Charge un fichier Lottie et retourne son contenu JSON '''
    with open(filepath, "r") as f:
        return json.load(f)