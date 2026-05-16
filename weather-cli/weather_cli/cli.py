import sys, webbrowser, requests, json, datetime

OPEN_WEATHER_URL = 'http://api.openweathermap.org'

def overview(info):
    # core fields
    city = info.get('name', '?')
    cc = info.get('sys', {}).get('country', '')
    desc = info['weather'][0]['description'].title()
    lat = info['coord']['lat']
    lon = info['coord']['lon']

    main = info['main']
    t_c = main['temp'] - 273.15
    fl_c = main['feels_like'] - 273.15
    hum = main['humidity']
    pres = main['pressure']

    wind = info.get('wind', {})
    wspd = wind.get('speed', 0)
    wdeg = wind.get('deg', 0)
    gust = wind.get('gust')

    clouds = info.get('clouds', {}).get('all')
    vis_km = info.get('visibility', 0) / 1000
    rain_1h = info.get('rain', {}).get('1h')

    tz = datetime.timezone(datetime.timedelta(seconds=info.get('timezone',0)))
    sr = datetime.datetime.fromtimestamp(info['sys']['sunrise'], tz).strftime('%H:%M')
    ss = datetime.datetime.fromtimestamp(info['sys']['sunset'], tz).strftime('%H:%M')

    def wind_dir(d):
        dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
        return dirs[int((d+11.25)//22.5) % 16]

    # build lines
    lines = []
    lines.append(f"{city}, {cc} • {desc}")
    lines.append(f"{lat:.2f}, {lon:.2f}\n")
    lines.append(f"{t_c:.0f}°C feels {fl_c:.0f}°C")
    lines.append(f"Humidity {hum}% • Pressure {pres} hPa")

    wind_line = f"Wind {wspd:.1f} m/s {wind_dir(wdeg)}"
    if gust:
        wind_line += f" gust {gust:.1f}"
    if rain_1h:
        wind_line += f" • Rain {rain_1h:.1f} mm/h"
    lines.append(wind_line)

    lines.append(f"Clouds {clouds}% • Visibility {vis_km:.0f} km")
    lines.append(f"Sunrise {sr} • Sunset {ss}")

    return "\n".join(lines)

def get_weather(city,country):

    # Reverse Geo Coding
    reverse_geo_limit = 1
    APP_ID = 'e1f83a674bb103eeb69d7615d0279fc6'
    response = requests.get(f"{OPEN_WEATHER_URL}/geo/1.0/direct?q={city},{country}&limit={reverse_geo_limit}&appid={APP_ID}")
    data = response.json()
    info = data[0]
    lat,lon= info['lat'],info['lon']

    # weather data
    response = requests.get(f"{OPEN_WEATHER_URL}/data/2.5/weather?lat={lat}&lon={lon}&appid={APP_ID}")
    data = response.json()
    result = overview(data)
    print(result)

def main():
    args_len = len(sys.argv)

    if args_len < 2 or args_len > 3:
        raise ValueError("expected city country as argument")
    
    address_list = sys.argv[1:]
    city = address_list[0]
    country = address_list[1]
    get_weather(city=city,country=country)

if __name__ == "__main__":
    main()
