from feeder import Feeder
from scale import Scale

IGNORE_ADDED_ABOVE = 1
IGNORE_REMOVED_ABOVE = 1

from asyncio import Event


class FoodCounter:
    """count the amount of food that is eaten from the scale, since last reset()"""
    def __init__(self):
        self.ate = 0
        self.event_ate=Event()

    async def task(self, scale: Scale, feeder:Feeder):
        prev_weight = 0
        while await scale.event_stable.wait():
            weight = scale.last_stable_weight
            removed = prev_weight - weight

            if feeder.feeding:
                print("FoodCounter: Feeder running, ignoring change")
            elif removed < -IGNORE_ADDED_ABOVE:
                print(f"FoodCounter: Ignoring big added weight {-removed:0.2f}g")
            elif removed > IGNORE_REMOVED_ABOVE:
                print(f"FoodCounter: Ignoring big removed weight {removed:0.2f}g")
            else:
                self.ate += removed
                print(f"FoodCounter: Ate {removed:0.2f}g, total = {self.ate:0.2f}g")
                self.event_ate.set()
                self.event_ate.clear()

            prev_weight = weight

    def reset(self):
        self.ate = 0
