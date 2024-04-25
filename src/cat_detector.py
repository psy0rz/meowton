from asyncio import Event

from peewee import fn

import db_cat
from db_cat import DbCat
from scale import Scale

MIN_WEIGHT = 100


class CatDetector:
    """detects which cat is on the scale and generates events"""

    def __init__(self):

        self.cat: DbCat | None = None

        self.event_changed = Event()

    def __event_changed(self):
        """called when a different cat is detected (or None)"""
        if self.cat is not None:
            print(f"CatDetector: cat changed to {self.cat.name}")
        else:
            print(f"CatDetector: cat left")

        self.event_changed.set()
        self.event_changed.clear()

    def __find_closest_weight(self, target_weight) -> DbCat | None:

        if target_weight < MIN_WEIGHT:
            return None

        closest_cat: DbCat | None = None

        for cat in DbCat.cats.values():
            if (closest_cat is None or
                    abs(target_weight - cat.weight) < abs(target_weight - closest_cat.weight)):
                closest_cat = cat

        # not close enough?
        if abs(closest_cat.weight - target_weight) > target_weight * 0.02:
            return None

        return closest_cat

    async def task(self, scale: Scale):
        current_id = None

        # wait for the cat scale to change
        while await scale.event_stable.wait():

            weight = scale.last_stable_weight
            cat = self.__find_closest_weight(weight)

            if cat is None:
                id = None
            else:
                id = cat.id

            if current_id != id:
                current_id = id

                # save previous cat
                if self.cat is not None:
                    self.cat.save()

                self.cat = cat
                self.__event_changed()
