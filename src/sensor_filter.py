class SensorFilter:
    """
    class SensorFilter:
        def __init__(self, filter_diff):
            Initializes a SensorFilter object with the specified filter difference.

            Args:
                filter_diff (int): The maximum difference between current and previous values for a value to be considered valid.

            Attributes:
                __last_value (int): The last value received.
                __prev_value (int): The previous value received.
                filter_diff (float): The maximum difference between current and previous values for a value to be considered valid.
                last_difference (float): The difference between the current and previous values of the last received value.
        """
    def __init__(self, filter_diff:int=0):
        self.__last_value=0
        self.__prev_value=0
        self.filter_diff=filter_diff
        self.last_difference=0
        # self.last_ignored_diff=0
        # self.filter_count=0
        # self.total_count=0


    # def reset_stats(self):
    #     self.filter_count=0
    #     self.total_count=0
    #
    # def get_filter_ratio(self):
    #     if self.total_count==0:
    #         return 0
    #     return self.filter_count/self.total_count


    def valid(self, value):
        """
        Checks if a value is valid based on the current and previous values.

        Args:
            value (float): The value to be checked.

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        ok=False
        diff=abs(value-self.__last_value)
        self.last_difference=diff
        if  diff <= self.filter_diff:
            ok=True
        else:
            diff = abs(value - self.__prev_value)
            if diff <= self.filter_diff:
                ok=True


        self.__prev_value=self.__last_value
        self.__last_value=value

        return ok
