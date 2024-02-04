import argparse
import os
from core import Core
import colorama
from colorama import Fore, Style

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

    parser = argparse.ArgumentParser(description=f"WebZir scanner v{coreModules.version}")
    parser.add_argument("target", help="your target URL")
    parser.add_argument("--output", help="output directory path")
    parser.add_argument("-r", "--random-agent", help="use random user agent", action="store_true")
    parser.add_argument("-v", "--verbose", help="use extensive output", action="store_true")
    args = parser.parse_args()

    try:
        coreModules.SetTarget(args.target)
        coreModules.Setup(randomUserAgent=args.random_agent, verbose=args.verbose)

        Log(f"Starting scan against {coreModules.targetURL} ({coreModules.targetIP})...", status='?')
        print()

        coreModules.DetectTech()
        coreModules.ScrapeWordlist()
        coreModules.Wayback()

        for finding in coreModules.results:
            if type(coreModules.results[finding]) != list:
                Log(f"{finding}: {coreModules.results[finding]}", status='+')
            else:
                Log(f"{finding}", status='+')
                print("    ", end='')
                for i in coreModules.results[finding]:
                    print(f"{i}; ", end='')
                print()
        
        if coreModules.wayback: Log(f"Found {len(coreModules.wayback)} link(s) in Wayback machine", status='+')
        
        if args.output:
            if args.verbose: print("[?] Saving data to the files...")
            if not os.path.exists(args.output): os.makedirs(args.output)
            with open(f"{args.output}/report.txt", 'w') as file:
                file.write(f"WebZir scanner v{coreModules.version}\nScan report for the host {coreModules.targetURL} ({coreModules.targetIP})\n\n")

                for finding in coreModules.results:
                    if type(coreModules.results[finding]) != list:
                        file.write(f"[+] {finding}: {coreModules.results[finding]}\n")
                    else:
                        file.write(f"[+] {finding}\n")
                        for i in coreModules.results[finding]: file.write(f"{i}; ")
                        file.write('\n')
            with open(f"{args.output}/dictionary.txt", 'w') as file:
                for element in coreModules.wordlist: file.write(element + '\n')
            if coreModules.wayback:
                with open(f"{args.output}/wayback.txt", 'w') as file:
                    for element in coreModules.wayback: file.write(element + '\n')

    except RuntimeError as e:
        Log(f"Fatal error: {e}", status='-')
        Log("Exiting...", status='?')
        exit(1)
    except KeyboardInterrupt:
        print()
        Log("Keyboard interruption", status='-')
        Log("Exiting...", status='?')
        exit(1)

if __name__ == "__main__": main()
