class State():
    def __init__(self):
        print("moi")
        pass


    def get(self):
        return(self.__dict__)

    def put(self, data):
        self.__dict__=data
