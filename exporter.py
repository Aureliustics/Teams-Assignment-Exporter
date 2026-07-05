import os
import sys
import colorama
import tkinter as tk
import requests
import json
import time
from tkinter import filedialog

#note to self add docstrings (summary, params, return and the datatypes) so it isnt a pain for anyone contributing in the future

SAVE_DIR = None
API_ENDPOINT = "https://graph.microsoft.com/v1.0"
TOKEN = None
FAIL_LOG = []
colorama.init(autoreset=True)
WARNING = "\033[38;2;255;165;0m"
ERROR = "\033[31m"
SUCCESS = "\033[92m"
INFO = "\033[36m"

def find_location():
    print(f"{INFO}[*] Choose a directory to export your data")
    parent_dir = filedialog.askdirectory(title="Choose Where to Save Export Data")
    if not parent_dir:
        print(f"{WARNING}[!] No folder selected so defaulting to Documents")
        os.path.join(os.path.expanduser("~"), "Documents", "Exports")

    os.makedirs(os.path.join(parent_dir, "Teams Export"), exist_ok=True)
    return parent_dir

def sanitize_name(name):
    if not name or not isinstance(name, str):
        print(f"{ERROR}[-] Param not in valid format or empty, defaulting to \"Untitled\"")
        return "Untitled"
    
    name = name.rstrip()
    not_allowed = ['<', '>', ':', '\"', '\\', '/', '|', '?', '*']
    sanitized_name = ""
    for char in name:
        if char not in not_allowed:
            sanitized_name += char

    return sanitized_name[:150]

def fetch_token():
    global TOKEN
    if TOKEN:
        return TOKEN
    else:
        print(f"{INFO}[*] Paste your token here. To get your token, see tokenExport.js in the repository.")
        TOKEN = str(input(">>> "))
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()# clear the line after recieving token
        print(f"{SUCCESS}[+] Token recieved! Preceding.")
        return TOKEN    

def fetch_channels():
    pass

def get_classes():
    classes = []
    print(f"{INFO}[*] Fetching classes...")
    teams = handle_pagination(f"{API_ENDPOINT}/me/joinedTeams")
    #print(teams)
    for team in teams:# only grab display name of classes and its id
        item = {
            "id": team["id"],
            "displayName": team.get("displayName", "Unnamed Team")
        }
        classes.append(item)
    return classes

def get_assignments(class_id):
    #print(f"{INFO}[*] Fetching assignments...")
    return handle_pagination(f"{API_ENDPOINT}/education/classes/{class_id}/assignments")


def GET_request(url, params=None, stream=False, attempts=3):
    global TOKEN
    for _ in range(attempts):
        headers = {"Authorization": f"Bearer {fetch_token()}"}
        resp = requests.get(url, headers=headers, params=params, stream=stream)
        if resp.status_code == 401:
            print(f"{ERROR}[!] Invalid or expired token, please fetch a new one.")
            TOKEN = None
            continue
        return resp
    raise RuntimeError(f"{ERROR}[-] Failed to GET {url} after {attempts} tries.")

def handle_pagination(url, params=None):
    '''
    because graph cant return full responses if too big. collect the chunks/pages via @odata.nextLink
    '''
    results = []
    next_url = url
    next_params = params
    while next_url:
        resp = GET_request(next_url, params=next_params)
        if resp.status_code != 200:# if not success break out loop
            print(f"{ERROR}[-] Error retrieving page, error code: {resp.status_code}")
            break

        data = resp.json()
        results.extend(data.get("value", []))
        next_url = data.get("@odata.nextLink")
        next_params = None

    return results

def get_icon(id, folder):
    resp = GET_request(f"{API_ENDPOINT}/groups/{id}/photo/$value", stream=True)
    if resp.status_code != 200:
        print(f"{ERROR}[-] Error retrieving teams icon. Error code: {resp.status_code}")
        return
    
    content_type = resp.headers.get("Content-Type", "image/jpeg")
    if "png" in content_type:
        extension = "png"
    else:
        extension = "jpg"
    with open(os.path.join(folder, f"icon.{extension}"), "wb") as file:
        for chunk in resp.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"{SUCCESS}[+] Class icon downloaded")
    

def main():
    global SAVE_DIR
    SAVE_DIR = f"{find_location()}/Teams Export"
    if SAVE_DIR != None:
        print(f"{SUCCESS}[+] Exporting data to: {SAVE_DIR}")
    else:
        print(f"{ERROR}[-] Save directory not found!")
    classes = get_classes()

    failed = 0
    succeed = 0
    for cls in classes:
        class_name = cls.get("displayName", "Untitled Team")#later use the sanitize function when creating folder name
        class_id = cls.get("id", "null")
        print(f"\nScraping data from -> {class_name}")
        #print(class_name)
        #print(class_id)
        try:
            class_folder = os.path.join(SAVE_DIR, sanitize_name(class_name))
            os.makedirs(class_folder, exist_ok=True)
            print(f"{SUCCESS}[+] Folder successfully created")
            succeed += 1
        except Exception as err:
            print(f"{ERROR}[-] Folder could not be created: {err}")
            failed += 1
        #todo make it download the teams icon to this path aswell

        assignments = get_assignments(class_id)

        print(f"{INFO}[*] Found {len(assignments)} assignments")

        get_icon(class_id, class_folder)
        time.sleep(0.2)#avoid ratelimit


    print(f"\n{INFO}[*] Success rate: {(succeed / (succeed + failed) * 100)}% | {succeed} succeeded {failed} failed")

resp = GET_request("https://graph.microsoft.com/v1.0/me")
print(f"[DEBUG]: Data retrieve attempt: {resp.status_code, resp.json()}")
print(get_classes())
main()
    
