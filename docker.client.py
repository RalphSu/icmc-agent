#!/usr/bin/python
import os, sys, platform, subprocess
import string,cgi,time
from os import curdir, sep
from sysinfo import System, CPU, RAM
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import docker
import psutil

c = docker.Client(base_url='unix://var/run/docker.sock',
                  version='1.12',
                  timeout=10)

sys = System()
cpu = CPU()
ram = RAM()

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if self.path.

            if self.path.endswith("docker/containers"):
                self.wfile.write(_get_containers())
                pass
            elif self.path.endswith("docker/info"):
                self.wfile.write(c.info())
                pass
            elif self.path.endswith("host/cpu"):
                self.wfile.write(self._get_host_cpu())
                pass
            elif self.path.endswith("host/memory"):
                self.wfile.write(self._get_host_memory())
                pass
            elif self.path.endswith("host/network"):
                self.wfile.write(self._get_host_network())
                pass
            elif self.path.endswith("host/info"):
                self.wfile.write(self._get_host_info())
                pass
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write("{ \"msg\" : \"api not supported!\"}")
            return
        except IOError:
	       self.send_error(404,'File Not Found: %s' % self.path)

    def _get_containers(self):
        result = {}
        array_containers = c.containers()
        for c in array_containers:
            cid = c['Id']
            cjson = c.inspect_container(cid)
            result[cid] = cjson
        return result

    def _get_host_cpu(self):
        return cpu.info()

    def _get_host_memory(self):
        return ram.info()

    def _get_host_network(self):
	return psutil.net_io_counters()

    def _get_host_info(self):
        return sys.info()

def main():

    try:
        #so = se = open(sys.path[0] + "/../../logs/icmc-agent.log", 'a')
        #sys.stdout = so
        #sys.stderr = se
        #sys.stdin = si
        server = HTTPServer(('', 21000), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
        main()
