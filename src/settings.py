import sys

dev_mode = "dev" in sys.argv[1]
if dev_mode:
    print("Using dev mode")
headless = "headless" in sys.argv[1]
if headless:
    print("Running in headless mode")

feed_times = [9, 13, 17, 21, 1]



