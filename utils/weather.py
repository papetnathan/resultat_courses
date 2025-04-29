import requests
import datetime

def get_weather_data(lat, lon, date, heure):
    ''' Récupère les données météorologiques historiques pour une latitude, une longitude et une date données '''

    try:
        if "/" in date:
            event_date = datetime.datetime.strptime(date, "%d/%m/%y").strftime("%Y-%m-%d")
        else:
            event_date = date
    except ValueError:
        return None

    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": event_date,
        "end_date": event_date,
        "hourly": "temperature_2m,weathercode,windspeed_10m,relativehumidity_2m",
        "timezone": "Europe/Paris"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "hourly" in data and "temperature_2m" in data["hourly"] and "weathercode" in data["hourly"] and "windspeed_10m" in data["hourly"]:
            # Récupération des données météorologiques à 10h (heure la plus fréquente de course)
            temperature = data["hourly"]["temperature_2m"][int(heure)]  
            weather_code = data["hourly"]["weathercode"][int(heure)]
            wind_speed = data["hourly"]["windspeed_10m"][int(heure)]
            humidity = data["hourly"]["relativehumidity_2m"][int(heure)]
            description = map_weather_code(weather_code)
            return {"temperature": temperature, "description": description, "wind_speed": wind_speed, "humidity": humidity}
        else:
            return None
    
    return None

def map_weather_code(code):
    ''' Convertit le code météo en une description lisible '''
    weather_mapping = {
        0: "Ciel clair",
        1: "Principalement dégagé",
        2: "Partiellement nuageux",
        3: "Couvert",
        45: "Brouillard",
        48: "Brouillard givrant",
        51: "Bruine légère",
        53: "Bruine modérée",
        55: "Bruine dense",
        61: "Pluie faible",
        63: "Pluie modérée",
        65: "Pluie forte",
        71: "Neige faible",
        73: "Neige modérée",
        75: "Neige forte",
        80: "Averses faibles",
        81: "Averses modérées",
        82: "Averses fortes",
    }
    return weather_mapping.get(code, "Météo inconnue")
