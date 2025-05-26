import sys

dev_mode = "dev" in sys.argv
if dev_mode:
    print("Using dev mode")
headless = "headless" in sys.argv
if headless:
    print("Running in headless mode")


version="2.0"

