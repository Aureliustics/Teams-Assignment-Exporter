import os
import sys
import colorama
import tkinter as tk
import requests
from tkinter import filedialog

SAVE_DIR = None
API_ENDPOINT = "https://graph.microsoft.com/v1.0"
TOKEN = None
FAIL_LOG = []
colorama.init(autoreset=True)
WARNING = "\033[38;2;255;165;0m"
ERROR = "\033[31m"
SUCCESS = "\033[92m"

def find_location():
    print(f"[*] Choose a directory to export your data")
    parent_dir = filedialog.askdirectory(title="Choose Where to Save Export Data")
    if not parent_dir:
        print(f"{WARNING}[!] No folder selected so defaulting to Documents")
        os.path.join(os.path.expanduser("~"), "Documents", "Exports")

    os.makedirs(os.path.join(parent_dir, "Teams Export"), exist_ok=True)

find_location()

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
        print("[*] Paste your token here. To get your token, see tokenExport.js in the repository.")
        TOKEN = str(input(">>> "))
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()# clear the line after recieving token
        print(f"{SUCCESS}[+] Token recieved! Preceding.")
        return TOKEN    

def fetch_channels():
    pass

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

def main():
    global SAVE_DIR
    SAVE_DIR = find_location()
    print(f"{SUCCESS}[+] Exporting data to: {SAVE_DIR}")

resp = GET_request("https://graph.microsoft.com/v1.0/me")
print(f"[DEBUG]: Data retrieve attempt: {resp.status_code, resp.json()}")
    
