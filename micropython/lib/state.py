import json

class State():
    def __init__(self):
        pass


    def get(self):
        return(self.__dict__)

    def put(self, data):
        self.__dict__=data


    def save(self, file_name):
        with open('w',file_name) as fh:
            json.dump(self.__dict__, fh)

    def load(self, file_name):
        with open('r',file_name) as fh:
            self.__dict__=json.load(fp)
