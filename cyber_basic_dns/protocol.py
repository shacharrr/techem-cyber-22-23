import socket
from scapy import *
import simula

class DNSServer:
    def __init__(self):
        self.sdb = simula.Simula("db.local.txt")
