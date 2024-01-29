import socket
import requests
import re
import random
import time

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
    except (socket.gaierror, TimeoutError):
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
        self.version = "0.2"
        self.target = target
        self.targetURL = None
        self.targetIP = None

        self.protocol = ""
        self.timeout = 3
        self.port = 0
        self.userAgent = "webzir"
        self.retryAfter = 0

        self.results = {}
        self.debug = False
    
    def SetTarget(self, t):
        self.target = t
    
    def RandomizeUserAgent(self):
        self.userAgent = random.choice(LoadList("userAgents.txt"))
    
    def Setup(self, randomUserAgent=False, verbose=False):
        # Configure target IP and URL
        self.targetIP = ConvertToIP(self.target)
        if not self.targetIP: raise RuntimeError("Host doesn't seem to be reachable")
        self.targetURL = self.target if self.target.startswith("http") else f"https://{self.target}"

        if randomUserAgent: self.RandomizeUserAgent()
        self.debug = verbose

        # https://stackoverflow.com/questions/27324494/is-there-any-timeout-value-for-socket-gethostbynamehostname-in-python
        # socket.setdefaulttimeout(self.timeout)
        # try:
        #     _GLOBAL_DEFAULT_TIMEOUT = socket._GLOBAL_DEFAULT_TIMEOUT
        # except AttributeError:
        #     _GLOBAL_DEFAULT_TIMEOUT = object()

        # Unsure why request takes too much time
        # https://stackoverflow.com/questions/27324494/is-there-any-timeout-value-for-socket-gethostbynamehostname-in-python

    def DetectTech(self):
        if self.debug: print(f"[v] Getting server headers...")
        
        response = requests.head(self.targetURL, allow_redirects=True)
        if response.headers["Server"]: self.results["Server"] = response.headers["Server"]
        
        if self.debug: print(f"[v] Server headers received")
        if self.debug: print(f"[v] Checking for availability of bruteforce enumeration...")

        nonExistentResponse = requests.head(f"{self.targetURL}/{RandomString()}", allow_redirects=True) # Allow redirects?
        if nonExistentResponse.status_code == 429:
            self.retryAfter = int(nonExistentResponse.headers["Retry-after"])/1000 + 1
            if self.debug: print(f"[v] Set up Retry-after ({self.retryAfter})")
        elif nonExistentResponse.status_code != 404:
            raise RuntimeError(f"Response for non-existent URL {self.target}/{RandomString()} responded with {nonExistentResponse}")
    
        if self.debug: print(f"[v] Starting bruteforce...")
        
        for variant in LoadList("basic.txt"):
            if requests.head(f"{self.targetURL}/{variant}", allow_redirects=True).status_code != 404:
                if not "Interesting findings" in self.results: self.results["Interesting findings"] = []
                self.results["Interesting findings"] += [variant]
                if self.debug: print(f"[v] Found {variant} ({requests.head(self.targetURL + '/' + variant).status_code})")
                time.sleep(self.retryAfter)
                # print("[+] Entry found:", variant)
            # else: print("[+] Entry not found:", variant, requests.head(f"http://{self.target}/{variant}").status_code)
        