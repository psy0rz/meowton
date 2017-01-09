# Automatic cat weighing system 

Meowton is a system that will automaticly weigh your cat and create nice graphs.

goals of the project:

* Automaticly weigh a cat with high accuracy while its eating
* Create graphs so you can see if your cat is getting heavier/lighter or becomes sick for example.
* Track weight of multiple cats by recognizing them by weight.

version 2 goals:
* Track how much the cat is eating and drinking (by weighing the food/water with a seperate scales)

version 3 goals:
* Limit the maximum amount of food each cat can eat in a given time period. (by closing the food bowl with a servo for example)

final goal: 
* ensuring Mogwai gets a healty weight. :)

# Examples

(example graphs of Tracy, she has a healthy weight currently)

Every measurement creates a graph for analysys and debugging:

![cat 0](https://github.com/psy0rz/meowton/blob/master/examples/1481594272.png?raw=true)

Example of a global graph (we need more data and tuning of curvefitting/smooting):
![global](https://github.com/psy0rz/meowton/blob/master/examples/Cat%200.png?raw=true)

# Hardware overview

Electronics on prototype board:

![electronics](https://github.com/psy0rz/meowton/blob/master/examples/20170104_015539.jpg?raw=true)

Tracy eating food while she automagically is getting weighed:

![cataction](https://github.com/psy0rz/meowton/blob/master/examples/20170104_015321.jpg?raw=true)

# Parts

 * 4x 5kg Kitchen Scale Electronic Load Cell Weighing Sensor: www.banggood.com/5Pcs-YZC-133-5kg-Kitchen-Scale-Electronic-Load-Cell-Weighing-Sensor-p-1043899.html
 * 4x 24 Bit AD HX711 Weighing Pressure Sensor Module For Arduino: www.banggood.com/5Pcs-24-Bit-AD-HX711-Weighing-Pressure-Sensor-Module-For-Arduino-p-953336.html
 * Some kind of ESP8266 ESP-12E, i used this one: www.banggood.com/Geekcreit-Doit-NodeMcu-Lua-ESP8266-ESP-12E-WIFI-Development-Board-p-985891.html
 * Breadboards and jumper wires. (you find them anywhere)


# Architecture

The raw data is collected from the scale 24/7:

[ weatstone bridge modules ] -> [ ESP8266] -- raw measurement data (10/s) http --> [ server.py ] --> [ mongodb ]

A seperate analyser generates the graphs. It can work incrementally or reanalyse all the data if we tune it or fix bugs:

[ mongodb ] <- [ analyser.py ] -> [ graphs ]


# Cloning this project

This project has submodule, therefore you should use the --recursive option:

 git clone --resursive https://github.com/psy0rz/meowton.git


