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
DEFAULTPROTOCOL = "http" # Default protocol
DEFAULTPORT = 80 # Default port

# Convert target URL to IP address
def ConvertToIP(url):
    try:
        # Check if the address starts with 'http://' or 'https://'
        match = re.match(r'(https?://)?(.*?)(/)?$', url)
        protocolPrefix, domain, _ = match.groups()

        # Resolve to IPv4 address
        IP = socket.gethostbyname(domain)
        
        return IP
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
    def __init__(self, hostname=None, ip=None, protocol=DEFAULTPROTOCOL, port=None, path="", timeout=0):
        self.hostname = hostname
        self.IP = ip
        self.protocol = protocol
        self.port = port
        self.path = path
        self.timeout = timeout
    
    def GetFullURL(self):
        if self.port: port = self.port
        else: port = 443 if self.protocol == "https" else 80
        return f"{self.protocol}://{self.hostname}:{port}/{self.path}"
    
    def Parse(self, target):
        if target.startswith("https"): self.protocol = "https"
        elif target.startswith("http"): self.protocol = "http"
        else: self.protocol = DEFAULTPROTOCOL

        target = target.replace("https://", '').replace("http://", '')

        # target = target.replace("//", '/').replace("::", ':')
        buff = target.split('/', 1)[0]
        
        if ":" in buff:
            self.port = int(buff.split(':')[1])
            self.hostname = buff.split(':')[0]
        else:
            self.port = None # DEFAULTPORT
            self.hostname = buff
        
        buff = target.split('/', 1)
        if len(buff) > 1: self.path = buff[1]
        # if self.path and self.path[-1] != '/': self.path += '/'
    
    def Setup(self):
        self.IP = ConvertToIP(self.hostname)
        if not self.IP: raise RuntimeError("Host doesn't seem to be reachable")
        # requests.head(self.GetFullURL())

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
        self.target.Parse(t)
        self.target.Setup()
    
    def RandomizeUserAgent(self):
        self.userAgent = random.choice(LoadList(USERAGENTS))
    
    def Setup(self, randomUserAgent=False, verbose=False):
        if randomUserAgent: self.RandomizeUserAgent()
        self.debug = verbose

    def DetectTech(self):
        if self.debug: print(f"[v] Getting server headers...")
        
        response = requests.head(self.target.GetFullURL(), headers={"User-Agent": self.userAgent}, allow_redirects=True)
        for header in response.headers:
            if header in LoadList(IMPORTANTHEADERS):
                self.results[header] = response.headers[header] # WARNING: dangerous, might be overwritten
        
        if self.debug: print(f"[v] Server headers received")
        if self.debug: print(f"[v] Checking for availability of bruteforce enumeration...")

        nonExistentResponse = requests.head(f"{self.target.GetFullURL()}/{RandomString()}", headers={"User-Agent": self.userAgent}, allow_redirects=True)
        if nonExistentResponse.status_code == 429:
            self.target.timeout = min(MAXREQWAIT, int(nonExistentResponse.headers["Retry-after"])/1000 + 1)
            if self.debug: print(f"[v] Set up Retry-after ({self.target.timeout})")
        elif nonExistentResponse.status_code != 404:
            raise RuntimeError(f"Response for non-existent URL {self.target}/{RandomString()} responded with {nonExistentResponse}")
    
        if nonExistentResponse.status_code in [429, 404]:
            if self.debug: print(f"[v] Starting bruteforce...")
            
            for variant in LoadList(IMPORTANTENTRIES):
                req = requests.head(f"{self.target.GetFullURL()}/{variant}", headers={"User-Agent": self.userAgent}, allow_redirects=True)
                if req.status_code != 404:
                    if not "Interesting findings" in self.results: self.results["Interesting findings"] = []
                    self.results["Interesting findings"] += [f"{variant} ({req.status_code})"]
                    if self.debug: print(f"[v] Found {variant} ({req.status_code})")
                time.sleep(self.target.timeout)

    def ScrapeWordlist(self):
        req = requests.get(self.target.GetFullURL(), headers={"User-Agent": self.userAgent}, allow_redirects=True)
        soup = BeautifulSoup(req.content, "html.parser")
        text = soup.find_all(text=True)
        text = ' '.join(text)
        text = text.replace('\n', ' ')
        while "  " in text: text = text.replace("  ", ' ') # Perhaps remove spaces entirely?
        self.wordlist = list(dict.fromkeys([word for word in text.split(' ') if word and len(word) < 10 and len(word) > 1]))

    def Wayback(self):
        if self.debug: print(f"[v] Searching in Wayback machine...")
        portal = f"http://web.archive.org/cdx/search/cdx?url=*.{self.target.hostname}/*&output=json&fl=original&collapse=urlkey"

        req = requests.get(portal, headers={"User-Agent": self.userAgent})
        result = []
        
        for v in req.json()[1:]:
            if type(v) == list:
                result += v
            else: result += [v]

        result = list(dict.fromkeys(result))

        if result: self.wayback = result