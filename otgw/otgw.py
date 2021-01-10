#!/usr/bin/python3
import asyncio
import json
import time
from pyotgw import pyotgw
import sys
import socket
import requests

global got_socket
global s
global metrics
global paths
global cache
global t_last

cache = {}
got_socket = False
s = None

with open('/etc/energy-monitoring-with-graphite/otgw/settings.json') as json_data:
    d = json.load(json_data)
    device = d['device']
    metrics = d['metrics']
    paths = d['paths']
    interval = d['interval']
    server = d['server']
    port = d['port']

s = None
t_last = int(time.time())

async def send_msg(): 
  global cache
  global t_last
  global got_socket
  global s

  while True:
    t_start = time.time()
    t_now = int(t_start)

    if t_last < t_now:
      t = ''
      for key in cache:
          t = t + key + ' ' + cache[key] + ' ' + str(int(t_start)) + '\n'

      if t != '':
          print(time.ctime(t_start) + ' otgw: sending ' + t)
          if got_socket == False:
              try:
                  s = socket.socket()
                  s.connect((server, port))
                  got_socket = True
              except:
                  s.close()
                  got_socket = False
      
          if got_socket:
              try:
                  s.send(t.encode('ascii'))
                  print(time.ctime(t_start) + ' otgw: sent ' + t)
              except:
                  print(time.ctime(t_start) + ' otgw: Error: Could not send message (send failed).')
                  s.close()
                  got_socket = False
          else:
              print(time.ctime(t_start) + ' otgw: Error: Could not send message (no socket).')

      t_last = t_now

    await asyncio.sleep(1)

async def print_status(status):
  """Receive and print status."""
  global metrics
  global paths
  global cache

  print("Received a status update:\n{}".format(status))
  #print(str(telegram[obis_references.P1_MESSAGE_TIMESTAMP].value))
  n = -1
  for m in metrics:
      x = m.split('.')
      base = x[0]
      ext = x[1]
      p = ''
      n = n + 1
      try:
          V = json.loads("{}".format(status).replace('\'', '"').replace('None', '"None"'))
          v = str(float(V[base][ext]))
          p = paths[n]
      except:
          continue
          
      if p != '':
          cache[p] = v

async def connect_and_subscribe():
  """Connect to the OpenTherm Gateway and subscribe to status updates."""

  # Create the object
  gw = pyotgw()

  # Connect to OpenTherm Gateway on device
  status = await gw.connect(asyncio.get_event_loop(), device)
  print("Initial status after connecting:\n{}".format(status))

  # Subscribe to updates from the gateway
  if not gw.subscribe(print_status):
    print("Could not subscribe to status updates.")

  # Keep the event loop alive...
  while True:
    await asyncio.sleep(1)

# Set up the event loop and run the connect_and_subscribe coroutine.
loop = asyncio.get_event_loop()
loop.create_task(connect_and_subscribe())
loop.create_task(send_msg())
loop.run_forever()

"""
try:
  loop.run_until_complete(connect_and_subscribe())
except KeyboardInterrupt:
  print("Exiting")
"""

sys.exit(0)
