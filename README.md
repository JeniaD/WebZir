# Webzir scanner
A basic web scanner designed for reconnaissance.

WebZir simplifies web findings and combines various tools commonly used by pentesters when assessing websites, such as Nikto, Gobuster, and Cewl, to expedite the process. Despite providing combined functionality of multiple tools, WebZir minimizes dependencies to ensure a streamlined and efficient scanning process.

## Usage
```sh
python3 webzir.py example.com
```

## Installation
```sh
git clone https://github.com/JeniaD/WebZir.git
cd WebZir
pip3 install -r requirements.txt
```

## Functionality
```
$ python3 webzir.py -h
WebZir scanner v0.3

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
Initiate a scan with a random user-agent and save the results to the `target/` directory

```sh
$ python3 webzir.py target.com -r --output target
WebZir scanner v0.3

[?] Starting scan against https://target.com (xxx.xxx.x.xx)...

[+] Server: Apache
[+] Interesting findings
robots.txt; .htaccess;
```
