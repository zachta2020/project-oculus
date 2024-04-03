from patreon.patreon_scanner import patreonScanner
from patreon.exceptions import parseFailedException

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
    except parseFailedException as e:
        print(e.message)
        print(f"Abandoning Scan of {scanner.target}")

    print(f"Closing {target}...")
    scanner.driver.close()

if len(sys.argv) < 2:
    print("Error: Target(s) not specified.")
    print("Quitting...")
else:
    targets = []

    if sys.argv[1] == "-f":
        inputFile = sys.argv[2]

        with open(inputFile, "r") as f:
            for line in f:
                targets.append(line.strip())

    else:
        targets = sys.argv.copy()
        targets.pop(0)

    for target in targets:
        scanPatreonTarget(target)
        print()


    print("Done.")