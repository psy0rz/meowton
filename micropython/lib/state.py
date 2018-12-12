import json

class StateItems():
    pass


class State():
    '''subclass from this class is you want persistant state. self.state will be pickled'''
    def __init__(self):
        self.state=StateItems()

    # def __getstate__(self):
    #     return(self.state)
    #
    # def __setstate__(self, state):
    #     self.state=state


    def save(self, file_name=None):
        if file_name:
            self._state_file_name=file_name

        with open(self._state_file_name,'w') as fh:
            json.dump(self.state.__dict__, fh)

    def load(self, file_name=None):
        if file_name:
            self._state_file_name=file_name


        with open(self._state_file_name,'r') as fh:
            d=dict(json.load(fh))
            for (key,value) in d.items():
                setattr(self.state,key,value)
