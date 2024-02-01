import argparse
import os
from core import Core

def main():
    coreModules = Core()
    print(f"WebZir scanner v{coreModules.version}\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="your target URL")
    parser.add_argument("--output", help="output directory path")
    parser.add_argument("-r", "--random-agent", help="use random user agent", action="store_true")
    parser.add_argument("-v", "--verbose", help="use extensive output", action="store_true")
    args = parser.parse_args()

    try:
        coreModules.SetTarget(args.target)
        coreModules.Setup(randomUserAgent=args.random_agent, verbose=args.verbose)

        print(f"[?] Starting scan against {coreModules.targetURL} ({coreModules.targetIP})...\n")
        coreModules.DetectTech()
        coreModules.ScrapeWordlist()

        for finding in coreModules.results:
            if type(coreModules.results[finding]) != list:
                print(f"[+] {finding}: {coreModules.results[finding]}")
            else:
                print(f"[+] {finding}")
                for i in coreModules.results[finding]:
                    print(f"{i}; ", end='')
                print()
        
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

    except RuntimeError as e:
        print("[-] Fatal error:", e)
        print("[?] Exiting...")
        exit(1)
    except KeyboardInterrupt:
        print("\n[-] Keyboard interruption")
        print("[?] Exiting...")
        exit(1)

if __name__ == "__main__": main()
