# BoneLab Mod.IO Downloader
# By Yernemm
# Version 1.0

import json
import os
import urllib.request
import zipfile

repos = ["https://blrepo.laund.moe/repository.json", "https://blrepo.laund.moe/nsfw_repository.json"];

# Get mod folder path
print("Getting mod folder path...")
modFolder = os.getenv('APPDATA') + "\\..\\LocalLow\\Stress Level Zero\\Bonelab\\Mods"

# Read installedinfo.json
print("Checking previously downloaded mods...")
installed = json.load(open("installedinfo.json"))

# Read modlist.txt
print("Reading mod list...")
modlist = []
with open('modlist.txt') as file:
    for line in file:
        modlist.append(line.strip())

print("Mods in list: " + str(len(modlist)))
#remove duplicates
modlist = list(dict.fromkeys(modlist))
print("Mods in list (no duplicates): " + str(len(modlist)))

allMods = []

# Read repository.json
for repo in repos:
    print("Downloading mod repository...")
    repo = json.load(urllib.request.urlopen(repo))
    print("Repo loaded.")
    print("\"" + repo["objects"]["o:1"]["description"] + "\"")

    mods = repo["objects"]["o:1"]["mods"]

    print("Mods in repo: " + str(len(mods)))

    print("Parsing mods...")


    for i, mod in enumerate(mods):
        modByRef = repo["objects"][str(mod["ref"])]
        
        if("pc" not in modByRef["targets"]):
            continue
        else:
            allMods.append(
                    {
                    "mod": modByRef,
                    "dl": repo["objects"][str(modByRef["targets"]["pc"]["ref"])]
                    }
                )

            print("\r"+str(i + 1)+"/"+str(len(mods)), end="")

    print("")
    #allMods = [*allMods, *mods]

print("Total PC mods: " + str(len(allMods)))

#print(repo["objects"])

#make tmp folder if it doesn't exist
if not os.path.exists(".\\tmp"):
    os.mkdir(".\\tmp")

zipFiles = []

counter = 0
initModListSize = len(modlist)


print("Get all mods from mod list...")
for i, mod in enumerate(allMods):
    if mod["mod"]["barcode"] in modlist:
        counter += 1

        modTitle = mod["mod"]["title"]
        modLink = mod["dl"]["url"]

        print("Downloading " + modTitle + "...")
        
        print(modLink)
        zipFile = ".\\tmp\\" + mod["mod"]["barcode"] + ".zip"
        urllib.request.urlretrieve(modLink, zipFile)
        zipFiles.append(zipFile)
        print(str(counter) + "/" + str(initModListSize) + " downloaded.")
        modlist.remove(mod["mod"]["barcode"])
        #print("Downloaded " + mod["name"] + ".")
        #installed.append(mod["name"])
       # print("\r"+str(i + 1)+"/"+str(len(allMods)), end="")

print("Installing mods...")
for i, zipFile in enumerate(zipFiles):
    print("Installing " + zipFile + "...")
    with zipfile.ZipFile(zipFile, 'r') as zip_ref:
        zip_ref.extractall(modFolder)
    print(str(i + 1) + "/" + str(len(zipFiles)) + " installed.")

# Clean up

print("Cleaning up...")
for zipFile in zipFiles:
    os.remove(zipFile)

print("Done.")


if(len(modlist) > 0):
    print("The following mods were not found:")
    for mod in modlist:
        print(mod)
