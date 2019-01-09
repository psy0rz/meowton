

class Display():
    """base display class. will print messages to stdout. subclass this to use other displays"""

    def __init__(self):
        self.print("Display init")

    def print(self, txt):
        print("DISPLAY: "+txt)

    def scale_weight_stable(self, weight):

        s="Scale {:4.0f}g".format(weight)
        self.print(s)

    def scale_weight_unstable(self):
        pass

    def food_weight_stable(self, weight):
        s="Food {:4.0f}g".format(weight)
        self.print(s)

    def food_weight_unstable(self):
        pass


    def update_cat(self, cat):
        if cat:
            self.print("{}: {:4.0f}g (ate {:4.2}g)".format(cat.state.name, cat.state.weight, cat.ate_session))


    def refresh(self):
        pass



    def msg(self, txt, timeout=10):
        self.print("Message: "+txt)
