import asyncio


import settings
from cat_detector import CatDetector
from feeder import Feeder
from food_counter import FoodCounter
from food_scheduler import FoodScheduler
from scale import Scale
from sensor_reader import SensorReader

#NOTE: my catfood weigh aprox 0.33g per piece

class Meowton:
    """main class that instantiates the other classes and tasks"""
    food_reader: SensorReader
    food_scale: Scale
    food_counter: FoodCounter
    food_scheduler: FoodScheduler

    cat_reader: SensorReader
    cat_scale: Scale
    cat_detector: CatDetector

    def __init__(self, sim: bool):

        self.init_food(sim)
        self.init_cat(sim)

        self.feeder= Feeder.get_or_create(id=1)[0]

        self.__tasks=set()

    # food scale stuff and default settings
    def init_food(self, sim):
        name = 'food'

        self.food_scale = Scale.get_or_none(name=name)
        if self.food_scale is None:
            self.food_scale = Scale.create(name=name, stable_range=0.1, stable_measurements=2)

        self.food_reader = SensorReader(name, 23, 24, sim, self.food_scale.measurement)
        self.food_counter = FoodCounter()


        self.food_scheduler = FoodScheduler.get_or_none(id=1)
        if self.food_scheduler is None:
            self.food_scheduler = FoodScheduler.create()

    # cat scale stuff and default settings
    def init_cat(self, sim):
        name = 'cat'

        self.cat_scale = Scale.get_or_none(name=name)
        if self.cat_scale is None:
            self.cat_scale = Scale.create(name=name, stable_range=50, stable_measurements=25)

        self.cat_reader = SensorReader(name, 27, 17, sim, self.cat_scale.measurement)
        self.cat_detector = CatDetector()

    def start(self):
        self.food_reader.start()
        self.cat_reader.start()

        self.__tasks.add(asyncio.create_task(self.cat_detector.task(self.cat_scale)))
        self.__tasks.add(asyncio.create_task(self.feeder.task(self.food_scale)))
        self.__tasks.add(asyncio.create_task(self.food_counter.task(self.food_scale, self.feeder)))
        self.__tasks.add(asyncio.create_task(self.food_scheduler.task(self.feeder, self.food_scale)))
        self.__tasks.add(asyncio.create_task(self.task()))

    def stop(self):
        self.food_reader.stop()
        self.cat_reader.stop()

    async def task(self):
        pass
        #

        # while True:
        #
        #
        #     await self.cat_detector.event_changed()

meowton = Meowton(settings.dev_mode)
