# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 17:23:42 2015

@author: chema
"""

from __future__ import print_function

from collections import Iterable
from functools import partial
from itertools import tee
from abc import abstractmethod

###
### Monad abstract class
###
class Monad(Iterable):
    
    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        """
            Overrided abstract method for the iterable protocol
        """
        self.iterable, it = tee(self.iterable) # cloned iterables
        return it
    
    def andThen(self, m, *args):
        """
            Equivalent to the haskell's method >>=
            (Monad m) => m a -> (a -> m b) -> m b
        """
        if callable(m):
            return Monad(b for a in self for b in m(a, *args))
        else:
            return Monad(b for a in self for b in m)
    
    def followedBy(self, mb):
        """
            equivalent to the haskell's method >>
            (Monad m) => m a -> m b -> m b
        """
        return Monad(b for a in self for b in mb)
    
    def do(self, *fs):
        """
            equivalent to the haskell's "do"
        """
        m = self
        for f in fs:
#            if isinstance(f, Monad):
#                m = m.followedBy(f)
#            else:
            args = f if isinstance(f, tuple) else (f,)
            m = m.andThen(*args)
        return m

    def run(self):
        list(self)
    
    def map(self, f):
        return Monad(f(i) for i in self)

    def __repr__(self):
        name = self.__class__.__name__
        return "{}({})".format(name, ",".join(repr(i) for i in self))



# (Monad m) => [m a] -> m [a]
def sequence(ms):
    return Monad(i for m in ms for i in m)

# (Monad m) => (a -> m b) -> [a] -> m [b]
def mapM(f, xs):
    return sequence(f(i) for i in xs)


 
   
###
### Maybe Monad 
###
class Maybe(Monad):
    def __init__(self, *values):
        self.values = values
        super(Maybe, self).__init__(iter(values))

class Nothing(Maybe):
    pass

class Just(Maybe):
    def __init__(self, value):
        self.value = value
        super(Just, self).__init__(value)

###
### List Monad
###
class ListM(Monad):
    def __init__(self, lst):
        self.lst = lst
        super(ListM, self).__init__(iter(lst))

###
### IO Monad
###
class IO(Monad):
    
    def __init__(self, a, *args):
        self(a,*args)
        super(IO,self).__init__(Just(a))

    @abstractmethod
    def __call__(self, a, *args):
        pass

class PrintM(IO):
    def __init__(self, a, *args, **kw):
        self.fmt=kw.get("fmt","{0}")
        super(PrintM,self).__init__(a,*args)
    def __call__(self, a, *args):
        print(self.fmt.format(a, *args))
        return Just(a)
        

###
### sample functions
###

def multn(n, x):
    return Just(x*n)

mult2 = partial(multn, 2)

def sumn(n, x):
    return Just(x+n)

sum10 = partial(sumn, 10)

def filtern(n, x):
    return Nothing() if x==n else Just(x)

def printM(x,*args):
    print(x,*args)
    return Just(x)


### PLAYING...

p=PrintM("Hello, world!").do()
print(p)


for i in Just(1).andThen(mult2).andThen(sum10).andThen(partial(multn,11)):
    print(i)

m = ListM([1,2,3]).andThen(mult2).andThen(sum10)
for i in m:
    print(i)
for i in m:
    print(i)

m2 = mapM(mult2, m)
print(m2)

filter28 = partial(filtern, 28)

m3 = mapM(filter28, m2)
print(m3)

l = ListM(Just(i) for i in m3)
print(l)

l = ListM([Just(1), Nothing(), Just(2)])
print(l)

#m4 = mapM(mult2, l)
#print(m4)

print
print(l)
print(sequence(l))

l = ListM([1,2,3,4,5])
print(l.map(sum10))
print(l.map(mult2))


m = Just(1).do(
    mult2,
    sum10,
    (multn, 11),
    printM,
    (sumn, -12123),
    mult2,
    PrintM(fmt="{0} <- Negative number")
   )
print(m)


p=ListM(range(3)).followedBy(PrintM("Hello, world!")).followedBy(ListM([1,2,3]))
print(p)

ListM(range(2)).do(
    (PrintM,"Hello, world!"),
    ListM([1,2,3]),
    PrintM
    ).run()
