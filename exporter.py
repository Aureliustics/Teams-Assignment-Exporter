import os
import sys
import colorama
import tkinter as tk
import requests
import re
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
            print(f"{ERROR}[-] Invalid or expired token, please fetch a new one.")
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


def get_submission(class_id, assignment_id):
    submissions = handle_pagination(f"{API_ENDPOINT}/education/classes/{class_id}/assignments/{assignment_id}/submissions")
    if submissions:
        return submissions[0]
    else:
        return None

def get_score(class_id, assignment_id, submission_id):
    resp = GET_request(f"{API_ENDPOINT}/education/classes/{class_id}/assignments/{assignment_id}/submissions/{submission_id}/outcomes")
    if resp.status_code != 200:
        print(F"{ERROR}[-] Failed to get assignment score. Error code: {resp.status_code}")
        return []

    return resp.json().get("value", [])

def get_submission_files(class_id, assignment_id, submission_id):
    resp = GET_request(f"{API_ENDPOINT}/education/classes/{class_id}/assignments/{assignment_id}/submissions/{submission_id}/resources")

    if resp.status_code != 200:
        print(f"{ERROR}[+] Could not retrieve submission files. Error: {resp.status_code}")
        return
    
    return resp.json().get("value", [])

def get_drive_id(url):
    if not url:
        return None
    
    match = re.search(r"/drives/([^/]+)/items/", url)#find the correct class drive by searching in: https://graph.microsoft.com/v1.0/drives/{driveId}/items/{itemId}
    if match:
        return match.group(1)
    else:
        return None
    
def get_reference_material(class_id, assignment_id):
    return handle_pagination(f"{API_ENDPOINT}/education/classes/{class_id}/assignments/{assignment_id}/resources")

def resource_handler(resource, path, drive_id=None, class_name="", assignment_name="", assignment_url=""):
    '''todo: need to do this for all resource types: https://learn.microsoft.com/en-us/graph/api/resources/educationresource?view=graph-rest-1.0'''
    resource = resource.get("resource", {})
    type = resource.get("@odata.type", "")
    filename = resource.get("displayName") or "resource"

    if "External" in type or "Link" in type:
        link = resource.get("link")
        url = resource.get("webUrl")
        if not url:
            if isinstance(link, dict):
                url = link.get("webUrl")
            else:
                url = None
        log_path = os.path.join(path, f"{sanitize_name(filename)}_LINK.txt")
        with open(log_path, "w", encoding="utf-8") as file:
            file.write(f"Name of file: {filename}\nType: {type}\nURL: {url or "Unavailable"}\n(No resources found so open URL manually instead)")
        print(f"    {SUCCESS}Saved resource link: {filename}")
        return

    drive_item_id = None
    resource_drive_id = drive_id

    file_info = resource.get("file")
    if isinstance(file_info, dict):
        drive_item_id = file_info.get("resourceId") or file_info.get("id")

    file_url = resource.get("fileUrl")

    if not drive_item_id and file_url:
        match = re.search(r"/drives/([^/]+)/items/([^/?]+)", file_url)#https://graph.microsoft.com/v1.0/drives/{driveId}/items/{itemId}
        if match:
            resource_drive_id = match.group(1)
            drive_item_id = match.group(2)

    urls = []
    if resource_drive_id and drive_item_id:
        urls.append(f"{API_ENDPOINT}/drives/{resource_drive_id}/items/{drive_item_id}/content")
    if drive_item_id:
        urls.append(f"{API_ENDPOINT}/me/drive/items/{drive_item_id}/content")
    if file_url:
        urls.append(file_url if file_url.endswith("/content") else f"{file_url}/content")

    downloaded = False
    destination = os.path.join(path, sanitize_name(filename))

    for url in urls:#method 1: trying a direct download of /content
        try:
            resp = GET_request(url, stream=True)
            if resp.status_code == 200:
                with open(destination, "wb") as file:
                    for chunk in resp.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"    {SUCCESS}Downloaded {filename}")
                downloaded = True
                break
        except requests.RequestException:
            print(f"    {WARNING}[!] Method 1 of content download failed.. attempting method 2")

    if not downloaded and resource_drive_id and drive_item_id:#method 2: if /content download fails due to something like 403, we fetch the items metadata and get the downloadUrl through that
        meta_url = f"{API_ENDPOINT}/drives/{resource_drive_id}/items/{drive_item_id}"
        try:
            meta_resp = GET_request(meta_url)
            if meta_resp.status_code == 200:
                fetched_url = meta_resp.json().get("@microsoft.graph.downloadUrl")
                if fetched_url:
                    download_resp = requests.get(fetched_url, stream=True)
                    if download_resp.status_code == 200:
                        with open(destination, "wb") as file:
                            for chunk in download_resp.iter_content(chunk_size=8192):
                                file.write(chunk)
                        print(f"    {SUCCESS}Downloaded {filename}")
                        downloaded = True
        except requests.RequestException as err:
            print(f"    {ERROR}[-] Download of submitted resource failed. Error code: {err}")

    if not downloaded:#if still failed to download, make a log
        log_path = os.path.join(path, f"{sanitize_name(filename)}_UNAVAILABLE.txt")
        with open(log_path, "w", encoding="utf-8") as file:
            file.write(f"Name: {filename}\nType: {type}\nCould not download this file. Try manually downloading:\n{assignment_url or 'Not found'}")
        print(f"    {ERROR}Could not download {filename} so saved details instead")
        FAIL_LOG.append((class_name, assignment_name, filename, assignment_url))

