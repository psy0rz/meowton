import display_base

class Display(display_base.Display):
    """merely collects data that you want the webserver to send to the browser"""

    def __init__(self):
        self.cat=None
        self.state={
            'v': 0,
            'cat': {
                'status': 'Eating',
                'name': '',
                'weight': 0,
                'ate_session': 0,
                'quota': 0,
                'time': 0
            }
        }
        self.msg_timeout=0
        

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

        if cat:
            self.state['cat']={
                'status': 'Eating',
                'name': cat.state.name,
                'weight': cat.state.weight,
                'ate_session': cat.ate_session,
                'quota': cat.get_quota(),
                'time': cat.time()
            }
            self.cat=cat

        else:
            self.state['cat']['status']='Done'

        self.send()

    def refresh(self):
        """called every second to update/refresh info on screen"""
        # we want the status page to update the quota in realtime
        if self.cat:
            self.update_cat(self.cat)
        pass

    def msg(self, txt, timeout=10):
        """called to display a message on the screen"""
        self.state['msg']=txt
        self.send()
