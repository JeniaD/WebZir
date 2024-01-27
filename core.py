import socket
import requests
import re
import random

# def CheckConnectivity(ip, port, timeout):
#     try:
#         with socket.create_connection((ip, port), timeout=timeout):
#             return True
#     except (socket.timeout, socket.error, ConnectionRefusedError):
#         return False
#     # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # s.settimeout(timeout)
#     # try:
#     #     s.connect((ip, int(port)))
#     #     s.shutdown(socket.SHUT_RDWR)
#     # except:
#     #     return False
#     # s.close()
#     # return True

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

def IsWebsiteUp(url):
    try:
        response = requests.head(url)
        return True
        # return response.status_code // 100 == 2
    except requests.RequestException as e:
        print(e)
        return False

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
        self.version = "0.0"
        self.target = target
        self.targetURL = target
        self.timeout = 3
        self.port = 0
    
    def SetTarget(self, t):
        self.target = t
        self.targetURL = t
    
    def Setup(self):
        self.target = ConvertToIP(self.target)
        if not self.target: #IsWebsiteUp(self.target):
            raise RuntimeError("Host doesn't seem to be reachable")
        # https = CheckConnectivity(self.target, 443, self.timeout)
        # if https:
        #     self.port = 443
        # else:
        #     http = CheckConnectivity(self.target, 80, self.timeout)
        #     if http: self.port = 80
        #     else: raise RuntimeError("Host doesn't seem to run on http or https")

    def DetectTech(self):
        nonExistentResponse = requests.head(f"http://{self.target}/{RandomString()}")
        if nonExistentResponse.status_code != 404:
            raise RuntimeError(f"Response for non-existent URL {self.target}/{RandomString()} responded with {nonExistentResponse}")
        
        for variant in LoadList("basic.txt"):
            if requests.head(f"http://{self.target}/{variant}").status_code != 404:
                print("[+] Entry found:", variant)
            # else: print("[+] Entry not found:", variant, requests.head(f"http://{self.target}/{variant}").status_code)
        