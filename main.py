from patreon.patreon_scanner import patreonScanner
from patreon.exceptions import ParseFailedException

import sys

def scanPatreonTarget(target):
    scanner = patreonScanner(target)
    try:
        scanner.open()
        print()
        scanner.scan()
        print()
        scanner.display()
        print()
        scanner.record()
    except ParseFailedException as e:
        print(e.message)
        print(f"Abandoning Scan of {scanner.target}")

    print(f"Closing {target}...")
    scanner.driver.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Target(s) not specified.\nExitting...")
    else:
        targets = []

        if sys.argv[1] == "-f":
            if len(sys.argv) < 3:
                print("Error: No file name specified.\nExitting...")
                exit(0)

            inputFile = sys.argv[2]

            try:
                with open(inputFile, "r") as f:
                    for line in f:
                        targets.append(line.strip())
            except FileNotFoundError:
                print("Error: Input file not found.\nExitting...")
                exit(0)

        else:
            targets = sys.argv.copy()
            targets.pop(0)

        for target in targets:
            if target == "":
                print("Error: Empty Target! Skipping...")
            else:
                scanPatreonTarget(target)
            print()

        print("Done.")