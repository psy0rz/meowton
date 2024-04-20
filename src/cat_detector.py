from typing import TypeAlias, Callable, List

from peewee import fn

from cat import Cat
from cat_session import CatSession
from scale import Scale

MIN_WEIGHT = 100

CatChangedCallable: TypeAlias = Callable[[Cat], None]


class CatDetector:
    """detects which cat is on the scale and generates events"""

    __subscriptions: List[CatChangedCallable]

    def __init__(self, scale: Scale):

        scale.subscribe_stable(self.__scale_stable)
        scale.subscribe_unstable(self.__scale_unstable)

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
        """callback is called when a different cat is detected"""
        self.__subscriptions.append(cb)
        pass

    def __find_closest_weight(self, target_weight):

        if target_weight < MIN_WEIGHT:
            return None

        query = (Cat.select()
                 .order_by(fn.Abs(Cat.weight - target_weight))
                 .limit(1))
        return query.first()

    def __scale_stable(self, weight: float):
        cat: Cat = self.__find_closest_weight(weight)

        if cat is None:
            id=None
        else:
            id=cat.id
            CatSession(cat=cat).save()

        if self.__current_id != id:
            self.__current_id=id
            self.current_cat = cat
            self.__event_changed(cat)


    def __scale_unstable(self):
        pass
