import requests

url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m,relative_humidity_2m,rain,snowfall,cloud_cover,pressure_msl,wind_speed_10m,weather_code&timezone=Europe%2FBerlin"
forecast = requests.get(url)
forecast.raise_for_status()
data = forecast.json()