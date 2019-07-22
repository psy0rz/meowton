#!/usr/bin/python3
"""MultiCall mem efficient version"""
__author__ = 'Jan Klopper (jan@underdark.nl)'
__version__ = 0.1
class MultiCall():
  def __init__(self, classes):
    self.classes = classes

  def caller(self, fname, args, kwargs):
    results = []
    for c in self.classes:
      results.append(c.__getattribute__(fname)(*args, **kwargs))
    return results

  def __getattr__(self, fname):
    setattr(self, fname, lambda *args,**kwargs: self.caller(fname, args, kwargs))
    return self.__dict__[fname]

if __name__ == '__main__':
  class A(object):
    def msg(self, string):
      print('A:', string)

  class B(object):
    def msg(self, string):
      print('B:', string)

  m=MultiCall([A(), B()])
  m.msg("hi")
  
