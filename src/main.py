
#    _                       __             __       
#   (_)______ _______ _____ / /__  ___ ____/ /__ ____
#  / / __/ _ `/ __/ // (_-</ / _ \/ _ `/ _  / -_) __/
# /_/\__/\_,_/_/  \_,_/___/_/\___/\_,_/\_,_/\__/_/   
#                                                    
# a modloader for roblox based on fleasion, written with python and slint
# made by kit <3 special thanks to the fleasion team
# 1.4.3, licensed under the mpl-2.0 license
# stream club icarus by artms
# (no kliko i will not be using customtkinter)

import json, os, logging, webbrowser, sys # installed by default with python
import slint, requests, jsonschema # pypi packages
from traceback import format_exception
from urllib.parse import urlparse
from tkinter.messagebox import showerror
requests.packages.urllib3.disable_warnings()
# logging.basicConfig( level=logging.INFO )
# YES the logging was intellisensed NO i am not gonna change it (i wrote like everything else myself i think)    

with open(f"{os.getcwd()}/schemas/mapping.schema.json", "r") as sf: mapping_schema = json.load(sf)
with open(f"{os.getcwd()}/schemas/meta.schema.json", "r") as sf: meta_schema = json.load(sf)

class log_msgbox:
    @staticmethod
    def error(message: str):
        logging.error(f"\x1b[31;20m{message}\x1b[0m")
        showerror("Error", message)
        sys.exit()
    @staticmethod
    def warning(message: str):
        logging.warning(f"\x1b[33;20m{message}\x1b[0m")
        showerror("Error", message)

def oops(type, value, tb):
    what_happened = format_exception(type, value, tb)
    logging.error(f"An unknown error has happened:\n\x1b[31;20m{"\n".join(what_happened)}\x1b[0m")
    showerror("Error", f"An unknown error has happened:\n{what_happened[-1].strip()}")
    sys.exit()

sys.excepthook = oops

class back:
    @staticmethod
    def fast(id: str = None, location: str = None, request: str = None):
        if id is not None:
            first = requests.post(f"https://assetdelivery.roblox.com/v1/assets/batch", verify=False, json=[{"assetId": id, "requestId": "0"}])
            if first.status_code != 200:
                log_msgbox.warning(f"Failed to fetch asset data for the asset ID {id}. Please check your internet connection or the asset ID.")
                return
            location = urlparse(first.json()[0]["location"]).path.split("/")[-1]
        here = f"{os.environ["LOCALAPPDATA"]}/Temp/Roblox/http"
        if not os.path.exists(here):
            log_msgbox.error("Cache folder does not exist. Are you sure Roblox is installed?")
            return
        if request == "cachedHash": return [location]
        files = []
        for file in os.listdir(here):
            try:
                with open(f"{here}/{file}", "rb") as f:
                    if location.encode("utf-8") + b"\x00" + "�".encode("utf-8") in f.read():
                        logging.info(f"Found cached file for the asset at {here}/{file}")
                        files.append(file)
                        if request != "array": break
            except: log_msgbox.warning(f"File for {location} inaccessible. Check if the asset was loaded.")
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

if not os.path.exists(f"{os.getcwd()}/config/enabled.json"):
    log_msgbox.warning("config/enabled.json not found, creating it.")
    os.makedirs(f"{os.getcwd()}/config", exist_ok=True)
    open(f"{os.getcwd()}/config/enabled.json", "a").close()
    ej = []
else:
    with open(f"{os.getcwd()}/config/enabled.json", "r") as ef:
        try: ej = json.load(ef)
        except json.JSONDecodeError:
            log_msgbox.warning("enabled.json is corrupted, creating it again.")
            ej = []
            with open(f"{os.getcwd()}/config/enabled.json", "w") as ef: ef.write("[]")

window = slint.load_file("ui/app-window.slint", style="fluent")

# loading the mods
mods = []
names = {}
if not os.path.exists(f"{os.getcwd()}/mods"):
    log_msgbox.warning("Mods directory not found, creating it.")
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
        try: jsonschema.validate(instance=meta, schema=meta_schema)
        except:
            log_msgbox.warning(f"Metadata for {name} is invalid. Check the meta.json file.")
            continue
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
            try: jsonschema.validate(instance=meta, schema=meta_schema)
            except:
                log_msgbox.warning(f"Mappings for {name} is invalid. Check the mapping.json file.")
                continue
            if name in ej:               
                update = False
                for file in mapping:
                    if not ("cachedHashes" in file or "locations" in file) and "assetIds" in file:
                        file["locations"] = []
                        file["cachedHashes"] = []
                        update = True
                        for assetId in file["assetIds"]:
                            search = back.fast(assetId)
                            back.replace(f"{here}/files/{file["name"]}", f"{os.environ["LOCALAPPDATA"]}/Temp/Roblox/http/{cashedHash}")
                            file["locations"].append(search[0])
                            file["cachedHashes"].append(search[1])
                    if file.get("cachedHashes", None) is not None:
                        for cashedHash in file["cachedHashes"]: back.replace(f"{here}/files/{file["name"]}", f"{os.environ["LOCALAPPDATA"]}/Temp/Roblox/http/{cashedHash}")
                if update:
                    with open(f"{here}/mapping.json", "w") as mapf: json.dump(mapping, mapf, indent=4)
            else:
                for file in mapping:
                    if "cachedHashes" in file:
                        for cashedHash in file["cachedHashes"]: back.delete(f"{os.environ["LOCALAPPDATA"]}/Temp/Roblox/http/{cashedHash}")
    @slint.callback
    def slint_toggle(self, id: str):
        if id in ej: ej.remove(id)
        else: ej.append(id) # god this somehow took me so much to figure out its probably horrible code tho
    @slint.callback
    def open_github(self): webbrowser.open("https://github.com/clubicarus/icarus")

app = App()
app.mods = slint.ListModel(mods)
app.version = "1.4.3"
app.run()
