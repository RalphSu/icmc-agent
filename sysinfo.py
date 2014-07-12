#!/usr/bin/python

import os
import re
import platform
from datetime import timedelta

class System(object):
    PROC_UPTIME = '/proc/uptime'
    PROC_LOAD = '/proc/loadavg'

    def info(self):
        return platform.architecture()[:0] + platform.uname()[:5]

    def uptime(self):
        if os.path.exists(self.PROC_UPTIME):
            uptime = open(self.PROC_UPTIME).read().split()
            return timedelta(seconds=float(uptime[0]))

    def load(self):
        ''' tuple of usage in (last minute, last 5mins, last 10min) '''
        if os.path.exists(self.PROC_LOAD) :
            load = open(self.PROC_LOAD).read().split()
            return (float(load[0]), float(load[1]), float(load[2]))

class RAM(object):
    PROC_MEM = '/proc/meminfo'
    INFO_KEY = ['memtotal', 'memfree']

    def info(self, brief=True):
        ''' kb based data'''
        mf = open(self.PROC_MEM)
        meminfos = {}
        for line in mf:
            array = line.split(':')
            # check
            key = array[0].lower()
            if self._check(brief, key) :
                meminfos[key] = int(array[1].lstrip().replace(' kB', ''))
        return meminfos

    def _check(self, brief, key):
        if brief :
            return key in self.INFO_KEY
        else:
            return True


class CPU(object):
    PROC_CPU = '/proc/cpuinfo'
    PROCESSOR = 'processor\t:'
    INFO_KEY = ['model name', 'vendor_id', 'cpu mhz']

    def __init__(self):
        self.cpufile=open(self.PROC_CPU).read()

    def count(self):
        return self.cpufile.count(self.PROCESSOR)

    def info(self, brief=True):
        """
        Converts PROC_CPU into a dict
        """
        cpus = self.count()

        infs = [x.split(': ') for x in self.cpufile.replace('\t', '').split('\n')][:-2]
        inf_list = []
        i = -1
        for inf in infs:
            if inf[0] != '':
                if inf[0] == "processor":
                    inf_list.append({})
                    i += 1

                key = inf[0].lower().lstrip()
                if self._check(brief, key):
                    inf_list[i][key] = inf[1] if len(inf) > 1 else ""
            else:
                continue
        return inf_list

    def _check(self, brief, key):
        if brief :
            return key in self.INFO_KEY
        else:
            return True

def test():
    sys = System()
    print '::sys info:'
    print sys.info()
    
    print '::sys uptime '
    print sys.uptime()
    print '::sys load'
    print sys.load()

    cpu = CPU()
    print '::cpu count' 
    print cpu.count()
    print '::cpu info' 
    print cpu.info()
    ram = RAM()
    print '::mem info'
    print ram.info()
if __name__ == '__main__':
        test()

