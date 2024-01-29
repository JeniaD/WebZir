import argparse
from core import Core

def main():
    coreModules = Core()
    print(f"WebZir scanner v{coreModules.version}\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="your target URL")
    parser.add_argument("-r", "--random-agent", help="use random user agent", action="store_true")
    parser.add_argument("-v", "--verbose", help="use extensive output", action="store_true")
    args = parser.parse_args()

    try:
        coreModules.SetTarget(args.target)
        coreModules.Setup(randomUserAgent=args.random_agent, verbose=args.verbose)

        print(f"[?] Starting scan against {coreModules.targetURL} ({coreModules.targetIP})...\n")
        coreModules.DetectTech()
        for finding in coreModules.results:
            if type(coreModules.results[finding]) != list:
                print(f"[+] {finding}: {coreModules.results[finding]}")
            else:
                print(f"[+] {finding}")
                for i in coreModules.results[finding]:
                    print(f"{i}; ", end='')
                print()

    except RuntimeError as e:
        print("[-] Fatal error:", e)
        print("[?] Exiting...")
        exit(1)
    except KeyboardInterrupt:
        print("\n[-] Keyboard interruption")
        print("[?] Exiting...")
        exit(1)

if __name__ == "__main__": main()
