import cat
import os


class Cats():
    def __init__(self, display):

        self.dbdir="catsdb"
        self.current_cat=None

        self.cats=[]
        try:
            os.mkdir(self.dbdir)
        except:
            pass

        for name in os.listdir(self.dbdir):
            c=cat.Cat()
            c.load(self.dbdir+"/"+name)
            self.cats.append(c)


    def new_cat(self, name):
        c=self.by_name(name)

        if not c:
            c=cat.Cat()
            self.cats.append(c)


        c.state.name=name
        c.save(self.dbdir+"/"+name)
        return(c)


    def by_name(self, name):
        for cat in self.cats:
            if cat.state.name==name:
                return cat


    def by_weight(self, weight):

        best_match=None
        for c in self.cats:
            #new cat?
            if c.state.weight==None:
                c.state.weight=weight
                return c

            if not best_match or abs(cat.state.weight-weight)<abs(best_match.state.weight-weight):
                best_match=cat

        return(best_match)


    def detected_cat(self, cat):
        if self.current_cat:
            self.current_cat.gone()

        self.current_cat=cat
        cat.detected()
