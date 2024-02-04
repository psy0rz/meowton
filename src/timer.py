import time

timestamp=0

#we have a changeble timer so we can also run simulations, and so we dont "miss" any time 
def update():
    global timestamp
    timestamp=time.ticks_ms()

add=time.ticks_add

diff=time.ticks_diff

update()
