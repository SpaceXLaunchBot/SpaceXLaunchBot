import sys

def warning():
    if input("SpaceX-Launch-Bot should not be running whilst this script is run\nContinue? (y/n) >> ").strip().upper() in ["N", "NO"]: sys.exit()
    else:
        return
