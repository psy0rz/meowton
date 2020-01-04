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

        for name in os.listdir(self.dbdir):
            c=cat.Cat()
            c.load(self.dbdir+"/"+name)
            self.cats.append(c)

            #since we dont have an RTC, just start from this point
            c.state.feed_quota_timestamp=timer.timestamp
            self.display.update_cat(c)


    def new(self, name):
        c=self.by_name(name)

        if not c:
            c=cat.Cat()
            self.cats.append(c)
            c.save_file_name(self.dbdir+"/"+name)


        c.state.name=name
        c.state.weight=None

        self.display.msg("Place {}".format(name))
        return(c)

    def remove(self, name):

        self.cats.remove(self.by_name(name))
        os.remove(self.dbdir+"/"+name)
        self.display.msg("Removed {}".format(name))
    # for catnr in  range(0, len(self.cats)):
    #         if self.cats[catnr].state.name==name:
    #             self.cats.remove(catnr)



    def save(self):
        for cat in self.cats:
            cat.save()


    def by_name(self, name):
        for cat in self.cats:
            if cat.state.name==name:
                return cat


    def by_weight(self, weight):

        if weight<100:
            return None

        best_match=None
        for c in self.cats:
            #new cat? 
            if c.state.weight==None:
                c.state.weight=weight
                self.display.msg("Learned {}".format(c.state.name))
                return c

            # max 10% difference
            if abs(c.state.weight-weight) < c.state.weight*0.10  and ( not best_match or abs(c.state.weight-weight) < abs(best_match.state.weight-weight)):
                best_match=c

        return(best_match)


    def select_cat(self, cat):
        self.current_cat=cat



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
