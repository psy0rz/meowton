#(C)2019 edwin@datux.nl - Released under GPL.

class MultiCall():
    """This class calls all methods in multiple other class objects.
    (all classes should have the same methods and arguments)

    e.g.:
     m=MultiCall([A(), B()])

     m.msg("hi")

     will result in a call to A.msg("hi") and B.msg("hi")

    """

    def __init__(self, classes):

        for fname in dir(classes[0]):
            methods=[]
            for cls in classes:
                methods.append(getattr(cls, fname))
                setattr(self, fname, lambda *args,**kwargs: self.call_all(methods, args, kwargs))

    def call_all(self, methods, args, kwargs):
        for method in methods:
            method(*args, **kwargs)
