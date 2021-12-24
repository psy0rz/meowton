import json

import display_base
import umqtt.simple
import ujson

class Display(display_base.Display):
    """sends data to mqtt server"""

    def __init__(self, settings):

        print("MQTT: starting")

        self.changed=False
        self.cat=None
        self.settings=settings
        self.state={
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
        self.mqtt_client=umqtt.simple.MQTTClient(
            settings['client_id'],
            settings['server'],
            settings['port'],
            settings['user'],
            settings['password'],
        )

        self.mqtt_client.set_last_will(self.settings['topic']+"/status", "offline")
        self.mqtt_client.connect()
        self.mqtt_client.publish(self.settings['topic']+"/status", "online")
        

    def send(self):
        self.changed=True


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

        if self.changed:
            self.mqtt_client.publish(self.settings['topic']+"/event", ujson.dumps(self.state))
            self.changed=False

    def msg(self, txt, timeout=10):
        """called to display a message on the screen"""
        self.state['msg']=txt
        self.send()
