from typing import TypeAlias, Callable, List

from peewee import fn

from cat import Cat
from scale import Scale

MIN_WEIGHT = 100

CatChangedCallable: TypeAlias = Callable[[Cat], None]


class CatDetector:
    __subscriptions: List[CatChangedCallable]

    def __init__(self, scale: Scale):
        # self.scale = scale
        scale.subscribe_stable(self.scale_stable)
        scale.subscribe_unstable(self.scale_unstable)

        self.current_cat: Cat | None = None
        self.__current_id: int | None = None

        self.__subscriptions  = []

    def __event_changed(self, cat: Cat):
        """called when a different cat is detected (or None)"""
        if cat is not None:
            print(f"CatDetector: cat changed to {cat.name}")
        else:
            print(f"CatDetector: cat left")

        for cb in self.__subscriptions:
            cb(cat)

    def subscribe(self, cb: CatChangedCallable):
        self.__subscriptions.append(cb)
        pass

    def find_closest_weight(self, target_weight):

        if target_weight < MIN_WEIGHT:
            return None

        query = (Cat.select()
                 .order_by(fn.Abs(Cat.weight - target_weight))
                 .limit(1))
        return query.first()

    def scale_stable(self, weight: float):
        cat: Cat = self.find_closest_weight(weight)

        if cat is None:
            id=None
        else:
            id=cat.id

        if self.__current_id != id:
            self.__current_id=id
            self.current_cat = cat
            self.__event_changed(cat)


    def scale_unstable(self):
        pass
