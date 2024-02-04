 
 

class Display():
    """base display class. will print messages to stdout. subclass this to use other displays"""

    def __init__(self):
        self._alerting=False
        pass

    def scale_weight_realtime(self, weight):
        """called on every measurement"""
        pass

    def scale_weight_stable(self, weight):
        """called when a stable weight is detected on the cat scale """
        pass

    def scale_weight_unstable(self):
        """called when cat scale starts moving """
        pass

    def food_weight_stable(self, weight):
        """called when a stable weight is detected on the food scale """
        pass

    def food_weight_unstable(self):
        """called when food scale starts moving """
        pass


    def update_cat(self, cat):
        """called to update info about currently detected cat. called with None if cat has left"""
        pass


    def refresh(self):
        """called every second to update/refresh info on screen"""
        pass

    def msg(self, txt):
        """called to display a message on the screen"""
        pass

    def alert(self, enabled):
        """called to change alerting status"""
        self._alerting=enabled
