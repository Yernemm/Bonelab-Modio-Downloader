# BoneLab Mod.IO Downloader
# By Yernemm
# Version 1.2

import json
import os
import urllib.request
import zipfile

repos = ["https://blrepo.laund.moe/repository.json", "https://blrepo.laund.moe/nsfw_repository.json"];

# Get mod folder path
print("Getting mod folder path...")
modFolder = os.getenv('APPDATA') + "\\..\\LocalLow\\Stress Level Zero\\Bonelab\\Mods"

print("Getting mod info file...")
modInfoPath = os.getenv('APPDATA') + "\\..\\LocalLow\\Stress Level Zero\\Bonelab\\yernemm_modio_downloader.json"
#create file if it doesn't exist
if not os.path.exists(modInfoPath):
    print("Creating mod info file...")
    with open(modInfoPath, 'w') as file:
        file.write('{"version": "1.2", "installed": []}')
        file.close()

modInfo = json.load(open(modInfoPath))

# Read installedinfo.json
#print("Checking previously downloaded mods...")
#installed = json.load(open("installedinfo.json"))

# Read modlist.txt
print("Reading mod list...")
modlist = []
with open('modlist.txt') as file:
    for line in file:
        modlist.append(line.strip())

notFoundList = []

print("Mods in list: " + str(len(modlist)))
#remove duplicates
modlist = list(dict.fromkeys(modlist))
print("Mods in list (no duplicates): " + str(len(modlist)))

def main():
    print("===========================")
    print("BoneLab Mod.IO Downloader by Yernemm")
    print("Choose an option:")
    mode = -1
    while mode < 0 or mode > 3:
        print("   1. Update existing list mods and install new ones")
        print("   2. Install all mods from list")
        print("   3. Generate mod list from installed mods")
        print("   0. Exit")
        try:
            mode = int(input("Option: "))
        except:
            print("Invalid input.")

    print(" ")

    if mode == 1:
        mode1()
    elif mode == 2:
        mode2()
    elif mode == 3:
        mode3()
    
        
    print("Done.")



def mode1():
    print("Update existing list mods and install new ones")
    allMods = getRepoMods()
    purgeUpdatedMods(allMods)
    zipFiles = downloadMods(allMods)
    installMods(zipFiles)
    saveInfo()
    cleanUp(zipFiles)
    checkNotFound()

def mode2():
    print("Install all mods from list")
    allMods = getRepoMods()
    zipFiles = downloadMods(allMods)
    installMods(zipFiles)
    cleanUp(zipFiles)
    checkNotFound()

def mode3():
    print("Generate mod list from installed mods")
    generateModList(modFolder)


def getRepoMods():
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
    return allMods

#print(repo["objects"])

def purgeUpdatedMods(allMods):
    global modlist
    print("Purging up-to-date mods from list...")
    for i, mod in enumerate(allMods):
        if mod["mod"]["barcode"] in modlist:
            #check if mod is installed
            barcode = mod["mod"]["barcode"]
            url = mod["dl"]["url"]
            if checkIfUpdated(barcode, url):
                print("Mod " + barcode + " is up-to-date.")
                modlist.remove(barcode)
    
                


def downloadMods(allMods):
    global modlist
    global notFoundList
    #make tmp folder if it doesn't exist
    if not os.path.exists(".\\tmp"):
        os.mkdir(".\\tmp")

    zipFiles = []

    counter = 0
    initModListSize = len(modlist)


    print("Downloading mods...")
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

            addInstalledMods(mod["mod"]["barcode"], modLink)
            #print("Downloaded " + mod["name"] + ".")
            #installed.append(mod["name"])
        # print("\r"+str(i + 1)+"/"+str(len(allMods)), end="")
    notFoundList = modlist
    modlist = []
    return zipFiles

def installMods(zipFiles):
    print("Installing mods...")
    for i, zipFile in enumerate(zipFiles):
        print("Installing " + zipFile + "...")
        with zipfile.ZipFile(zipFile, 'r') as zip_ref:
            zip_ref.extractall(modFolder)
        print(str(i + 1) + "/" + str(len(zipFiles)) + " installed.")

# Clean up

def cleanUp(zipFiles):
    print("Cleaning up...")
    for zipFile in zipFiles:
        os.remove(zipFile)


def checkNotFound():
    if(len(notFoundList) > 0):
        print("The following mods were not found:")
        for mod in notFoundList:
            print("   " + mod)
 
def saveInfo():
    global modInfo
    global modInfoPath
    print("Logging installed mods...")
    with open(modInfoPath, 'w') as file:
        json.dump(modInfo, file, indent=4)
        file.close()

def addInstalledMods(barcode, url):
    global modInfo
    modInfo["installed"].append({"barcode": barcode, "url": url})
    saveInfo()

def checkIfUpdated(barcode, url):
    global modInfo
    for mod in modInfo["installed"]:
        if mod["barcode"] == barcode:
            if mod["url"] == url:
                return True
            else:
                return False
    return False

def generateModList(path):
    #loop through all folders in path
    #if folder contains a pallet.json, open it
    #get the barcode and add it to the list

    newList = ""

    #get all folders in path
    folders = os.listdir(path)
    for folder in folders:
        #check if folder contains a pallet.json
        if os.path.exists(path + "\\" + folder + "\\pallet.json"):
            #open pallet.json
            with open(path + "\\" + folder + "\\pallet.json") as file:
                pallet = json.load(file)
                file.close()
            #get barcode
            barcode = pallet["objects"]["o:1"]["barcode"]
            #add barcode to list
            newList += barcode + "\n"
            print(barcode)
    
    #save list to file
    with open("generated-modlist.txt", "w") as file:
        file.write(newList)
        file.close()
    print("--------------------")
    print("Saved to generated-modlist.txt")

main()