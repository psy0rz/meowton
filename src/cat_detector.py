from peewee import fn

from cat import Cat
from scale import Scale

MIN_WEIGHT = 100


class CatDetector:

    def __init__(self, scale: Scale):
        # self.scale = scale
        scale.subscribe_stable(self.scale_stable)
        scale.subscribe_unstable(self.scale_unstable)

    def find_closest_weight(self, target_weight):

        if target_weight < MIN_WEIGHT:
            return None

        query = (Cat.select()
                 .order_by(fn.Abs(Cat.weight - target_weight))
                 .limit(1))
        return query.first()

    def scale_stable(self, weight: float):
        cat: Cat = self.find_closest_weight(weight)
        if cat is not None:
            print(f" {cat.name} = {cat.weight}g")
        pass

    def scale_unstable(self):
        pass
