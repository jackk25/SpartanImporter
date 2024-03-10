import os
import sys

# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
vendor_dir = os.path.join(parent_dir, 'vendor')
print(parent_dir)
print(vendor_dir)

sys.path.append(vendor_dir)

from msal import PublicClientApplication
import requests
import json
import xml.etree.ElementTree as ET


app = PublicClientApplication(
    "bd4b98d1-2f0a-48c3-b717-268991f08a2a",
    authority = "https://login.microsoftonline.com/consumers"
)

def get_access_token(app):
    result = None
    accounts = app.get_accounts()

    # Attempt to grab users from the cache
    if accounts:
        print("Pick acc:")

        for account in accounts:
            print(account["username"])

        chosen = accounts[0]
        result = app.acquire_token_silent(["Xboxlive.signin", "Xboxlive.offline_access"], account=chosen)

    if not result:
        # So no suitable token exists in cache. Let's get a new one from Azure AD.
        result = app.acquire_token_interactive(scopes=["Xboxlive.signin", "Xboxlive.offline_access"])
    if "access_token" in result:
        access_token = result["access_token"]
        return access_token
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id")) 
        return None

def get_user_token(access_token):
    post_body = {
        "Properties": {
            "AuthMethod": "RPS",
            "RpsTicket": f"d={access_token}",
            "SiteName": "user.auth.xboxlive.com"
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }

    req = requests.post("https://user.auth.xboxlive.com/user/authenticate", data=json.dumps(post_body))

    if req.status_code == 200:
        response_json = req.json()
        user_token = response_json["Token"]
        uhs = response_json["DisplayClaims"]["xui"][0]['uhs']

        return user_token, uhs
    
    else:
        return None, None

def get_xsts_token(user_token):
    headers = {
        "Content-Type": "application/json",
	    "x-xbl-contract-version": "1"
    }

    post_body = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                user_token
            ]
        },
        "RelyingParty": "https://prod.xsts.halowaypoint.com/",
        "TokenType": "JWT"
    }

    xsts_req = requests.post("https://xsts.auth.xboxlive.com/xsts/authorize", headers=headers, data=json.dumps(post_body))

    if xsts_req.status_code == 200:
        response_json = xsts_req.json()
        xsts_token = response_json["Token"]

        return xsts_token
    
    else:
        return None

def get_spartan_token(xsts_token):
    headers = {
        "Content-Type": "application/json",
    }

    post_body = {
        "Audience": "urn:343:s3:services",
        "MinVersion": "4",
        "Proof": [
            {
                "Token": xsts_token,
                "TokenType": "Xbox_XSTSv3"
            }
        ]
    }

    spartan_token_req = requests.post(
        "https://settings.svc.halowaypoint.com/spartan-token", 
        headers=headers, 
        json=post_body
    )
    
    if spartan_token_req.status_code == 201:
        response_xml = spartan_token_req.content
        tree = ET.ElementTree(ET.fromstring(response_xml))
        
        root = tree.getroot()

        namespace = {'d': 'http://schemas.datacontract.org/2004/07/Microsoft.Halo.RegisterClient.Bond'}
        spartan_token = root.find("d:SpartanToken", namespace).text

        return spartan_token
    
    else:
        return None

def get_xuid(headers):
    gamer_info_req = requests.get("https://profile.svc.halowaypoint.com/users/me", headers=headers)
    
    if gamer_info_req.status_code == 200:
        response_json = gamer_info_req.json()
        xuid = response_json["xuid"]

        return xuid
    else:
        return None
    

def get_clearance(headers, xuid):
    editedUserID = f"xuid({xuid})"
    url = f"https://settings.svc.halowaypoint.com/oban/flight-configurations/titles/hi/audiences/RETAIL/players/{editedUserID}/active?sandbox=UNUSED&build=210921.22.01.10.1706-0"

    clearenceRequest = requests.get(url, headers=headers)
    if clearenceRequest.status_code == 200:
        response_json = clearenceRequest.json()
        flight_config_id = response_json["FlightConfigurationId"]

        return flight_config_id
    else:
        return None
    
def authenticate():
    access_token = get_access_token(app)
    if access_token:
            user_token, uhs = get_user_token(access_token)
            if user_token:
                xsts_token = get_xsts_token(user_token)
                if xsts_token:
                    spartan_token = get_spartan_token(xsts_token)

                    headers = {
                        "Content-Type": "application/json",
                        "x-343-authorization-spartan": spartan_token
                    }

                    xuid = get_xuid(headers)
                    if xuid:
                        clearance = get_clearance(headers, xuid)

                        return spartan_token, xuid, clearance, headers
