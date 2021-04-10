#!/usr/bin/python3
import json
import time
import sys
import socket
import urllib.request

with open('/etc/energy-monitoring-with-graphite/clairvoyance/settings.json') as json_data:
    d = json.load(json_data)
    remote_server = d['remoteServer']
    remote_port = d['remotePort']
    addresses = d['addresses']
    metrics = d['metrics']
    paths = d['paths']
    interval = d['interval']
    server = d['server']
    port = d['port']

t_prev = ''
while True:
    t_start = time.time()
    t = ''
    timestamp_prev = -1
    for a in addresses:
        f = urllib.parse.urlencode({"formula": str(",".join(metrics))})
        a = urllib.parse.urlencode({"address": a})
        url = "http://" + remote_server + ":" + str(remote_port) + "/forecast?" + f + "&" + a
        j = json.loads(urllib.request.urlopen(url).read())
        #print("anser: " + str(json.dumps(j, indent=2)))
        n = 0
        timestamp = j["time"]
        for m in metrics:
            a_ = a.replace(".", "_").replace(" ", "_").replace("address=","").replace("+", "_").replace("%2C", "").replace("%5C", "")
            p = paths[n] + "." + a_

            value = ""
            t_value = 0
            try:
                data = j[m]
                for d in data:
                    if timestamp < d["time"]:
                        value = d["value"]
                        t_value = d["time"]
                        break
            except:
                pass

            v = str(value)

            if p != '' and t_value != 0:
                t = t + p + ' ' + v + ' ' + str(int(t_value)) + '\n'

            n = n + 1

    if t != '' and t != t_prev:
        try:
            s = socket.socket()
            s.connect((server, port))
            s.send(t.encode('ascii'))
            s.close()
            t_prev = t
        except:
            print(time.ctime(t_start) + ' Nest: Error: Could not send message.')

    t_now = time.time()
    if (t_now - t_start) < interval:
        time.sleep(interval - (t_now - t_start))

