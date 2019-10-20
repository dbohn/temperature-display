# Temperature Display

This application fetches temperature data from an InfluxDB time-series database and visualizes the current temperature data on an e-ink display.

# Setup
Requires Python 3.7.

Install dependencies using

```
pip3 install -r requirements.txt
```

Make sure, to install the used fonts. By default, deja vu sans is used:

```
sudo apt-get install fonts-dejavu
```

Also enable hardware SPI using raspi-config. Duplicate `config.example.json` to `config.json` and adjust the settings.