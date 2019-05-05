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