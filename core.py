import socket
import requests
import re
import random
import time
from bs4 import BeautifulSoup

# Wordlists
IMPORTANTENTRIES = "basic.txt" # Something should be checked to identify server
USERAGENTS = "userAgents.txt" # List of user-agents

# Values
MAXREQWAIT = 5

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
        self.version = "0.4"
        self.target = target
        self.targetURL = None
        self.targetIP = None

        self.protocol = "http"
        self.timeout = 3
        self.port = 0
        self.userAgent = "webzir/" + self.version
        self.retryAfter = 0

        self.results = {}
        self.wordlist = []
        self.wayback = []

        self.debug = False
    
    def SetTarget(self, t):
        self.target = t
    
    def RandomizeUserAgent(self):
        self.userAgent = random.choice(LoadList(USERAGENTS))
    
    def Setup(self, randomUserAgent=False, verbose=False):
        # Configure target IP and URL
        self.targetIP = ConvertToIP(self.target)
        if not self.targetIP: raise RuntimeError("Host doesn't seem to be reachable")
        self.targetURL = self.target if self.target.startswith("http") else f"{self.protocol}://{self.target}"

        if randomUserAgent: self.RandomizeUserAgent()
        self.debug = verbose

    def DetectTech(self):
        if self.debug: print(f"[v] Getting server headers...")
        
        response = requests.head(self.targetURL, headers={"User-Agent": self.userAgent}, allow_redirects=True)
        if response.headers["Server"]: self.results["Server"] = response.headers["Server"]
        
        if self.debug: print(f"[v] Server headers received")
        if self.debug: print(f"[v] Checking for availability of bruteforce enumeration...")

        nonExistentResponse = requests.head(f"{self.targetURL}/{RandomString()}", headers={"User-Agent": self.userAgent}, allow_redirects=True) # Allow redirects?
        if nonExistentResponse.status_code == 429:
            self.retryAfter = min(MAXREQWAIT, int(nonExistentResponse.headers["Retry-after"])/1000 + 1)
            if self.debug: print(f"[v] Set up Retry-after ({self.retryAfter})")
        elif nonExistentResponse.status_code != 404:
            raise RuntimeError(f"Response for non-existent URL {self.target}/{RandomString()} responded with {nonExistentResponse}")
    
        if nonExistentResponse.status_code in [429, 404]: # redirect?
            if self.debug: print(f"[v] Starting bruteforce...")
            
            for variant in LoadList(IMPORTANTENTRIES):
                req = requests.head(f"{self.targetURL}/{variant}", headers={"User-Agent": self.userAgent}, allow_redirects=True)
                if req.status_code != 404:
                    if not "Interesting findings" in self.results: self.results["Interesting findings"] = []
                    self.results["Interesting findings"] += [f"{variant} ({req.status_code})"]
                    if self.debug: print(f"[v] Found {variant} ({req.status_code})")
                time.sleep(self.retryAfter)

    def ScrapeWordlist(self):
        req = requests.get(self.targetURL, headers={"User-Agent": self.userAgent}, allow_redirects=True)
        soup = BeautifulSoup(req.content, "html.parser")
        text = soup.find_all(text=True)
        text = ' '.join(text)
        text = text.replace('\n', ' ')
        while "  " in text: text = text.replace("  ", ' ')
        self.wordlist = list(dict.fromkeys([word for word in text.split(' ') if word and len(word) < 10 and len(word) > 1]))

    def Wayback(self):
        if self.debug: print(f"[v] Searching in Wayback machine...")
        target = self.target.replace("http://", '').replace("https://", '') # Clear protocol
        portal = f"http://web.archive.org/cdx/search/cdx?url=*.{target}/*&output=json&fl=original&collapse=urlkey"

        req = requests.get(portal, headers={"User-Agent": self.userAgent})
        result = []
        
        for v in req.json()[1:]:
            if type(v) == list:
                result += v
            else: result += [v]

        result = list(dict.fromkeys(result))

        if result: self.wayback = result #self.results["Wayback"] = result