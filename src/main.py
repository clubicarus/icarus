"""
██▓ ▄████▄   ▄▄▄       ██▀███   █    ██   ██████ 
▓██▒▒██▀ ▀█  ▒████▄    ▓██ ▒ ██▒ ██  ▓██▒▒██    ▒ 
▒██▒▒▓█    ▄ ▒██  ▀█▄  ▓██ ░▄█ ▒▓██  ▒██░░ ▓██▄   
░██░▒▓▓▄ ▄██▒░██▄▄▄▄██ ▒██▀▀█▄  ▓▓█  ░██░  ▒   ██▒
░██░▒ ▓███▀ ░ ▓█   ▓██▒░██▓ ▒██▒▒▒█████▓ ▒██████▒▒
░▓  ░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
 ▒ ░  ░  ▒     ▒   ▒▒ ░  ░▒ ░ ▒░░░▒░ ░ ░ ░ ░▒  ░ ░
 ▒ ░░          ░   ▒     ░░   ░  ░░░ ░ ░ ░  ░  ░  
 ░  ░ ░            ░  ░   ░        ░           ░  
    ░                                             

a modloader for roblox based on fleasion, written with python and slint
made by kit <3 special thanks to the fleasion team
1.3.0, licensed under the mpl-2.0 license
stream club icarus by artms
(no kliko i will not be using customtkinter)
"""

import slint, json, os, logging, webbrowser, requests
from urllib.parse import urlparse
requests.packages.urllib3.disable_warnings()

# logging.basicConfig( level=logging.INFO )
# YES the logging was intellisensed NO i am not gonna change it (i wrote like everything else myself i think)

class back:
    @staticmethod
    def fast(id: str = None, location: str = None, request: str = None):
        if id is not None:
            first = requests.post(f"https://assetdelivery.roblox.com/v1/assets/batch", verify=False, json=[{"assetId": id, "requestId": "0"}])
            if first.status_code != 200:
                logging.error("Failed to fetch asset data")
                return
            location = urlparse(first.json()[0]["location"]).path.split('/')[-1]
        here = f"{os.environ['LOCALAPPDATA']}/Temp/Roblox/http"
        if not os.path.exists(here):
            logging.error("Directory passed does not exist")
            return
        if request == "cachedHash": return [location]
        files = []
        for file in os.listdir(here):
            try:
                with open(f"{here}/{file}", "rb") as f:
                    if location.encode('utf-8') + b"\x00" + "�".encode('utf-8') in f.read():
                        logging.info(f"Found cached file for the asset at {here}/{file}")
                        files.append(file)
                        if request != "array": break
            except: logging.error("File inaccessible")
        return [location, files]
    @staticmethod
    def replace(file: str, cached: str):
        with open(file, "rb") as f: data = f.read()
        with open(cached, "wb") as f: f.write(data)
        logging.info("Modified cached file")
    @staticmethod
    def delete(cached: str = None):
        if os.path.exists(cached): os.remove(cached)
        logging.info("Deleted cached file")
    @staticmethod
    def corrupt_rbxstorage():
        with open(f"{os.environ['LOCALAPPDATA']}/Roblox/rbx-storage.db", "r+b") as f:
            data = f.read()
            if data != b"SQLite format 3\x00":
                f.truncate(0)
                f.seek(0)
                f.write(b"SQLite format 3\x00")
                logging.info("Corrupted rbx-storage.db")
        with open(f"{os.environ['LOCALAPPDATA']}/Roblox/rbx-storage-clone.db", "wb") as f: f.write(data)
        open(f"{os.environ['LOCALAPPDATA']}/Roblox/rbx-storage.db", "wb").close()

back.corrupt_rbxstorage()

try:
    with open(f"{os.getcwd()}/config/enabled.json", "r") as ef: ej = json.load(ef)
except:
    ej = []
    open(f"{os.getcwd()}/config/enabled.json", "a").close()
    logging.warning("enabled.json not found, creating a new one with an empty list.")
window = slint.load_file("ui/app-window.slint", style="fluent")

# loading the mods
mods = []
names = {}
if not os.path.exists(f"{os.getcwd()}/mods"):
    logging.warning("Mods directory not found, creating a new one.")
    os.makedirs(f"{os.getcwd()}/mods")
else:
    for name in os.listdir(f"{os.getcwd()}/mods"):
        here = f"{os.getcwd()}/mods/{name}"
        image_path = f"{os.getcwd()}/ui/images/default.png"
        for filetype in ["png", "jpg", "jpeg"]:
            possibility = f"{here}/icon.{filetype}"
            if os.path.exists(possibility):
                image_path = possibility
                break
        image = slint.Image.load_from_path(image_path)
        with open(f"{here}/meta.json", "r") as mf: meta = json.load(mf)
        try: enabled = meta["id"] in ej
        except: enabled = False
        mods.append({
            "name": meta["name"],
            "description": meta["description"],
            "image": image,
            "enabled": enabled,
            "id": meta["id"]
        })
        names[meta["id"]] = here

# oki the rest ;-;
class App(window.AppWindow):
    @slint.callback
    def slint_save(self):
        with open(f"{os.getcwd()}/config/enabled.json", "w") as ef: json.dump(ej, ef)
        for name, here in names.items():
            with open(f"{here}/meta.json", "r") as mf: meta = json.load(mf)
            with open(f"{here}/mapping.json", "r") as mapf: mapping = json.load(mapf)
            if name in ej:               
                update = False
                for file in mapping:
                    if not ("cachedHashes" in file or "locations" in file) and "assetIds" in file:
                        file["locations"] = []
                        file["cachedHashes"] = []
                        update = True
                        for assetId in file["assetIds"]:
                            search = back.fast(assetId)
                            back.replace(f"{here}/files/{file["name"]}", f"{os.environ['LOCALAPPDATA']}\\Temp\\Roblox\\http\\{cashedHash}")
                            file["locations"].append(search[0])
                            file["cachedHashes"].append(search[1])
                    if file.get("cachedHashes", None) is not None:
                        for cashedHash in file["cachedHashes"]: back.replace(f"{here}/files/{file["name"]}", f"{os.environ['LOCALAPPDATA']}\\Temp\\Roblox\\http\\{cashedHash}")
                if update:
                    with open(f"{here}/mapping.json", "w") as mapf: json.dump(mapping, mapf, indent=4)
            else:
                for file in mapping:
                    if "cachedHashes" in file:
                        for cashedHash in file["cachedHashes"]: back.delete(f"{os.environ['LOCALAPPDATA']}\\Temp\\Roblox\\http\\{cashedHash}")
    @slint.callback
    def slint_toggle(self, id: str):
        if id in ej: ej.remove(id)
        else: ej.append(id) # god this took me so much to figure out its probably horrible code tho
    @slint.callback
    def open_github(self): webbrowser.open("https://github.com/clubicarus/icarus")

app = App()
app.mods = slint.ListModel(mods)
app.run()
