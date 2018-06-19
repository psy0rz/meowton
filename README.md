# Automatic cat weighing system 

Meowton is a system that will automaticly weigh your cat and create nice graphs.

goals of the project:

* Automaticly weigh a cat with high accuracy while its eating
* Create graphs so you can see if your cat is getting heavier/lighter or becomes sick for example.
* Track weight of multiple cats by recognizing them by weight.
* Operate a cat feeder and making sure each cat get a certain amount of food per day. (Mogwai needs to loose weight)

# Examples

Note: old graphs from before the feeder. Mogwai has been losing weight slowly but steady for the past 6 weeks. Its amazing how much weight he gained in a couple days of over feeding. It takes weeks to lose it.


Example of graphs (Created with Grafana):

![global](https://github.com/psy0rz/meowton/blob/master/examples/Cat%200.png?raw=true)

![global](https://github.com/psy0rz/meowton/blob/master/examples/Cat%201.png?raw=true)

# Hardware overview

Electronics on prototype board:

![electronics](https://github.com/psy0rz/meowton/blob/master/examples/20170104_015539.jpg?raw=true)

Mogwai eating food from the dispenser while he automagically is getting weighed:

![cataction](https://github.com/psy0rz/meowton/blob/master/examples/20180408_210341.jpg?raw=true)

# Parts

 * 4x 5kg Kitchen Scale Electronic Load Cell Weighing Sensor: www.banggood.com/5Pcs-YZC-133-5kg-Kitchen-Scale-Electronic-Load-Cell-Weighing-Sensor-p-1043899.html
 * 4x 24 Bit AD HX711 Weighing Pressure Sensor Module For Arduino: www.banggood.com/5Pcs-24-Bit-AD-HX711-Weighing-Pressure-Sensor-Module-For-Arduino-p-953336.html
 * Some kind of ESP8266 ESP-12E, i used this one: www.banggood.com/Geekcreit-Doit-NodeMcu-Lua-ESP8266-ESP-12E-WIFI-Development-Board-p-985891.html
 * Breadboards and jumper wires. (you find them anywhere)


# Architecture

The raw data is collected from the scale 24/7:

[ Load cells ] -> [ HX711 ] -> [ ESP8266 ] -- raw measurement data (10/s) http --> [ analyser.py ] --> [ influxdb ]

 * Scale measures all sensors 10 times per second
 * It will send a batch of raw measurements to the analyser approx every 7 seconds.
 * When the scale is idle for a certain time it will stop sending data.
 
 * The analyser will store all raw data in the Influxdb, for testing/debugging and reanalysing with a new version in the future. 
 
 * The analyser will also take this raw data and do tarring, calibration and generate weighing events.
 * With these events it will determine which cat is on the scale and create a sepearte Influxdb entry for that. (Measurement 'cats', field 'weight' and the tag contains the cat-name)
 
 * If you build a seperate cat-feeder, it can send http events to give each cat a certain number of portions per day, depending on the configured feed-rate. (look in the sourcecode how to do this, it basicaly involves adding a bunch of fields to each cat in the analyser.yaml file)
 * I created a simple ESPEasy plugin to operate a simple worm-wheel based feeder, like the ones you find on thingiverse. (altough i'm currently using parts of a coffee machine to do it) You can that plugin here: https://github.com/letscontrolit/ESPEasyPluginPlayground/blob/master/_P203_Feeder.ino 
 
 
 
 
 
 

# Cloning this project

This project has submodule, therefore you should use the --recursive option:

 git clone --resursive https://github.com/psy0rz/meowton.git


