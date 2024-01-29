import socket
import requests
import re
import random

def ConvertToIP(url):
    try:
        # Check if the address starts with 'http://' or 'https://'
        match = re.match(r'(https?://)?(.*?)(/)?$', url)
        protocol_prefix, domain, _ = match.groups()

        if not protocol_prefix:
            # If no protocol specified, default to 'http'
            protocol_prefix = 'http://'

        # Resolve to IPv4 address
        IP = socket.gethostbyname(domain)
        
        return IP # return f"{protocol_prefix}{ip_address}"
    except socket.gaierror as e:
        # print(f"Error resolving {domain}: {e}")
        return None

def RandomString():
    res = ""
    chars = "1234567890qwertyuiopasdfghjklzxcvbnm"
    for i in range(random.randint(5, 15)):
        res += random.choice(chars)
    
    return res

def LoadList(name):
    with open(f"wordlists/{name}", 'r') as file:
        return file.read().split('\n')

class Core:
    def __init__(self, target="127.0.0.1") -> None:
        self.version = "0.1"
        self.target = target
        self.targetURL = None
        self.targetIP = None

        self.protocol = ""
        self.timeout = 3
        self.port = 0
        self.userAgent = "webzir"
    
    def SetTarget(self, t):
        self.target = t
    
    def RandomizeUserAgent(self):
        self.userAgent = random.choice(LoadList("userAgents.txt"))
    
    def Setup(self, randomUserAgent=False):
        # Configure target IP and URL
        self.targetIP = ConvertToIP(self.target)
        if not self.targetIP: raise RuntimeError("Host doesn't seem to be reachable")
        self.targetURL = self.target if self.target.startswith("http") else f"https://{self.target}"

        if randomUserAgent: self.RandomizeUserAgent()

    def DetectTech(self):
        nonExistentResponse = requests.head(f"{self.targetURL}/{RandomString()}")
        if nonExistentResponse.status_code != 404:
            raise RuntimeError(f"Response for non-existent URL {self.target}/{RandomString()} responded with {nonExistentResponse}")
        
        for variant in LoadList("basic.txt"):
            if requests.head(f"{self.targetURL}/{variant}").status_code != 404:
                print("[+] Entry found:", variant)
            # else: print("[+] Entry not found:", variant, requests.head(f"http://{self.target}/{variant}").status_code)
        