def write_metadata(path, class_name, assignment, submission, scores):
    points = "?"
    max_points = "?"
    feedback = "None"
    instructions = "None"
    if submission:
        status = submission.get("status", "unknown")
    else:
        status = "unknown"

    grading = assignment.get("grading")
    if isinstance(grading, dict):
        max_points = grading.get("maxPoints", "?")

    for score in scores:
        if "PointsOutcome" in score.get("@odata.type", ""):
            published = score.get("publishedPoints")
            drafted = score.get("points")
            if published and published.get("publishedPoints") is not None:
                points = published
            elif drafted and drafted.get("points") is not None:
                points = drafted["points"]
        elif "FeedbackOutcome" in score.get("@odata.type", ""):
            feedback = score.get("publishedFeedback")
            if isinstance(feedback, dict):#prevent errors upon no feedback
                feedback_text = feedback.get("text")
                if isinstance(feedback_text, dict) and feedback_text.get("content"):#checks to make it resistent to variations in data structure
                    feedback = feedback_text["content"]
                elif isinstance(feedback_text, str) and feedback_text:
                    feedback = feedback_text
    if assignment.get("instructions"):
        instructions = assignment["instructions"].get("content", "None")

    data = [f"Assignment: {assignment.get('displayName', 'Untitled')}\nStatus: {status}\nPoints: {points}/{max_points}\nDue Date: {assignment.get('dueDateTime', 'Unknown')}\nAssigned: {assignment.get('assignedDateTime', 'Unknown')}\nClass name: {class_name}\nInstructions: {instructions}\nFeedback: {feedback}"]
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(data))
    #print(f"{SUCCESS}     -> Wrote assignment metadata")

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
            continue

        get_icon(class_id, class_folder)

        assignments = get_assignments(class_id)
        print(f"{INFO}[*] Found {len(assignments)} assignment{'s' if len(assignments) > 1 else ''}")

        for assignment in assignments:
            assignment_name = sanitize_name(assignment.get("displayName", "Untitled Assignment"))
            assignment_folder = os.path.join(class_folder, assignment_name)
            reference_material_folder = os.path.join(assignment_folder, "reference_material")
            os.makedirs(reference_material_folder, exist_ok=True)

            try:
                os.makedirs(assignment_folder, exist_ok=True)
                print(f"{SUCCESS}  -> Created assignment subfolder: {assignment_name}")
            except Exception as err:
                print(f"{ERROR}[-] Subfolder {assignment_name} could not be created")

            submission = get_submission(class_id, assignment["id"])
            drive_id = get_drive_id(assignment.get("resourcesFolderUrl"))
            score = []
            if submission:
                score = get_score(class_id, assignment["id"], submission["id"])
                submitted_files = get_submission_files(class_id, assignment["id"], submission["id"])
                if submitted_files:# fetching the resources that student submitted
                    submission_folder = os.path.join(assignment_folder, "my_work")
                    os.makedirs(submission_folder, exist_ok=True)
                    #print(f"Submitted files: {submitted_files}")
                    submission_folder = os.path.join(assignment_folder, "my_work")
                    os.makedirs(submission_folder, exist_ok=True)
                    for resource in submitted_files:
                        resource_handler(resource, submission_folder, drive_id, class_name, assignment_name, assignment.get("webUrl", ""))

            for material in get_reference_material(class_id, assignment["id"]):#getting teacher provided resources
                resource_handler(material, reference_material_folder, drive_id, class_name, assignment_name, assignment.get("webUrl", ""))

            write_metadata(os.path.join(assignment_folder, "metadata.txt"), class_name, assignment, submission, score)

        time.sleep(0.2)#avoid ratelimit

    if FAIL_LOG:
        log_path = os.path.join(SAVE_DIR, "REQUIRES_MANUAL_DOWNLOAD")
        with open(log_path, "w", encoding="utf-8") as file:
            file.write(f"{len(FAIL_LOG)} files failed to download likely due to blocked permissions or rate limit. Manually download the files below in order to presereve them.\n")
            file.write("#" * 67 + "\n\n")
            for team, assignment, filename, url in FAIL_LOG:
                file.write(f"Team:  {team}\nAssignment:  {assignment}\nFile:  {filename}\nLink:  {url or 'Not Found'}")

            print(f"{WARNING}[!] Detected {len(FAIL_LOG)} files that require manual downloading. Check {log_path}")
    try:
        print(f"\n{INFO}[*] Success rate: {(succeed / (succeed + failed) * 100)}% | {succeed} succeeded {failed} failed")
    except ZeroDivisionError:
        print(f"[*] Cannot calculate success rate because no teams were found")

main()
    
