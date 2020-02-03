 
 

class Display():
    """base display class. will print messages to stdout. subclass this to use other displays"""

    def __init__(self):
        self._alerting=False
        pass

    def print(self, txt):
        print("display: "+txt)

    def scale_weight_stable(self, weight):
        """called when a stable weight is detected on the cat scale """

        s="Scale {:4.0f}g".format(weight)
        self.print(s)

    def scale_weight_unstable(self):
        """called when cat scale starts moving """
        pass

    def food_weight_stable(self, weight):
        """called when a stable weight is detected on the food scale """
        s="Food {:4.3f}g".format(weight)
        self.print(s)

    def food_weight_unstable(self):
        """called when food scale starts moving """
        pass


    def update_cat(self, cat):
        """called to update info about currently detected cat. called with None if cat has left"""
        if cat:
            self.print("{}: {:4.0f}g (ate {:4.2}g)".format(cat.state.name, cat.state.weight, cat.ate_session))


    def refresh(self):
        """called every second to update/refresh info on screen"""
        pass



    def msg(self, txt, timeout=10):
        """called to display a message on the screen"""
        self.print("Message: "+txt)

    def alert(self, enabled):
        self._alerting=enabled
