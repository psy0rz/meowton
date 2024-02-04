#(C)2019 edwin@datux.nl - Released under GPL.

import json

class StateItems():

    def __repr__(self):
        return(repr(self.__dict__))




class State():
    '''subclass from this class is you want persistant state. self.state can be saved/loaded'''
    def __init__(self, file_name=None):
        self.state=StateItems()

        if file_name:
            self.load(file_name)

    # def __getstate__(self):
    #     return(self.state)
    #
    # def __setstate__(self, state):
    #     self.state=state

    def __repr__(self):
        return(self._state_file_name+": "+repr(self.state.__dict__))

    def save_file_name(self, file_name):
        self._state_file_name=file_name

    def save(self, file_name=None):
        if file_name:
            self._state_file_name=file_name

        if self._state_file_name:
            with open(self._state_file_name,'w') as fh:
                json.dump(self.state.__dict__, fh)

    def load(self, file_name=None):
        if file_name:
            self._state_file_name=file_name

        with open(self._state_file_name,'r') as fh:
            d=dict(json.load(fh))
            for (key,value) in d.items():
                setattr(self.state,key,value)

    def get_state(self):
        """get state as normal dict"""
        return(self.state.__dict__)
    
    def update_state(self, d):
        """update state from a normal dict """
        for (key,value) in d.items():
            setattr(self.state,key,value)
