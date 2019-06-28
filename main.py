#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from screen import Screen
from sensors import SensorCollection
from gpiozero import Button
from signal import pause
import json
from threading import Timer

from influxdb import InfluxDBClient

with open("config.json", encoding="utf-8") as configFile:
    config = json.load(configFile)

client = InfluxDBClient(config['influxdb']['host'], config['influxdb']['port'], config['influxdb']['user'], config['influxdb']['password'], config['influxdb']['database'], ssl = config['influxdb']['ssl'], verify_ssl = config['influxdb']['verify_ssl'])

sensors = SensorCollection("sensors.json", client)

screen = Screen(sensors.sensors)

sensors.update()

screen.update()

def update():
    global sensors, screen, t
    print("Update")
    sensors.update()
    screen.update()
    #t = Timer(30, update)
    #t.start()

t = Timer(30, update)
t.start()

print("Waiting for button")
button = Button(5)
button.when_pressed = update

pause()

print("Exit")