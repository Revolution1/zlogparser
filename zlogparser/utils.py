# coding=utf-8
from __future__ import print_function

import datetime
import sys
import time
from collections import namedtuple, OrderedDict
from functools import wraps
from threading import Thread, Lock

if sys.version_info[0] < 3:
    PY2 = True
    PY3 = False
else:
    PY2 = False
    PY3 = True

_CacheInfo = namedtuple("CacheInfo", "hits misses maxsize currsize")


def lru_cache(maxsize=100):
    """Least-recently-used cache decorator.
    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.
    Arguments to the cached function must be hashable.
    View the cache statistics named tuple (hits, misses, maxsize, currsize) with
    f.cache_info().  Clear the cache and statistics with f.cache_clear().
    Access the underlying function with f.__wrapped__.
    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used
    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    def decorating_function(user_function):
        hits, misses = [0], [0]
        kwd_mark = (object(),)  # separates positional and keyword args
        lock = Lock()  # needed because OrderedDict isn't threadsafe

        if maxsize is None:
            cache = dict()  # simple cache without ordering or size limit

            @wraps(user_function)
            def wrapper(*args, **kwds):
                key = args
                if kwds:
                    key += kwd_mark + tuple(sorted(kwds.items()))
                try:
                    result = cache[key]
                    hits[0] += 1
                    return result
                except KeyError:
                    pass
                result = user_function(*args, **kwds)
                cache[key] = result
                misses[0] += 1
                return result
        else:
            cache = OrderedDict()  # ordered least recent to most recent
            cache_popitem = cache.popitem

            @wraps(user_function)
            def wrapper(*args, **kwds):
                key = args
                if kwds:
                    key += kwd_mark + tuple(sorted(kwds.items()))
                with lock:
                    try:
                        result = cache[key]
                        cache[key] = cache.pop(key)  # record recent use of this key
                        hits[0] += 1
                        return result
                    except KeyError:
                        pass
                result = user_function(*args, **kwds)
                with lock:
                    cache[key] = result  # record recent use of this key
                    misses[0] += 1
                    if len(cache) > maxsize:
                        cache_popitem(0)  # purge least recently used cache entry
                return result

        def cache_info():
            """Report cache statistics"""
            with lock:
                return _CacheInfo(hits[0], misses[0], maxsize, len(cache))

        def cache_clear():
            """Clear the cache and cache statistics"""
            with lock:
                cache.clear()
                hits[0] = misses[0] = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper

    return decorating_function


class cached_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class SpinnerStyle():
    Box1 = u'⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    Box2 = u'⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓'
    Box3 = u'⠄⠆⠇⠋⠙⠸⠰⠠⠰⠸⠙⠋⠇⠆'
    Box4 = u'⠋⠙⠚⠒⠂⠂⠒⠲⠴⠦⠖⠒⠐⠐⠒⠓⠋'
    Box5 = u'⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠴⠲⠒⠂⠂⠒⠚⠙⠉⠁'
    Box6 = u'⠈⠉⠋⠓⠒⠐⠐⠒⠖⠦⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈'
    Box7 = u'⠁⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈⠈'
    Spin1 = u'|/-\\'
    Spin2 = u'◴◷◶◵'
    Spin3 = u'◰◳◲◱'
    Spin4 = u'◐◓◑◒'
    Spin5 = u'▉▊▋▌▍▎▏▎▍▌▋▊▉'
    Spin6 = u'▌▄▐▀'
    Spin7 = u'╫╪'
    Spin8 = u'■□▪▫'
    Spin9 = u'←↑→↓'
    Default = Box1


class Spinner(object):
    def __init__(self, message, style=SpinnerStyle.Default, end=''):
        self.message = message
        self.frames = style
        self.length = len(style)
        self.position = 0
        self.running = False
        self.thread = None
        self.end = end

    def current(self):
        return self.frames[self.position]

    def next(self):
        current_frame = self.current()
        self.position = (self.position + 1) % self.length
        # return six.text_type(current_frame)
        return current_frame

    def reset(self):
        self.position = 0

    def start(self):
        def spin():
            while self.running:
                print('\r' + self.message + ' ' + self.next(), end=' ')
                sys.stdout.flush()
                time.sleep(0.1)
            print('\r' + self.message, end=' ')
            print(self.end, end="")
            sys.stdout.flush()

        self.running = True
        self.thread = Thread(target=spin)
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def indent_block(s, n=1, indent='    ', border='| '):
    padding = indent * n
    border = border or ''
    if not n:
        border = ''
    if border:
        padding = padding
    return u'\n'.join(padding + border + i for i in s.splitlines())


def parse_puttime(t):
    return datetime.datetime.strptime(t.replace('T', ' '), '%Y-%m-%d %H:%M:%S.%f')


def shorten_time(t):
    return parse_puttime(t).strftime('%H:%M:%S.%f').rstrip('0')


def levenshtein(seq1, seq2, limit=None):
    """
    the Levenshtein edit distance between two strings.
    """
    # oneago = None
    thisrow = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        oneago, thisrow = thisrow, [0] * len(seq2) + [x + 1]
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)

        if limit and x > limit and min(thisrow) > limit:
            return limit + 1

    return thisrow[len(seq2) - 1]
