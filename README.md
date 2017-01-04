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

# example graphs

Every measurement creates a graph for analasys and debugging:

![cat 0](https://github.com/psy0rz/meowton/blob/master/examples/1481594272.png?raw=true)

Example of a global graph (we need more data and tuning of curvefitting/smooting):
![global](https://github.com/psy0rz/meowton/blob/master/examples/Cat%200.png?raw=true)



# Cloning this project

This project has submodule, therefore you should use the --recursive option:

 git clone --resursive https://github.com/psy0rz/meowton.git


