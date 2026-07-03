import os
import colorama
import tkinter as tk
from tkinter import filedialog

SAVE_DIR = None
API = "https://graph.microsoft.com/v1.0"
TOKEN = None
FAIL_LOG = []
colorama.init(autoreset=True)
WARNING = "\033[38;2;255;165;0m"
ERROR = "\033[31m"
SUCCESS = "\033[92m"

def find_location():
    parent_dir = filedialog.askdirectory(title="Choose Where to Save Export Data")
    if not parent_dir:
        print(f"{WARNING}No folder selected so defaulting to Documents")
        os.path.join(os.path.expanduser("~"), "Documents", "Exports")

    os.makedirs(os.path.join(parent_dir, "Teams Export"), exist_ok=True)

find_location()find_location()

def sanitize_name(name):
    if not name or not isinstance(name, str):
        print(f"{ERROR} Param not in valid format or empty, defaulting to \"Untitled\"")
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
        print("Paste your token here. To get your token, see tokenExport.js in the repository.")
        TOKEN = str(input(">>> "))
        return TOKEN    

    
