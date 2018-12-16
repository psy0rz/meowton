import time

timestamp=0

#we have a changeble timer so we can also run simulations
def update(set=time.ticks_ms()):
    global timestamp
    timestamp=set
