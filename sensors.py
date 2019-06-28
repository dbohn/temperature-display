import json

class Sensor(object):
    def __init__(self, name, value, unit, metric):
        self.name = name
        self.value = value
        self.unit = unit
        self.metric = metric
        self.units = {
            'temperature': '\u2103'
        }

    def measurementValue(self):
        if self.value is None:
            return 'N/A'
        return '{:05.2f} {}'.format(self.value, self.units[self.unit])

class SensorCollection(object):
    def __init__(self, configFile, influxClient):
        self.configFile = configFile
        self.client = influxClient
        self.sensors = self.loadSensors()

    def loadSensors(self):
        sensorData = {
            "sensors": []
        }
        with open(self.configFile, encoding='utf-8') as file:
            sensorData = json.load(file)

        sensors = []

        for sensor in sensorData['sensors']:
            sensors.append(Sensor(sensor['name'], 0.00, sensor['unit'], sensor['metric']))

        return sensors

    def update(self):
        sensorNames = list(map(lambda sensor: sensor.metric, self.sensors))
        result = self.client.query('select last(value) from {}'.format(', '.join(sensorNames)))

        for sensor in self.sensors:
            measurements = list(result.get_points(measurement=sensor.metric))
            if len(measurements) > 0:
                sensor.value = measurements[0]['last']
            else:
                sensor.value = None