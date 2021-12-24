import display_base


class Display(display_base.Display):
    """base display class. will print messages to stdout. subclass this to use other displays"""

    def __init__(self):
        self._alerting=False
        self.cat=None
        pass

    def print(self, txt):
        print("display: "+txt)

    def scale_weight_stable(self, weight):
        """called when a stable weight is detected on the cat scale """

        s="Scale {:4.0f}g".format(weight)
        self.print(s)

    def scale_weight_unstable(self):
        """called when cat scale starts moving """
        self.print("Scale unstable")

    def food_weight_stable(self, weight):
        """called when a stable weight is detected on the food scale """
        s="Food {:4.3f}g".format(weight)
        self.print(s)

    def food_weight_unstable(self):
        """called when food scale starts moving """
        self.print("Food unstable")

    def update_cat(self, cat):
        """called to update info about currently detected cat. called with None if cat has left"""
        if cat!=self.cat:
            if cat:
                self.print("{}: {:4.0f}g (ate {:4.2}g)".format(cat.state.name, cat.state.weight, cat.ate_session))
            else:
                self.print("cat left")

    def msg(self, txt, timeout=10):
        """called to display a message on the screen"""
        self.print("Message: "+txt)

    def refresh(self):
        if self._alerting:
            self.print("ALERT")

