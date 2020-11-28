#!/usr/bin/python3
import json
import time
from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V2_2, SERIAL_SETTINGS_V4, SERIAL_SETTINGS_V5
from dsmr_parser import obis_references
import sys
import socket
import requests

def retrieve_current_value_from_path(path):
    t = ['-1s', '-1min', '-1hours', '-1days', '-7days', '-30days']
    l = None
    k = 0
    while l is None:
        url = 'http://data/render?target=' + path + '&from=' + t[k] + '&format=json'
        # print('url: ' + url)
        r = requests.get(url, verify=False)
        j = json.loads(r.text)
        for i in j:
            l = i['datapoints'][-1][0]
        k = k + 1
        if k >= len(t):
            break
    return l

def retrieve_current_value_from_metric_names(delta_name, metric_name):
    # retrieve current value from metric with name metric_name
    value = None
    for m in metrics:
        if m == delta_name:
            k = 0
            p = None
            for m_ in metrics:
                if m_ == metric_name:
                    p = paths[k]
                    break
                k = k + 1
            if p is not None:
                value = retrieve_current_value_from_path(p)
    if value is None:
        value = 0
    return value

with open('/etc/energy-monitoring-with-graphite/dsmr/settings.json') as json_data:
    d = json.load(json_data)
    device = d['device']
    dsmr_version = d['dsmr_version']
    metrics = d['metrics']
    paths = d['paths']
    interval = d['interval']
    server = d['server']
    port = d['port']

if dsmr_version >= 5.0:
     serial_settings = SERIAL_SETTINGS_V5
     telegram_specification = telegram_specifications.V5
elif dsmr_version >= 4.0:
     serial_settings = SERIAL_SETTINGS_V4
     telegram_specification = telegram_specifications.V4
elif dsmr_version >= 2.2:
     serial_settings = SERIAL_SETTINGS_V2_2
     telegram_specification = telegram_specifications.V2_2
else:
    print('Error: unsupported version: ' + str(dsmr_version))
    sys.exit(1)

t_now = time.time()

electricity_used_tariff_1_old = 0
electricity_used_tariff_2_old = 0
electricity_used_tariff_1_2_old = 0
electricity_delivered_tariff_1_old = 0
electricity_delivered_tariff_2_old = 0
electricity_delivered_tariff_1_2_old = 0
hourly_gas_meter_reading_old = 0
gas_meter_reading_old = 0

# print(time.ctime(t_now) + ' Retrieving current values')
# electricity_used_tariff_1_old = retrieve_current_value_from_metric_names(
#     'electricity_delta_used_tariff_1', 'electricity_used_tariff_1')
# electricity_used_tariff_2_old = retrieve_current_value_from_metric_names(
#     'electricity_delta_used_tariff_2', 'electricity_used_tariff_2')
# electricity_used_tariff_1_2_old = retrieve_current_value_from_metric_names(
#     'electricity_delta_used_tariff_1_2', 'electricity_used_tariff_1_2')
# 
# electricity_delivered_tariff_1_old = retrieve_current_value_from_metric_names(
#     'electricity_delta_delivered_tariff_1', 'electricity_delivered_tariff_1')
# electricity_delivered_tariff_2_old = retrieve_current_value_from_metric_names(
#     'electricity_delta_delivered_tariff_2', 'electricity_delivered_tariff_2')
# electricity_delivered_tariff_1_2_old = retrieve_current_value_from_metric_names(
#     'electricity_delta_delivered_tariff_1_2', 'electricity_delivered_tariff_1_2')
# 
# hourly_gas_meter_reading_old = retrieve_current_value_from_metric_names(
#     'delta_hourly_gas_meter_reading', 'hourly_gas_meter_reading')
# gas_meter_reading_old = retrieve_current_value_from_metric_names(
#     'delta_ggas_meter_reading', 'hourly_gas_meter_reading')
# 
# print('current values: ')
# print('electricity_used_tariff_1:   ' + str(electricity_used_tariff_1_old))
# print('electricity_used_tariff_2:   ' + str(electricity_used_tariff_2_old))
# print('electricity_used_tariff_1_2: ' + str(electricity_used_tariff_1_2_old))
# print('electricity_delivered_tariff_1:   ' + str(electricity_delivered_tariff_1_old))
# print('electricity_delivered_tariff_2:   ' + str(electricity_delivered_tariff_2_old))
# print('electricity_delivered_tariff_1_2: ' + str(electricity_delivered_tariff_1_2_old))
# print('hourly_gas_meter_reading: ' + str(hourly_gas_meter_reading_old))
# print('gas_meter_reading: ' + str(gas_meter_reading_old))

serial_reader = SerialReader(device = device, 
    serial_settings = serial_settings, 
    telegram_specification = telegram_specification)

