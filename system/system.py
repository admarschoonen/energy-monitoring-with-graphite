import json
import time
import os
import sys
import socket
import psutil
from collections import namedtuple

disk_ntuple = namedtuple('partition',  'device mountpoint fstype')
usage_ntuple = namedtuple('usage',  'total used free percent')

# from https://stackoverflow.com/questions/4260116/find-size-and-free-space-of-the-filesystem-containing-a-given-file

def disk_partitions(all=False):
    """Return all mountd partitions as a nameduple.
    If all == False return phyisical partitions only.
    """
    phydevs = []
    f = open("/proc/filesystems", "r")
    for line in f:
        if not line.startswith("nodev"):
            phydevs.append(line.strip())

    retlist = []
    f = open('/etc/mtab', "r")
    for line in f:
        if not all and line.startswith('none'):
            continue
        fields = line.split()
        device = fields[0]
        mountpoint = fields[1]
        fstype = fields[2]
        if not all and fstype not in phydevs:
            continue
        if device == 'none':
            device = ''
        ntuple = disk_ntuple(device, mountpoint, fstype)
        retlist.append(ntuple)
    return retlist

def disk_usage(path):
    """Return disk usage associated with path."""
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    # NB: the percentage is -5% than what shown by df due to
    # reserved blocks that we are currently not considering:
    # http://goo.gl/sWGbH
    return usage_ntuple(total, used, free, round(percent, 1))



with open('settings.json') as json_data:
    d = json.load(json_data)
    metrics = d['metrics']
    paths = d['paths']
    interval = d['interval']
    server = d['server']
    port = d['port']

while True:
    t_start = time.time()
    t = ''
    n = -1
    for m in metrics:
        p = ''
        n = n + 1
        if m == "load":
            p = paths[n]
            v = str(os.getloadavg()[0])
        if m == "cpu_usage":
            x = psutil.cpu_percent(percpu = True)
            x.append(sum(x) / float(len(x)))
            v = []
            p = []
            k = 0
            for val in x:
                v.append(str(val))
                p.append(paths[n] + '.' + str(k))
                k = k + 1
        if m == "ram_available":
            p = paths[n]
            v = str(float(psutil.virtual_memory().available) / 1024.0 / 1024.0)
        if m == "disk_free":
            v = []
            p = []
            k = 0
            for part in disk_partitions():
                p.append(paths[n] + '.' + part.mountpoint.replace("/", "_"))
                x = float(disk_usage(part.mountpoint).free) / 1024.0 / 1024.0
                v.append(str(x)) 

        if p != '':
            if not isinstance(v, (list, )):
                v = [v]
                p = [p]

            k = 0
            for e in v:
                t = t + p[k] + ' ' + e + ' ' + str(int(t_start)) + '\n'
                k = k + 1

    if t != '':
        try:
            s = socket.socket()
            s.connect((server, port))
            s.send(t.encode('ascii'))
            s.close()
        except:
            print(time.ctime(t_start) + ' System: Error: Could not send message.')

    t_now = time.time()
    if (t_now - t_start) < interval:
        time.sleep(interval - (t_now - t_start))

sys.exit(0)


