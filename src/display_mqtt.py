import json

import display_base
from umqtt.robust2 import MQTTClient
import ujson

class Display(display_base.Display):
    """sends data to mqtt server"""

    def __init__(self, settings):

        print("MQTT: starting")

        self.activity_count=0
        self.changed=False
        self.cat=None
        self.settings=settings
        self.state={
            'cat': None,
            'activity': False

        }
        self.msg_timeout=0
        self.mqtt_client=MQTTClient(
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

    def scale_weight_realtime(self, weight):
        if weight>100:
            self.activity_count=self.activity_count+1
        else:
            self.activity_count=0

        if self.activity_count>=3:
            if not self.state['activity']:
                self.state['activity']=True
                self.send()
        else:
            if self.state['activity']:
                self.state['activity']=False
                self.send()



    def scale_weight_stable(self, weight):
        self.state['scale_weight']=round(weight)
        self.state['scale_weight_unstable']=False
        self.send()

    def scale_weight_unstable(self):
        """called when cat scale starts moving """
        self.state['scale_weight_unstable']=True
        self.send()

    def food_weight_stable(self, weight):
        """called when a stable weight is detected on the food scale """
        self.state['food_weight']=round(weight,1)
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
                'name': cat.state.name,
                'weight': round(cat.state.weight),
                'quota': round(cat.get_quota()),
                'wait_time': -round(cat.time()),
                'ate': round(cat.ate_session)
            }
        else:
            self.state['cat']=None

        self.cat=cat

        self.send()

    def refresh(self):
        """called every second to update/refresh info on screen"""
        # we want the status page to update the quota in realtime

        if self.mqtt_client.is_conn_issue():
            print("MQTT: reconnecting")
            self.mqtt_client.reconnect()
            return

        if self.cat:
            self.update_cat(self.cat)

        if self.changed:
            self.mqtt_client.publish(self.settings['topic']+"/event", ujson.dumps(self.state))
            self.changed=False

    def msg(self, txt, timeout=10):
        """called to display a message on the screen"""
        self.state['msg']=txt
        self.send()
