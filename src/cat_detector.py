from scale import Scale

import nicegui


class CatDetector:

    def __init__(self, scale: Scale):
        # self.scale = scale
        scale.subscribe_stable(self.scale_stable)
        scale.subscribe_unstable(self.scale_unstable)

    def scale_stable(self, weight: float):
        pass

    def scale_unstable(self):
        pass
