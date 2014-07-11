#!/usr/bin/python
import os, sys, platform, subprocess
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


import docker
c = docker.Client(base_url='unix://var/run/docker.sock',
                  version='1.12',
                  timeout=10)

print c.info()

print c.containers()


class MyHandler(BaseHTTPRequestHandler):

        def do_GET(self):
                try:
                        if self.path.endswith("discoverSystemDetails"):
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                osPlatform = platform.platform().upper()
                                if osPlatform.find("ESX") > 0:
                                        module = __import__('discover_os_info_esx')
                                        self.wfile.write ( module.print_output() )
                                elif osPlatform.find("WINDOWS") >= 0:
                                        module = __import__('discover_os_info_windows')
                                        self.wfile.write ( module.print_output() )
                                elif osPlatform.find("SUNOS") >= 0:
                                        module = __import__('discover_os_info_solaris')
                                        self.wfile.write ( module.print_output() )
                                else:
                                        proc = subprocess.Popen('sudo dmidecode -s system-manufacturer', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                        strOsType = proc.communicate()[0]
                                        if strOsType.find("VMware") >= 0:
                                                module = __import__('discover_os_info_vm')
                                                self.wfile.write ( module.print_output() )
                                        else:
                                                module = __import__('discover_os_info')
                                                self.wfile.write ( module.print_output() )
                                        return
                                return
                        else:
                                self.send_response(404)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                self.wfile.write("Function not supported")
                        return

                except IOError:
                        self.send_error(404,'File Not Found: %s' % self.path)

def main():
        try:
                so = se = open(sys.path[0] + "/../../logs/webserver.log", 'a')
                sys.stdout = so
                sys.stderr = se
                #sys.stdin = si
                server = HTTPServer(('', 12021), MyHandler)
                print 'started httpserver...'
                server.serve_forever()

        except KeyboardInterrupt:
                print '^C received, shutting down server'
                server.socket.close()

if __name__ == '__main__':
        main()


