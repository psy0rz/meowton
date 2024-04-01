class SensorFilter:
    def __init__(self, filter_diff):
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
        """filter outliers: if a value is very different from both the last and previous value, filter it."""
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
