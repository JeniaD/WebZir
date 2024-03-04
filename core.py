import socket
import requests
import re
import random
import time
from bs4 import BeautifulSoup

# Global values
IMPORTANTENTRIES = "common.txt" # Wordlist for something that should be checked to identify server
IMPORTANTHEADERS = "OWASP_dangerousHeaders.txt" # Wordlist for headers that should be checked
USERAGENTS = "userAgents.txt" # List of random user-agents
MAXREQWAIT = 3 # Max wait time between requests
DEFAULTPROTOCOL = "http"

# Convert target URL to IP address
def ConvertToIP(url):
    try:
        # Check if the address starts with 'http://' or 'https://'
        match = re.match(r'(https?://)?(.*?)(/)?$', url)
        protocolPrefix, domain, _ = match.groups()

        # If no protocol specified, default to 'http'
        if not protocolPrefix: protocolPrefix = DEFAULTPROTOCOL + "://"

        # Resolve to IPv4 address
        IP = socket.gethostbyname(domain)
        
        return IP # return f"{protocolPrefix}{IP}"
    except (socket.gaierror, TimeoutError):
        return None

# Generate random string
def RandomString():
    res = ""
    chars = "1234567890qwertyuiopasdfghjklzxcvbnm"
    for i in range(random.randint(5, 15)):
        res += random.choice(chars)
    
    return res

# Load wordlist by name
def LoadList(name):
    with open(f"wordlists/{name}", 'r') as file:
        return file.read().split('\n')

class Target:
    def __init__(self, raw=None, url=None, ip=None, protocol=None, timeout=0):
        self.raw = raw
        self.URL = url
        self.IP = ip
        self.protocol = protocol
        self.timeout = timeout
    
    def Setup(self, target, protocol=DEFAULTPROTOCOL):
        self.protocol = protocol
        self.raw = target
        self.IP = ConvertToIP(self.raw)
        if not self.IP: raise RuntimeError("Host doesn't seem to be reachable")
        self.URL = target if target.startswith("http") else f"{protocol}://{target}"

class Core:
    def __init__(self, target="127.0.0.1") -> None:
        self.version = "0.6"
        self.userAgent = "webzir/" + self.version

        self.target = Target()

        self.results = {}
        self.wordlist = []
        self.wayback = []

        self.debug = False
    
    def SetTarget(self, t):
        self.target.Setup(t)
    
    def RandomizeUserAgent(self):
        self.userAgent = random.choice(LoadList(USERAGENTS))
    
    def Setup(self, randomUserAgent=False, verbose=False):
        if randomUserAgent: self.RandomizeUserAgent()
        self.debug = verbose

    def DetectTech(self):
        if self.debug: print(f"[v] Getting server headers...")
        
        response = requests.head(self.target.URL, headers={"User-Agent": self.userAgent}, allow_redirects=True)
        for header in response.headers:
            if header in LoadList(IMPORTANTHEADERS):
                self.results[header] = response.headers[header] # WARNING: dangerous, might be overwritten
        
        if self.debug: print(f"[v] Server headers received")
        if self.debug: print(f"[v] Checking for availability of bruteforce enumeration...")

        nonExistentResponse = requests.head(f"{self.target.URL}/{RandomString()}", headers={"User-Agent": self.userAgent}, allow_redirects=True)
        if nonExistentResponse.status_code == 429:
            self.target.timeout = min(MAXREQWAIT, int(nonExistentResponse.headers["Retry-after"])/1000 + 1)
            if self.debug: print(f"[v] Set up Retry-after ({self.target.timeout})")
        elif nonExistentResponse.status_code != 404:
            raise RuntimeError(f"Response for non-existent URL {self.target}/{RandomString()} responded with {nonExistentResponse}")
    
        if nonExistentResponse.status_code in [429, 404]:
            if self.debug: print(f"[v] Starting bruteforce...")
            
            for variant in LoadList(IMPORTANTENTRIES):
                req = requests.head(f"{self.target.URL}/{variant}", headers={"User-Agent": self.userAgent}, allow_redirects=True)
                if req.status_code != 404:
                    if not "Interesting findings" in self.results: self.results["Interesting findings"] = []
                    self.results["Interesting findings"] += [f"{variant} ({req.status_code})"]
                    if self.debug: print(f"[v] Found {variant} ({req.status_code})")
                time.sleep(self.target.timeout)

    def ScrapeWordlist(self):
        req = requests.get(self.target.URL, headers={"User-Agent": self.userAgent}, allow_redirects=True)
        soup = BeautifulSoup(req.content, "html.parser")
        text = soup.find_all(text=True)
        text = ' '.join(text)
        text = text.replace('\n', ' ')
        while "  " in text: text = text.replace("  ", ' ') # Perhaps remove spaces entirely?
        self.wordlist = list(dict.fromkeys([word for word in text.split(' ') if word and len(word) < 10 and len(word) > 1]))

    def Wayback(self):
        if self.debug: print(f"[v] Searching in Wayback machine...")
        target = self.target.raw.replace("http://", '').replace("https://", '') # Clear protocol
        portal = f"http://web.archive.org/cdx/search/cdx?url=*.{target}/*&output=json&fl=original&collapse=urlkey"

        req = requests.get(portal, headers={"User-Agent": self.userAgent})
        result = []
        
        for v in req.json()[1:]:
            if type(v) == list:
                result += v
            else: result += [v]

        result = list(dict.fromkeys(result))

        if result: self.wayback = result