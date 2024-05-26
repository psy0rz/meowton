import sys

dev_mode = "dev" in sys.argv
if dev_mode:
    print("Using dev mode")
headless = "headless" in sys.argv
if headless:
    print("Running in headless mode")

feed_times = [9, 13, 17, 21, 1]

version="2.0"

