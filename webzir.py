import argparse
import os
import time
import datetime
import requests
import colorama
from colorama import Fore, Style
from core import Core

def Log(msg, status='?'):
    color = Fore.CYAN
    if status == '+': color = Fore.GREEN
    elif status == '-': color = Fore.RED

    print(f"[{color}{status}{Style.RESET_ALL}] {msg}")

def PrintName(v):
    print(''' __      __      ___.   __________.__        
/  \    /  \ ____\_ |__ \____    /|__|______ 
\   \/\/   // __ \| __ \  /     / |  \_  __ \\
 \        /\  ___/| \_\ \/     /_ |  ||  | \/
  \__/\  /  \___  >___  /_______ \|__||__|   
       \/       \/    \/        \/''' + f" {Fore.GREEN}v{v}{Style.RESET_ALL}\n")

def main():
    coreModules = Core()
    colorama.init(autoreset=True)
    colorama.ansi.clear_screen()
    PrintName(coreModules.version)

    parser = argparse.ArgumentParser(description=f"Lightweight web scanner for quick recon")
    parser.add_argument("target", help="your target URL")
    parser.add_argument("--output", help="output directory path")
    parser.add_argument("-r", "--random-agent", help="use random user agent", action="store_true")
    parser.add_argument("-v", "--verbose", help="use extensive output", action="store_true")
    parser.add_argument("-f", "--noRedirect", help="don't allow redirect when bruteforcing entries (faster)", action="store_true")
    parser.add_argument("-i", metavar="IGNORE_CODES", help="ignore status codes when bruteforcing", default="404")
    args = parser.parse_args()

    startScanTime = time.time()
    try:
        coreModules.SetTarget(args.target)
        coreModules.Setup(randomUserAgent=args.random_agent, verbose=args.verbose, allowRedirect=not args.noRedirect, excludeCodes=args.i)

        if coreModules.target.IP == coreModules.target.hostname:
            Log(f"Initiating a security scan for {coreModules.target.GetFullURL()}...", status='?')
        else:
            Log(f"Initiating a security scan for {coreModules.target.GetFullURL()} ({coreModules.target.IP})...", status='?')
        print()

        coreModules.DetectTech()
        coreModules.ScrapeWordlist()
        coreModules.Wayback()
        coreModules.Whois()
    except (RuntimeError, requests.exceptions.ConnectionError) as e:
        Log(f"Fatal error: {e}", status='-')
        Log("Exiting...", status='?')
        exit(1)
    except KeyboardInterrupt:
        print()
        Log("Keyboard interruption", status='-')
    
    totalScanTime = round(time.time() - startScanTime, 2)
    
    for finding in coreModules.results:
        if type(coreModules.results[finding]) == list:
            Log(f"{finding}", status='+')
            print("    ", end='')
            for i in coreModules.results[finding]:
                print(f"{i}; ", end='')
            print()
        elif type(coreModules.results[finding]) == dict:
            Log(f"{finding}", status='+')
            for elem in coreModules.results[finding]:
                print(f"    {elem}: {coreModules.results[finding][elem]}")
        else:
            Log(f"{finding}: {coreModules.results[finding]}", status='+')
    
    if coreModules.wayback: Log(f"Found {len(coreModules.wayback)} link(s) in Wayback machine", status='+')

    print()
    Log(f"Time elapsed: {totalScanTime}s", status='?')
    
    if args.output:
        if args.verbose: print("[?] Writing data to the files...")
        if not os.path.exists(args.output): os.makedirs(args.output)
        with open(f"{args.output}/report.txt", 'w') as file:
            file.write(f"WebZir scanner v{coreModules.version}\nScan report for the host {coreModules.target.GetFullURL()} ({coreModules.target.IP}) ")
            file.write(f"{datetime.datetime.now()}\n\n")

            for finding in coreModules.results:
                if type(coreModules.results[finding]) == list:
                    file.write(f"[+] {finding}\n")
                    for i in coreModules.results[finding]: file.write(f"{i}; ")
                    file.write('\n')
                elif type(coreModules.results[finding]) == dict:
                    file.write(f"[+] {finding}\n")
                    for elem in coreModules.results[finding]: file.write(f"    {elem}: {coreModules.results[finding][elem]}\n")
                else:
                    file.write(f"[+] {finding}: {coreModules.results[finding]}\n")

        with open(f"{args.output}/dictionary.txt", 'w') as file:
            for element in coreModules.wordlist: file.write(element + '\n')
        if coreModules.wayback:
            with open(f"{args.output}/wayback.txt", 'w') as file:
                for element in coreModules.wayback: file.write(element + '\n')

if __name__ == "__main__": main()
