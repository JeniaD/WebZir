try:
    import argparse
except ImportError as e:
    print("[-] Fatal error:", e)
    print("[?] Exiting...")
    exit(1)

from core import Core

def main():
    coreModules = Core()
    print(f"WebZir scanner v{coreModules.version}\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="your target URL (ex. 1.2.3.4 or example.com)")
    parser.add_argument("-r", "--random-agent", help="use random user agent", action="store_true")
    args = parser.parse_args()

    print("[?] Target:", args.target)
    print("[?] Using random user agent:", args.random_agent)
    print()

    try:
        coreModules.SetTarget(args.target)
        coreModules.Setup()

        print(f"[?] Starting scan against {coreModules.target}...")
        coreModules.DetectTech()
    except RuntimeError as e:
        print("[-] Fatal error:", e)
        print("[?] Exiting...")
        exit(1)

if __name__ == "__main__": main()
