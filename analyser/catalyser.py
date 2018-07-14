class Catalyser():
    '''cat analyser that tries to track the weights of several cats during eating'''

    def __init__(self, callback):

        self.callback=callback

        self.state={}



        #per cat data
        self.state['cats']=[]

        # ignore stuff under this weight
        self.min_cat_weight=2000

        # if cat changes by this much while on scale, invalidate measurement
        # self.on_scale_max_change=100

        pass



    def measurement_event(self, timestamp, weight):
        '''scale() detected a stable measurement. timestamp in ms, weight in grams. '''
        # cat on scale?
        if weight>self.min_cat_weight:
            self.callback(timestamp, self.find_cat(weight), weight)



    def find_cat(self, weight, new=True):
        '''try to find a cat by weight'''

        best_match=None
        for cat in self.state['cats']:
            if abs(cat['weight']-weight)<500:
                if not best_match or abs(cat['weight']-weight)<abs(best_match['weight']-weight):
                    best_match=cat

        if best_match:
            #update moving average and count
            best_match['weight']=int(best_match['weight']*0.9 + weight*0.1)
            best_match['count']=best_match['count']+1

            return(best_match)

        return (None)
        # if new:
        #
        #     #new cat
        #     cat={
        #         'weight': weight,
        #         'name': "Cat "+str(len(self.state['cats'])),
        #         'count': 0
        #     }
        #     self.state['cats'].append(cat)
        #
        #     return(cat)
        # else:
        #     return(None)
