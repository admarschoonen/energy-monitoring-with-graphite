#!/usr/bin/python3
import json
import time
import pyowm
import sys
import socket

with open('/etc/energy-monitoring-with-graphite/OpenWeatherMap/settings.json') as json_data:
    d = json.load(json_data)
    api_key = d['API_key']
    location = d['location']
    metrics = d['metrics']
    paths = d['paths']
    interval = d['interval']
    server = d['server']
    port = d['port']

owm = pyowm.OWM(api_key)

while True:
    t_start = time.time()
    try:
        observation = owm.weather_at_place(location)
        weather = observation.get_weather()
    except:
        time.sleep(interval)
        continue

    t = ''
    n = 0
    for m in metrics:
        p = ''
        if m == 'humidity':
            p = paths[n]
            v = str(weather.get_humidity())
        if m == 'temperature':
            p = paths[n]
            v = str(weather.get_temperature('celsius')['temp'])
        if m == 'day_length':
            p = paths[n]
            sunrise = weather.get_sunrise_time()
            sunset = weather.get_sunset_time()
            day_length = (float(sunset) - float(sunrise)) / float(3600)
            v = str(day_length)

        if p != '':
            t = t + p + ' ' + v + ' ' + str(int(t_start)) + '\n'

        n = n + 1

    if t != '':
        try:
            s = socket.socket()
            s.connect((server, port))
            s.send(t.encode('ascii'))
            s.close()
        except:
            print(time.ctime(t_start) + ' OpenWeatherMap: Error: Could not send message.')

    t_now = time.time()
    if (t_now - t_start) < interval:
        time.sleep(interval - (t_now - t_start))

sys.exit(0)

