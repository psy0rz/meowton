import cat
import os
import timer


class Cats():
    def __init__(self, display):

        self.dbdir="catsdb"
        self.current_cat=None
        self.display=display

        self.cats=[]
        try:
            os.mkdir(self.dbdir)
        except:
            pass

        self.min_cat_weight=100

        for name in os.listdir(self.dbdir):
            c=cat.Cat()
            c.load(self.dbdir+"/"+name)
            self.cats.append(c)

            #since we dont have an RTC, just start from this point
            c.state.feed_quota_timestamp=timer.timestamp
            # self.display.update_cat(c)

    def __repr__(self):
        return(self.cats)

    def new(self, name):
        c=self.by_name(name)

        if c:
            raise(Exception("Cat already exists"))

        c=cat.Cat(name)
        self.cats.append(c)
        c.save_file_name(self.dbdir+"/"+name)
 
        self.display.msg("Place {}".format(name))


    def remove(self, name):

        self.cats.remove(self.by_name(name))
        os.remove(self.dbdir+"/"+name)
        self.display.msg("Removed {}".format(name))


    def save(self):
        for cat in self.cats:
            cat.save()


    def by_name(self, name):
        for cat in self.cats:
            if cat.state.name==name:
                return cat

        return(None)

    def get_cat_state(self, name):
        return(self.by_name(name).get_state())

    def update_cat_state(self, state):
        #NOTE: set sane values for now, not configurable via GUI since default here is probably good:
        state['feed_quota_max']=state['feed_daily']
        state['feed_quota_min']=-state['feed_daily']

        cat=self.by_name(state['name'])
        cat.update_state(state)
        cat.save()


    def by_weight(self, weight):

        if weight<self.min_cat_weight:
            return None

        best_match=None
        for c in self.cats:
            #new cat? 
            if c.state.weight==0:
                c.state.weight=weight
                self.display.msg("Learned {}".format(c.state.name))
                return c

            # max +/- 3% difference
            if abs(c.state.weight-weight) < c.state.weight*0.03  and ( not best_match or abs(c.state.weight-weight) < abs(best_match.state.weight-weight)):
                best_match=c

        return(best_match)


    def select_cat(self, cat):
        self.current_cat=cat

    def get_all(self):
        ret=[]
        for cat in self.cats:
            ret.append(cat.get_state())
        
        return(ret)


    def quota_all(self, min=10):
        '''determine if all cats have a quota of at least min'''
        yes=True

        for cat in self.cats:
            if cat.get_quota()<min:
                yes=False

        return(yes)


    def reset_all(self, amount):
        '''reset all food quotas'''
        for cat in self.cats:
            cat.state.feed_quota=amount
