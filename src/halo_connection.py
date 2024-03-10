import requests

def get_current_core(headers, xuid, clearance):
    headers = {
        "Accept": "application/json",
        "343-clearance": clearance,
        "X-343-authorization-spartan": headers["x-343-authorization-spartan"]
    }

    editedUserID = f"xuid({xuid})"
    url = f"https://economy.svc.halowaypoint.com/hi/customization?players={editedUserID}"

    inventory_request  = requests.get(url, headers=headers)

    if inventory_request.status_code:
        return inventory_request.json()

def get_item_details(spartan_token, path):
    url = f"https://gamecms-hacs.svc.halowaypoint.com/hi/progression/file/{path}"

    headers = {
        "X-343-Authorization-Spartan": spartan_token
    }

    req = requests.get(url, headers=headers)

    if req.status_code == 200:
        return req.json()
    
def get_item_name(item_json):
    return item_json["CommonData"]["Title"]["value"]

def get_spartan_setup(spartan_token, inventory):
    armor_path = inventory["PlayerCustomizations"][0]["Result"]["ArmorCores"]["ArmorCores"][0]
    core_path = armor_path["CorePath"]

    loadout = {}

    core_details = get_item_details(spartan_token, core_path)
    loadout["Core"] = get_item_name(core_details)

    theme_path = armor_path["Themes"][0]

    items = [
        "Glove",
        "Helmet",
        "HelmetAttachment",
        "ChestAttachment",
        "KneePad",
        "LeftShoulderPad",
        "RightShoulderPad",
        "HipAttachment",
        "WristAttachment"
    ]

    for item in items:
        item_path = theme_path[f"{item}Path"]
        if item_path:
            item_details = get_item_details(spartan_token, item_path)
            loadout[item] = get_item_name(item_details)

    return loadout



