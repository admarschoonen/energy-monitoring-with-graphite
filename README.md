# energy-monitoring-with-graphite
Some scripts to monitor energy usage with Graphite

Will need some more work to:
* centralize configuration
* do proper logging 
* properly store (Nest) access tokens

## Prerequisite
You need to have a working Graphite installation. To install Graphite on a Raspberry PI, you can use the synthesize script from [obfuscurity](https://github.com/obfuscurity/synthesize) or [my version](https://github.com/admarschoonen/synthesize).

## Installation
1. Create the following directories: /etc/energy-monitoring-with-graphite/dsmr, /etc/energy-monitoring-with-graphite/Nest, /etc/energy-monitoring-with-graphite/OpenWeatherMap, /etc/energy-monitoring-with-graphite/system
2. Make sure the user that will run the services (for example, root) has read/write access to /etc/energy-monitoring-with-graphite/Nest to store the access tokens
3. Copy dsmr/settings.json to /etc/energy-monitoring-with-graphite/dsmr, Nest/settings.json to /etc/energy-monitoring-with-graphite/Nest, OpenWeatherMap/settings.json to /etc/energy-monitoring-with-graphite/OpenWeatherMap and system/settings.json to /etc/energy-monitoring-with-graphite/system
4. Create a Nest developer account
5. Run the Nest script once (./Nest/Nest.py) manually to store the access token. It will show a link to the Nest website where you have to allow permissions to collect data. After granting permissions, the Nest site will show a pin code which you have to enter in the terminal. The script will then store the access tokens in /etc/energy-monitoring-with-graphite/Nest/nest.json
6. Create an OpenWeatherMap account
7. Store your OpenWeatherMap API key in /etc/energy-monitoring-with-graphite/OpenWeatherMap/settings.json
8. Copy the energy-monitoring-with-graphite script to /etc/init.d
9. Run systemctl enable energy-monitoring-with-graphite to start all the services
