from patreon.scanner import patreonScanner
from common.exceptions import ParseFailedException
from youtube.scanner import youtubeScanner
from twitch.scanner import TwitchScanner

from selenium.common.exceptions import ElementNotInteractableException

from argparse import ArgumentParser, SUPPRESS

modes = {
    "patreon" : "Patreon",
    "youtube" : "YouTube",
    "twitch" : "Twitch",
    }

def scanTarget(target, mode):
    scanner = None
    if mode == "patreon":
        scanner = patreonScanner(target)
    elif mode == "youtube":
        scanner = youtubeScanner(target)
    elif mode == "twitch":
        scanner = TwitchScanner(target)
    try:
        scanner.run()
        print()
        scanner.display()
        print()
        scanner.record()
    except ParseFailedException as e:
        print(e.message)
        print(f"Abandoning Scan of {scanner.target}")

    print(f"Closing {target}...")
    scanner.close()

parser = ArgumentParser(
    prog="cmdline",
    description="""
        Scrapes information of target user(s) from a specified social media or content creator focused website.
        Avaiable websites: Patreon, Youtube
    """,
    argument_default=SUPPRESS
)
parser.add_argument("mode", help="sets the target website from the list available")

userTargetGroup = parser.add_mutually_exclusive_group(required=True)
userTargetGroup.add_argument("-t", "--targets", nargs="+", help="<Required> sets target user(s) to be scraped")
userTargetGroup.add_argument("-f", "--file", help="<Required> reads target user(s) from specified file")

args = parser.parse_args()
mode = args.mode.lower()

if mode in modes:
    currentMode = modes[mode]
    print(f"Mode: {currentMode} selected.\n")

    targets = []

    try: #if file was specified
        file = args.file
        try:
            with open(file, "r") as f:
                for line in f:
                    targets.append(line.strip())
        except FileNotFoundError:
            print("Error: Input file not found.\nExiting...")
            exit(0)
    except AttributeError: #if targets were directly inputted on cmdline
        targets = args.targets
    
    for target in targets:
            if target == "":
                print("Error: Empty Target! Skipping...")
            else:
                scanTarget(target, mode)
            print()

else:
    print("ERROR: INVALID MODE SELECTED")

print("Done.")