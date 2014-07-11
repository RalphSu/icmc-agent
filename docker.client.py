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
