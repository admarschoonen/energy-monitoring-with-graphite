import json
import time
import nest
import sys
import socket

with open('settings.json') as json_data:
    d = json.load(json_data)
    client_id = d['client_id']
    client_secret = d['client_secret']
    metrics = d['metrics']
    paths = d['paths']
    interval = d['interval']
    server = d['server']
    port = d['port']

access_token_cache_file = 'nest.json'
product_version = 0

napi = nest.Nest(client_id=client_id, client_secret=client_secret, 
        access_token_cache_file=access_token_cache_file, 
        product_version=product_version)

if napi.authorization_required:
    print('Go to ' + napi.authorize_url + ' to authorize, then enter PIN below')
    if sys.version_info[0] < 3:
        pin = raw_input("PIN: ")
    else:
        pin = input("PIN: ")
    napi.request_token(pin)

while True:
    t_start = time.time()
    t = ''
    n = 0
    for m in metrics:
        # metrics should have following layout:
        # strucure_name.device_type.device_name.device_property

        m_str = m.split('.')
        if len(m_str) != 4:
            print('Error: metric ' + m + ' is not according to the layout strucure_name.device_type.device_name.device_property')
            sys.exit(1)
        else:
            structure_name = m_str[0]
            device_type = m_str[1]
            device_name = m_str[2]
            device_property = m_str[3]

        for nest_struct in napi.structures:
            if nest_struct.name != structure_name:
                continue

            # for now we only support Nest thermostats
            if nest_struct.num_thermostats <= 0:
                continue

            for nest_device in nest_struct.thermostats:
                p = ''
                if nest_device.name != device_name:
                    continue

                if device_property == 'Fan Timer':
                    p = paths[n]
                    v = str(nest_device.fan_timer)

                if device_property == 'Temp':
                    p = paths[n]
                    v = str(nest_device.temperature)

                if device_property == 'Humidity':
                    p = paths[n]
                    v = str(nest_device.humidity)

                if device_property == 'Target':
                    p = paths[n]
                    v = str(nest_device.target)

                if device_property == 'Eco High':
                    p = paths[n]
                    v = str(nest_device.eco_temperature.high)

                if device_property == 'Eco Low':
                    p = paths[n]
                    v = str(nest_device.eco_temperature.low)

                if p != '':
                    t = t + p + ' ' + v + ' ' + str(int(t_start)) + '\n'

        n = n + 1

    if t != '':
        try:
            s = socket.socket()
            s.connect((server, port))
            s.send(t)
            s.close()
        except:
            print(time.ctime(t_start) + ' Nest: Error: Could not send message.')

    t_now = time.time()
    if (t_now - t_start) < interval:
        time.sleep(interval - (t_now - t_start))



sys.exit(0)

while True:
    t_start = time.time()
    try:
        observation = owm.weather_at_place(location)
        weather = observation.get_weather()
    except:
        continue

    n = 0
    for m in metrics:
        p = ''
        if m == 'humidity':
            p = paths[n]
            v = str(weather.get_humidity())
        if m == 'temperature':
            p = paths[n]
            v = str(weather.get_temperature('celsius')['temp'])

        if p != '':
            t = p + ' ' + v + ' ' + str(int(t_start)) + '\n'
            s = socket.socket()
            s.connect((server, port))
            s.send(t)
            s.close()

        n = n + 1


    t_now = time.time()
    if (t_now - t_start) < interval:
        time.sleep(interval - (t_now - t_start))

