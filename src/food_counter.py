from scale import Scale

IGNORE_ADDED_ABOVE = 1
IGNORE_REMOVED_ABOVE = 1

class FoodCounter:
    def __init__(self, scale: Scale):
        self.ate = 0
        self.__prev_weight = 0

        scale.subscribe_stable(self.__stable)

    def __stable(self, weight: float):
        removed = self.__prev_weight - weight

        if removed < -IGNORE_ADDED_ABOVE:
            print(f"FoodCounter: Ignoring big added weight {-removed:0.2f}g")
        elif removed > IGNORE_REMOVED_ABOVE:
                print(f"FoodCounter: Ignoring big removed weight {removed:0.2f}g")
        else:
            self.ate += removed
            print(f"FoodCounter: Ate {removed:0.2f}g, total = {self.ate:0.2f}g")

        self.__prev_weight=weight

    def reset(self):
        self.ate = 0
