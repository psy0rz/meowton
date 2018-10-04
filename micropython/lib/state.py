import json

class State():
    def __init__(self):
        pass


    def get(self):
        return(self.__dict__)

    def put(self, data):
        self.__dict__=data


    def save(self, file_name):
        with open(file_name,'w') as fh:
            json.dump(self.__dict__, fh)

    def load(self, file_name):
        with open(file_name,'r') as fh:
            d=dict(json.load(fh))
            for (key,value) in d.items():
                setattr(self,key,value)
