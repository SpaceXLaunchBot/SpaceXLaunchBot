"""
A Python3 script to help when installing this bot on a new / clean server
"""
from os import path
import sys

def replacePlaceholderInFiles(filePathList, placeHolder, replaceWith):
    for path in filePathList:
        with open(path, "r") as fin:
            body = fin.read()
        with open(path, "w") as fout:
            fout.write(body.replace(placeHolder, replaceWith))

"""
Each array contains the paths to files that need said values replacing
"""
discordTokenFiles = [path.join("services", "systemd", "SLB.service")]
dblTokenFiles = [path.join("services", "systemd", "SLB.service")]

# Get variables
discordToken = input("Input your Discord token\n>> ").strip()
dblToken = input("Input your Discord bot list token\n>> ").strip()

print(f"""
Using:
discord token : {discordToken[0:10]}...{discordToken[-10:]}
dbl token     : {dblToken[0:10]}...{dblToken[-10:]}
""")

if input("Is this correct? y/n ").strip().lower() == "n":
    sys.exit()

print("\nCopying variables to associated files")

replacePlaceholderInFiles(
    discordTokenFiles,
    "DISCORD-TOKEN",
    discordToken
)
replacePlaceholderInFiles(
    dblTokenFiles,
    "DBL-TOKEN",
    dblToken
)

print("\nDone")
