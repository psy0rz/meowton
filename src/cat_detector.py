from asyncio import Event

from peewee import fn

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

    def __find_closest_weight(self, target_weight):

        if target_weight < MIN_WEIGHT:
            return None

        query = (DbCat.select()
                 .order_by(fn.Abs(DbCat.weight - target_weight))
                 .limit(1))
        return query.first()

    async def task(self, scale: Scale):
        current_id = None
        while await scale.event_stable.wait():
            weight = scale.last_stable_weight
            cat: DbCat = self.__find_closest_weight(weight)

            if cat is None:
                id = None
            else:
                id = cat.id

            if current_id != id:
                current_id = id
                self.cat = cat
                self.__event_changed()
