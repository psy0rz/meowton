class SensorFilter:
    def __init__(self, max_diff):
        self.__last_value=0
        self.__prev_value=0
        self.__max_diff=max_diff


    def valid(self, value):
        """filter outliers: if a value is very different from both the last and previous value, filter it."""
        ok=False
        if abs(value-self.__last_value) <= self.__max_diff:
            ok=True

        if abs(value-self.__prev_value) <= self.__max_diff:
            ok=True

        self.__prev_value=self.__last_value
        self.__last_value=value

        return ok
