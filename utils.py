# coding=utf-8
from __future__ import print_function

import datetime
import sys
import time
from threading import Thread


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


def indent_block(s, n=1, indent='  ', border='| '):
    padding = indent * n
    border = border or ''
    if not n:
        border = ''
    if border:
        padding = padding
    return '\n'.join(padding + border + i for i in s.splitlines())


def parse_puttime(t):
    return datetime.datetime.strptime(t.replace('T', ' '), '%Y-%m-%d %H:%M:%S.%f')


def shorten_time(t):
    return parse_puttime(t).strftime('%H:%M:%S.%f').rstrip('0')
