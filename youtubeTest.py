from youtube.youtube_scanner import youtubeScanner

target1 = "alfabusa"
target2 = "AsureLuna"
target3 = "NarrativeDeclaration"
target4 = "PhilipDeFranco"

target = target1

test = youtubeScanner(target)
test.open()
print()
test.scan()
print()
test.display()
print()
"""
test.record() """
print(f"Closing {target}...")
test.aboutDriver.close()
test.videoDriver.close()

print("Done.")