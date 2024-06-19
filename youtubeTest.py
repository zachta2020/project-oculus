from youtube.youtube_scanner import youtubeScanner
from selenium.common.exceptions import NoSuchElementException, TimeoutException

targets = [
    "alfabusa", #0
    "AsureLuna", #1
    "NarrativeDeclaration", #2
    "PhilipDeFranco", #3
    "AtrocityGuide", #4
    "ArimuraTaishi12", #5
    "MrBeast", #6
    "ffxiv", #7
    "markiplier", #8
 ]

target = targets[3]

try:
    test = youtubeScanner(target)
    test.open()
    print()
    test.scan()
    print()
    test.display()
    print()
    test.record()
    print(f"Closing {target}...")
    test.close()

    print("Done.")
except NoSuchElementException as e:
    test.driver.save_screenshot("output/NSEEState.png")
    print(e.msg)
    print(e.stacktrace)
    print(e.screen)
except TimeoutException as e:
    test.driver.save_screenshot("output/TimeoutState.png")
    print(e.msg)
    print(e.stacktrace)
    print(e.screen)