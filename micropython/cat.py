class Cat:
    def __init__(self, state):
        self.state=state
        self.state.feed_daily=0
        self.state.feed_quota=0
        self.state.feed_quota_timestamp=0
        self.state.feed_max_quota=0


    def get_quota(self, timestamp):
        '''calculate food quota, depending on time that has passed'''

        if self.state.feed_daily:
            if self.state.feed_quota_timestamp:
                if timestamp>=self.state.feed_quota_timestamp:

                    #prevent rounding errors, smallest increment is one second
                    if timestamp-self.state.feed_quota_timestamp<1000:
                        return

                    # update food quota
                    quota_add=(timestamp-self.state.feed_quota_timestamp)*self.state.feed_daily/(24*3600*1000)

                    self.state.feed_quota=self.state.feed_quota+quota_add

                    if self.state.feed_quota>self.state.feed_quota_max:
                        self.state.feed_quota=self.state.feed_quota_max

        self.state.feed_quota_timestamp=timestamp

        return(self.state.feed_quota)


    def ate(self, weight):
        '''substract amount cat has eaten'''
        self.state.feed_quota=self.state.feed_quota-weight
