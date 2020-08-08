from state import State
import timer

class Cat(State):
    def __init__(self, name=None):
        super().__init__()
        self.state.name=name
        self.state.feed_daily=0
        self.state.feed_quota=0
        self.state.feed_quota_timestamp=timer.timestamp
        self.state.feed_quota_max=0
        self.state.feed_quota_min=0
        self.state.weight=0

        #aten during this feeding session (usually ends when cat leaves and uploaded to database)
        self.ate_session=0


    def get_quota(self):
        '''calculate food quota, depending on time that has passed'''
 
        if self.state.feed_daily:
            diff=timer.diff(timer.timestamp,self.state.feed_quota_timestamp)

            #Minimum update time difference. dont make too small to prevent rounding and processing overhead

            #I tested rouding errors like this:
            # >>> q=0
            # >>> for i in range(0,24*3600):  q=q+((900+random.random()*200)*30/(24*3600*1000))
            # ... 
            # >>> q
            # 30.01269
            if diff>1000:

                # update food quota
                quota_add=diff*self.state.feed_daily/(24*3600*1000)

                self.state.feed_quota=self.state.feed_quota+quota_add

                if self.state.feed_quota>self.state.feed_quota_max:
                    self.state.feed_quota=self.state.feed_quota_max

                if self.state.feed_quota<self.state.feed_quota_min:
                    self.state.feed_quota=self.state.feed_quota_min

                self.state.feed_quota_timestamp=timer.timestamp

        return(self.state.feed_quota)


    def time(self):
        '''time in minutes that the current quota took to build, or will take to reach 0 again, in minutes (negative in that case)'''

        if self.state.feed_daily:
            quota=self.get_quota()
            return(quota/(self.state.feed_daily/(24*60)))

        return 0


    def ate(self, weight):
        '''substract amount cat has eaten'''
        self.state.feed_quota=self.state.feed_quota-weight
        self.ate_session=self.ate_session+weight


    def update_weight(self, weight):
        '''update weight by moving average'''
        self.state.weight=self.state.weight*0.99 + weight*0.01
