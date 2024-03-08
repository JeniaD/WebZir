# Webzir scanner
A basic web scanner designed for reconnaissance.

WebZir simplifies web findings and combines features of various tools commonly used by pentesters when assessing websites, such as Nikto, Gobuster, and Cewl. Despite providing combined functionality of multiple tools, WebZir minimizes dependencies to ensure a quick scanning process and easy installation.

## Usage
```
python3 webzir.py target.com
```

## Installation
```
git clone https://github.com/JeniaD/WebZir.git
cd WebZir
pip3 install -r requirements.txt
```

## Functionality
```
$ python3 webzir.py -h

usage: webzir.py [-h] [--output OUTPUT] [-r] [-v] target

positional arguments:
  target              your target URL

optional arguments:
  -h, --help          show this help message and exit
  --output OUTPUT     output directory path
  -r, --random-agent  use random user agent
  -v, --verbose       use extensive output
```

## Example
Initiate a scan with a random user-agent and save the results to the `./results` directory

```
$ python3 webzir.py target.com -r --output results
 __      __      ___.   __________.__        
/  \    /  \ ____\_ |__ \____    /|__|______ 
\   \/\/   // __ \| __ \  /     / |  \_  __ \
 \        /\  ___/| \_\ \/     /_ |  ||  | \/
  \__/\  /  \___  >___  /_______ \|__||__|   
       \/       \/    \/        \/ v0.x

[?] Initiating a security scan for http://target.com:80/ (xxx.xx.xxx.xx)...

[+] Server: Apache/2.4.56 (Debian)
[+] Interesting findings
    robots.txt (200); humans.txt (200); sitemap.xml (200); dashboard (403); 
[+] Found 1 link(s) in Wayback machine

[?] Time elapsed: 12.1s
```
