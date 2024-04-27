from asyncio import Event

from db_cat import DbCat
from db_cat_session import DbCatSession
from scale import Scale
from util import Status

MIN_WEIGHT = 100


class CatDetector:
    """detects which cat is on the scale and generates DbCatSessions. also records max weight of cat during a weighing session"""

    def __init__(self):

        self.cat: DbCat | None = None
        self.cat_session: DbCatSession | None = None

        self.event_changed = Event()

        self.unknown_ate = 0

        self.status_msg = "Ready"
        self.status: Status = Status.OK

    def __event_changed(self):
        """called when a different cat is detected (or None)"""

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
        if closest_cat is not None and abs(closest_cat.weight - target_weight) > target_weight * 0.02:
            return None

        return closest_cat

    def ate(self, weight):
        """called by food detector task to inform us of eaten food"""
        if self.cat is None:
            self.unknown_ate += weight
            print(f"CatDetector: unknown cat ate {weight:0.2f}g (total: {self.unknown_ate:0.2f}g)")
        else:
            self.cat.ate(weight)
            self.cat_session.ate += weight

            self.status_msg = f"{self.cat.name} ate {self.cat_session.ate:0.2f}g"
            self.status = Status.BUSY

    def __start_session(self, cat: DbCat):

        if cat is None:
            return

        print(f"CatDetector: {cat.name} on scale.")

        # take into account food that was already eaten before session started:
        if self.unknown_ate != 0:
            print(f"CatDetector: {cat.name} probably already ate {self.unknown_ate:0.2f}g")
            cat.ate(self.unknown_ate)

        self.cat = cat
        self.cat_session = DbCatSession.create(cat=cat, ate=self.unknown_ate)

        self.unknown_ate = 0

    def __end_session(self, max_weight:float):

        if self.cat is None:
            return

        # note that we want the maximum weight of the cat during this session, to make sure the whole cat, including its tail is measured :D
        self.cat.update_weight(max_weight)
        self.cat.save()
        self.cat_session.weight=max_weight
        self.cat_session.end_session()

        print(f"CatDetector: {self.cat.name} left. Max weight {max_weight:0.2f}g . Ate {self.cat_session.ate:0.2f}g . Duration {self.cat_session.length}s")

        self.cat_session = None
        self.cat = None

    async def task(self, cat_scale: Scale):

        current_id = None
        max_weight = 0

        # wait for the cat scale to change
        while await cat_scale.event_stable.wait():

            weight = cat_scale.last_stable_weight

            cat = self.__find_closest_weight(weight)

            if cat is None:
                id = None

            else:
                id = cat.id

            # changed?
            if current_id != id:
                current_id = id

                self.__end_session(max_weight)
                max_weight = 0
                self.__start_session(cat)
                self.__event_changed()

            if weight > max_weight:
                max_weight = weight

            #update status:

            if self.cat is not None:
                self.status_msg = f"{self.cat.name} ate {self.cat_session.ate:0.2f}g"
                self.status = Status.BUSY
            else:
                if weight<-50:
                    self.status_msg = "Out of range"
                    self.status = Status.ERROR
                elif weight>MIN_WEIGHT:
                    self.status_msg="Unknown cat"
                    self.status=Status.ERROR
                else:
                    self.status_msg="Ready"
                    self.status=Status.OK



