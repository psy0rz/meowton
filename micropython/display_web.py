

class DisplayWeb():
    """merely collects data that you want the webserver to send to the browser"""

    def __init__(self):
        self.state={
            'v': 0
        }


    def send(self):
        self.state['v']=self.state['v']+1

    def scale_weight_stable(self, weight):
        self.state['scale_weight']=weight
        self.state['scale_weight_unstable']=False
        self.send()

    def scale_weight_unstable(self):
        """called when cat scale starts moving """
        self.state['scale_weight_unstable']=True
        self.send()

    def food_weight_stable(self, weight):
        """called when a stable weight is detected on the food scale """
        self.state['food_weight']=weight
        self.state['food_weight_unstable']=False
        self.send()

    def food_weight_unstable(self):
        """called when food scale starts moving """
        self.state['food_weight_unstable']=True
        self.send()


    def update_cat(self, cat):
        """called to update info about currently detected cat. called with None if cat has left"""
        pass
        # if cat:
        #     self.print("{}: {:4.0f}g (ate {:4.2}g)".format(cat.state.name, cat.state.weight, cat.ate_session))


    def refresh(self):
        """called every second to update/refresh info on screen"""
        pass



    def msg(self, txt, timeout=10):
        """called to display a message on the screen"""
        # self.print("Message: "+txt)
        pass
