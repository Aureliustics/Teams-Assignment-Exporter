<h1>Teams Assignment Exporter</h1>
<h3>A CLI tool to scrape Teams assignment data via Graph API in bulk. Downloads assignment files, submitted files, score, Teams channel icon, and other miscellaneous metadata. Used for students graduating or if you just want to backup all your work.</h3>
<h5>🌟 If you like this repository, a star would be greatly appreciated, thank you.</h5>

<h1>Requirements</h1>
<ul>
  <li>Python 3.12+</li>
  <li>`pip install requests colorama`</li>
  <li>`tkinter` (included with Python on Windows/Mac; on Linux you may need `sudo apt install python3-tk`)</li>
</ul>

<h1>Installation and Usage</h1>
<ul>
  <li>1. Download the repository (Code > Local > Download ZIP) then extract the ZIP file</li>
  <li>2. Open command prompt (Windows + R, type cmd then press enter)</li>
  <li>3. Navigate to the folder that you got from extracting. `cd [PATH TO THE FOLDER HERE]`</li>
  <li>4. run `python exporter.py` then follow the prompts in the program</li>
</ul>

<h1>Getting and Using Token</h1>
  <h3>
    Method 1: With Script
  </h3>
<ul>
  <li>1. Copy the script from <a href="https://github.com/Aureliustics/Teams-Assignment-Exporter/blob/main/tokenExport.js" target="_blank">here</a> or from your folder</li>
  <li>2. Open Teams from a web browser and press F12 to open developer tools</li>
  <li>3. Click on any Teams assignment (this will make sure the token is loaded)</li>
  <li>4. Navigate to `Console` tab then paste and run the script. Since Chrome blocks script pasting, you may need to run `allow pasting` if prompted</li>
  <li>5. Copy the token that gets printed out and return to the program then right click to paste the token in</li>
</ul>
  <h3>
    Method 2: Manually
  </h3>
<ul>
  <li>1. Copy the script from <a href="https://github.com/Aureliustics/Teams-Assignment-Exporter/blob/main/exporter.py" target="_blank">here</a> or from your folder</li>
  <li>2. Open Teams from a web browser and press F12 to open developer tools</li>
  <li>3. Under `Network` tab, type in `graph.microsoft.com` in the `Filter` textbox</li>
  <li>4. Click on any Teams assignment (this will make sure the token is loaded)</li>
  <li>5. When you see `$value` get loaded, click on it and copy the `Authorization` text under `Request Headers` make sure to not copy `Bearer` within your token</li>
  <li>6. Return to the program then right click to paste the token in</li>
</ul>

<h1>Features</h1>
<ul>
  <li>Creating an export folder and subsequent folders for each Team you are in</li>
  <li>Downloads all resources within an assignment (files the user submitted, feedback, score, reference material, etc.)</li>
  <li>Downloads icon of every Team.</li>
  <li>Neatly organizes files download into their designated paths ie. `my_work`, `reference_material`</li>
  <li>Any resources that fail to download will have their resource link saved into `REQUIRES_MANUAL_DOWNLOAD.txt`</li>
  <li>(Coming Soon) HTML viewer which you can use to select the exports folder and view your assignment history through a UI that mimics Teams</li>
</ul>

> **Disclaimer:** This uses a personal access token that is required for getting Teams data. It only accesses data you already have permission to see. Never share your token and treat it like a password.
