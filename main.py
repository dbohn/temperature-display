#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from screen import Screen
from sensors import Sensor
import json

from influxdb import InfluxDBClient

with open("config.json", encoding="utf-8") as configFile:
    config = json.load(configFile)

client = InfluxDBClient(config['influxdb']['host'], config['influxdb']['port'], config['influxdb']['user'], config['influxdb']['password'], config['influxdb']['database'], ssl = config['influxdb']['ssl'], verify_ssl = config['influxdb']['verify_ssl'])

sensorData = {
    "sensors": []
}
with open("sensors.json", encoding='utf-8') as file:
    sensorData = json.load(file)

sensors = []

for sensor in sensorData['sensors']:
    sensors.append(Sensor(sensor['name'], 0.00, sensor['unit'], sensor['metric']))

sensorNames = list(map(lambda sensor: sensor.metric, sensors))
result = client.query('select last(value) from {}'.format(', '.join(sensorNames)))

for sensor in sensors:
    measurements = list(result.get_points(measurement=sensor.metric))
    if len(measurements) > 0:
        sensor.value = measurements[0]['last']
    else:
        sensor.value = None

screen = Screen(sensors)

screen.update()
