#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from screen import Screen
from sensors import SensorCollection
from gpiozero import Button
import json
from time import sleep

from influxdb import InfluxDBClient

class App(object):
    def __init__(self):
        config = self.load_config("config.json")
        self.client = InfluxDBClient(config['influxdb']['host'], config['influxdb']['port'], config['influxdb']['user'], config['influxdb']['password'], config['influxdb']['database'], ssl = config['influxdb']['ssl'], verify_ssl = config['influxdb']['verify_ssl'])
        self.sensors = SensorCollection("sensors.json", client)
        self.screen = Screen(sensors.sensors)
        self.buttons = {}
        self.register_button(5, self.update)

    def update(self):
        print("Updating screen")
        self.sensors.update()
        self.screen.update()

    def loop(self):
        self.update()
        sleep(30)

    def load_config(self, filename):
        with open("config.json", encoding="utf-8") as configFile:
            return json.load(configFile)

    def register_button(self, key, handler):
        button = Button(key)
        button.when_pressed = handler
        self.buttons.update({key: button})


if __name__ == "__main__":
    print("Launching thermometer...")
    app = App()
    while True:
        app.loop()

print("Exit")