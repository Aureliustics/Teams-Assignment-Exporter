import os
import tkinter as tk
from tkinter import filedialog

SAVE_DIR = None
API = "https://graph.microsoft.com/v1.0"
TOKEN = None
FAIL_LOG = []

def find_location():
    parent_dir = filedialog.askdirectory(title="Choose Where to Save Export Data")
    if not parent_dir:
        print("No folder selected so defaulting to Documents")
        os.path.join(os.path.expanduser("~"), "Documents", "Exports")

    os.makedirs(os.path.join(parent_dir, "Teams Export"), exist_ok=True)

find_location()