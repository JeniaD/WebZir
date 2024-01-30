# Webzir scanner
Basic web scanner for recon

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
WebZir scanner v0.2

usage: webzir.py [-h] [-r] [-v] target

positional arguments:
  target              your target URL

optional arguments:
  -h, --help          show this help message and exit
  -r, --random-agent  use random user agent
  -v, --verbose       use extensive output
```

## Example
```
$ python3 webzir.py target.com -r
WebZir scanner v0.x

[?] Starting scan against https://target.com (xxx.xxx.x.xx)...

[+] Server: Apache
[+] Interesting findings
robots.txt; .htaccess;
```