got_socket = False
while True:
    try:
        for telegram in serial_reader.read():
            t_start = time.time()
            #print(str(telegram[obis_references.P1_MESSAGE_TIMESTAMP].value))
            t = ''
            n = -1
            for m in metrics:
                p = ''
                n = n + 1
                if m == "p1_message_header":
                    try:
                        v = str(int(telegram[obis_references.P1_MESSAGE_HEADER].value))
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_imported_total":
                    try:
                        v = str(float(telegram[obis_references.ELECTRICITY_IMPORTED_TOTAL].value))
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_used_tariff_1":
                    try:
                        v = str(float(telegram[obis_references.ELECTRICITY_USED_TARIFF_1].value))
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_used_tariff_2":
                    try:
                        v = str(float(telegram[obis_references.ELECTRICITY_USED_TARIFF_2].value))
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delivered_tariff_1":
                    try:
                        v = str(float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_1].value))
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delivered_tariff_2":
                    try:
                        v = str(float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_2].value))
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_active_tariff":
                    try:
                        v = str(int(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_2].value))
                        p = paths[n]
                    except:
                        continue
                if m == "equipment_id":
                    try:
                        v = str(float(telegram[obis_references.EQUIPMENT_ID].value))
                        p = paths[n]
                    except:
                        continue
                if m == "current_electricity_usage":
                    try:
                        v = str(float(telegram[obis_references.CURRENT_ELECTRICITY_USAGE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "current_electricity_delivery":
                    try:
                        v = str(float(telegram[obis_references.CURRENT_ELECTRICITY_DELIVERY].value))
                        p = paths[n]
                    except:
                        continue
                if m == "long_power_failure_count":
                    try:
                        v = str(int(telegram[obis_references.LONG_POWER_FAILURE_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "short_power_failure_count":
                    try:
                        v = str(int(telegram[obis_references.SHORT_POWER_FAILURE_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "voltage_sag_l1_count":
                    try:
                        v = str(int(telegram[obis_references.VOLTAGE_SAG_L1_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "voltage_sag_l2_count":
                    try:
                        v = str(int(telegram[obis_references.VOLTAGE_SAG_L2_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "voltage_sag_l3_count":
                    try:
                        v = str(int(telegram[obis_references.VOLTAGE_SAG_L3_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "voltage_swell_l1_count":
                    try:
                        v = str(int(telegram[obis_references.VOLTAGE_SWELL_L1_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "voltage_swell_l2_count":
                    try:
                        v = str(int(telegram[obis_references.VOLTAGE_SWELL_L2_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "voltage_swell_l3_count":
                    try:
                        v = str(int(telegram[obis_references.VOLTAGE_SWELL_L3_COUNT].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_voltage_l1":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_VOLTAGE_L1].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_voltage_l2":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_VOLTAGE_L2].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_voltage_l3":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_VOLTAGE_L3].value))
                        p = paths[n]
                    except:
                        continue
                if m == "text_message_code":
                    try:
                        v = str((telegram[obis_references.TEXT_MESSAGE_CODE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "text_message":
                    try:
                        v = str((telegram[obis_references.TEXT_MESSAGE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "device_type":
                    try:
                        v = str(int(telegram[obis_references.DEVICE_TYPE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_active_power_l1_positive":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_active_power_l2_positive":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_active_power_l3_positive":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_active_power_l1_negative":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_active_power_l2_negative":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "instantaneous_active_power_l3_negative":
                    try:
                        v = str(float(telegram[obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE].value))
                        p = paths[n]
                    except:
                        continue
                if m == "equipment_identifier_gas":
                    try:
                        v = str(int(telegram[obis_references.EQUIPMENT_IDENTIFIER_GAS].value))
                        p = paths[n]
                    except:
                        continue
                if m == "hourly_gas_meter_reading":
                    try:
                        v = str(float(telegram[obis_references.HOURLY_GAS_METER_READING].value))
                        p = paths[n]
                    except:
                        continue
                if m == "gas_meter_reading":
                    try:
                        v = str(float(telegram[obis_references.GAS_METER_READING].value))
                        p = paths[n]
                    except:
                        continue
                if m == "actual_threshold_electricity":
                    try:
                        v = str(float(telegram[obis_references.ACTUAL_THRESHOLD_ELECTRICITY].value))
                        p = paths[n]
                    except:
                        continue
                if m == "actual_switch_position":
                    try:
                        v = str(int(telegram[obis_references.ACTUAL_SWITCH_POSITION].value))
                        p = paths[n]
                    except:
                        continue
                if m == "valve_position_gas":
                    try:
                        v = str(int(telegram[obis_references.VALVE_POSITION_GAS].value))
                        p = paths[n]
                    except:
                        continue
            
                if m == "electricity_used_tariff_1_2":
                    try:
                        v = str(float(telegram[obis_references.ELECTRICITY_USED_TARIFF_1].value) +
                            float(telegram[obis_references.ELECTRICITY_USED_TARIFF_2].value))
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delivered_tariff_1_2":
                    try:
                        v = str(float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_1].value) +
                            float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_2].value))
                        p = paths[n]
                    except:
                        continue
            
                if m == "electricity_delta_used_tariff_1":
                    try:
                        v2 = float(telegram[obis_references.ELECTRICITY_USED_TARIFF_1].value)
                        v = str(v2 - electricity_used_tariff_1_old)
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delta_used_tariff_2":
                    try:
                        v2 = float(telegram[obis_references.ELECTRICITY_USED_TARIFF_2].value)
                        v = str(v2 - electricity_used_tariff_2_old)
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delta_used_tariff_1_2":
                    try:
                        v2a = float(telegram[obis_references.ELECTRICITY_USED_TARIFF_1].value)
                        v2b = float(telegram[obis_references.ELECTRICITY_USED_TARIFF_2].value)
                        v2 = v2a + v2b
                        v = str(v2 - electricity_used_tariff_1_2_old)
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delta_delivered_tariff_1":
                    try:
                        v2 = float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_1].value)
                        v = str(v2 - electricity_delivered_tariff_1_old)
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delta_delivered_tariff_2":
                    try:
                        v2 = float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_2].value)
                        v = str(v2 - electricity_delivered_tariff_2_old)
                        p = paths[n]
                    except:
                        continue
                if m == "electricity_delta_delivered_tariff_1_2":
                    try:
                        v2a = float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_1].value)
                        v2b = float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_2].value)
                        v2 = v2a + v2b
                        v = str(v2 - electricity_delivered_tariff_1_2_old)
                        p = paths[n]
                    except:
                        continue
                if m == "delta_hourly_gas_meter_reading":
                    try:
                        v2 = float(telegram[obis_references.HOURLY_GAS_METER_READING].value)
                        v = str(v2 - hourly_gas_meter_reading_old)
                        p = paths[n]
                    except:
                        continue
                if m == "delta_gas_meter_reading":
                    try:
                        v2 = float(telegram[obis_references.GAS_METER_READING].value)
                        v = str(v2 - gas_meter_reading_old)
                        p = paths[n]
                    except:
                        continue
                    
                if p != '':
                    t = t + p + ' ' + v + ' ' + str(int(t_start)) + '\n'
            
            store_values = False
            if t != '':
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
                        store_values = True
                        print(time.ctime(t_start) + ' dsmr: sent ' + t.encode('ascii'))
                    except:
                        print(time.ctime(t_start) + ' dsmr: Error: Could not send message (send failed).')
                        s.close()
                        got_socket = False
                else:
                    print(time.ctime(t_start) + ' dsmr: Error: Could not send message (no socket).')
        
            if store_values:
                try:
                    electricity_used_tariff_1_old = \
                        float(telegram[obis_references.ELECTRICITY_USED_TARIFF_1].value)
                except:
                    electricity_used_tariff_1_old = 0
                try:
                    electricity_used_tariff_2_old = \
                        float(telegram[obis_references.ELECTRICITY_USED_TARIFF_2].value)
                except:
                    electricity_used_tariff_2_old = 0
                try:
                    electricity_used_tariff_1_2_old = electricity_used_tariff_1_old + \
                        electricity_used_tariff_2_old 
                except:
                    electricity_used_tariff_1_2_old = 0
                try:
                    electricity_delivered_tariff_1_old = \
                        float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_1].value)
                except:
                    electricity_delivered_tariff_1_old = 0
                try:
                    electricity_delivered_tariff_2_old = \
                        float(telegram[obis_references.ELECTRICITY_DELIVERED_TARIFF_2].value)
                except:
                    electricity_delivered_tariff_2_old = 0
                try:
                    electricity_delivered_tariff_1_2_old = electricity_delivered_tariff_1_old + \
                        electricity_delivered_tariff_2_old 
                except:
                    electricity_delivered_tariff_1_2_old = 0
                try:
                    hourly_gas_meter_reading_old = \
                        float(telegram[obis_references.HOURLY_GAS_METER_READING].value)
                except:
                    hourly_gas_meter_reading_old = 0
                try:
                    gas_meter_reading_old = \
                        float(telegram[obis_references.GAS_METER_READING].value)
                except:
                    gas_meter_reading_old = 0
        
            t_now = time.time()
            if (t_now - t_start) < interval:
                time.sleep(interval - (t_now - t_start))
    except:
        print(time.ctime(t_start) + ' dsmr: Error: Could parse dsmr message.')

sys.exit(0)
