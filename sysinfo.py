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
    PROC_USAGE = '/proc/stat'
    PROCESSOR = 'processor\t:'
    INFO_KEY = ['model name', 'vendor_id', 'cpu mhz']

    def __init__(self):
        self.cpufile=open(self.PROC_CPU).read()

    def count(self):
        return self.cpufile.count(self.PROCESSOR)

    def usage(self):
    	''' TODO: use a backgroud thread periodically read stat file, calcualte based on comparison'''
        statfile = open(self.PROC_USAGE)
        # convert to dict
	current = []
        for line in statfile:
            parts = re.split('\s+', line)
	    if parts[0] == "cpu" :
	        current = map(long, list(parts[1:len(parts) -1]))
	        break
	print current
	if len(current) > 0 :
	    idle = current[3]
	    total = sum(current)
    	    return 100 * float(total - idle) / float(total)
	else :
	    return "calculate error!"

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

class Network(object):
    def __init__():
        params['refresh_rate']=10
        params['target_device']='eth0'
        self.device=params['target_device']
        self.workThread = UpdateTrafficThread(params)

    def info(self):
        result = {}
        key = 'recv_bytes_' + self.device
        result[key] = self.workThread.metric_of(key)
        key = 'recv_pkts_'+self.device
        result[key] = self.workThread.metric_of(key)
        key = 'recv_errs_' + self.device
        result[key] = self.workThread.metric_of(key)
        key = 'trans_bytes_' + self.device
        result[key] = self.workThread.metric_of(key)
        key = 'trans_pkts_' + self.device
        result[key] = self.workThread.metric_of(key)
        key = 'trans_errs_' +self.device
        result[key] = self.workThread.metric_of(key)
        return result

_Lock = threading.Lock() # synchronization lock
def dprint(f, *v):
    pass

class UpdateTrafficThread(threading.Thread):

    __slots__ = ( 'proc_file' )

    def __init__(self, params):
        threading.Thread.__init__(self)
        self.running       = False
        self.shuttingdown  = False
        self.refresh_rate = 10
        if "refresh_rate" in params:
            self.refresh_rate = int(params["refresh_rate"])

        self.target_device = params["target_device"]
        self.metric       = {}

        self.proc_file = "/proc/net/dev"
        self.stats_tab = {
            "recv_bytes"  : 0,
            "recv_pkts"   : 1,
            "recv_errs"   : 2,
            "recv_drops"  : 3,
            "trans_bytes" : 8,
            "trans_pkts"  : 9,
            "trans_errs"  : 10,
            "trans_drops" : 11,
            }
        self.stats      = {}
        self.stats_prev = {}

    def shutdown(self):
        self.shuttingdown = True
        if not self.running:
            return
        self.join()

    def run(self):
        self.running = True

        while not self.shuttingdown:
            _Lock.acquire()
            self.update_metric()
            _Lock.release()
            time.sleep(self.refresh_rate)

        self.running = False

    def update_metric(self):
        f = open(self.proc_file, "r")
        for l in f:
            a = l.split(":")
            dev = a[0].lstrip()
            if dev != self.target_device: continue

            dprint("%s", ">>update_metric")
            self.stats = {}
            _stats = a[1].split()
            for name, index in self.stats_tab.iteritems():
                self.stats[name+'_'+self.target_device] = int(_stats[index])
            self.stats["time"] = time.time()
            dprint("%s", self.stats)

            if "time" in self.stats_prev:
                dprint("%s: %d = %d - %d", "DO DIFF", self.stats["time"]-self.stats_prev["time"], self.stats["time"], self.stats_prev["time"])
                d = self.stats["time"] - self.stats_prev["time"]
                for name, cur in self.stats.iteritems():
                    self.metric[name] = float(cur - self.stats_prev[name])/d

            self.stats_prev = self.stats.copy()
            break

        return

    def metric_of(self, name):
        val = 0
        if name in self.metric:
            _Lock.acquire()
            val = self.metric[name]
            _Lock.release()
        return val



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

