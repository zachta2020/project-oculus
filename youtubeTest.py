from youtube.youtube_scanner import youtubeScanner

targets = [
    "alfabusa", #0
    "AsureLuna", #1
    "NarrativeDeclaration", #2
    "PhilipDeFranco", #3
    "AtrocityGuide", #4
    "ArimuraTaishi12", #5
    "MrBeast", #6
    "ffxiv", #7
 ]

target = targets[0]

test = youtubeScanner(target)
test.open()
""" print()
test.scan()
print()
test.display()
print()
test.record() """
print(f"Closing {target}...")
test.close()

print("Done.")