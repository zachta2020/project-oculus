from patreon.patreon_scanner import patreonScanner
from patreon.exceptions import parseFailedException

testScanner = patreonScanner("alfabusa")
try:
    testScanner.open()
    print()
    testScanner.scan()
    print()
    testScanner.display()
    print()
    testScanner.record()
except parseFailedException as e:
    print(e.message)
    print(f"Abandoning Scan of {testScanner.target}")

testScanner.driver.close()
print("Done.")