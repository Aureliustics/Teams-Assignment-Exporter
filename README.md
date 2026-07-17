<h1>Teams Assignment Exporter</h1>
<h3>A CLI tool to scrape Teams assignment data via Graph API in bulk. Downloads assignment files, submitted files, score, Teams channel icon, and other miscellaneous metadata. Used for students graduating or if you just want to backup all your work.</h3>
<h5>🌟 If you like this repository, a star would be greatly appreciated, thank you. 🌟</h5>

<h1>Requirements</h1>
<ul>
  <li>Python 3.12+</li>
  <li>Double click the file <code>Install-Dependencies.bat<code> or run <code>pip install requests colorama</code> to do install manually</li>
  <li><code>tkinter</code> (on Linux you may need <code>sudo apt install python3-tk</code>)</li>
</ul>

<h1>Installation and Usage</h1>
<ul>
  <li>1. Download the repository (Code > Local > Download ZIP) then extract the ZIP file</li>
  <li>2. Open command prompt (Windows + R, type cmd then press enter)</li>
  <li>3. Navigate to the folder that you got from extracting. <code>cd [PATH TO THE FOLDER HERE]</code></li>
  <li>4. Run <code>python exporter.py</code> then follow the prompts in the program</li>
</ul>

<h1>Getting and Using Token</h1>
  <h3>
    Method 1: With Script
  </h3>
<ul>
  <li>1. Copy the script from <a href="https://github.com/Aureliustics/Teams-Assignment-Exporter/blob/main/tokenExport.js" target="_blank">here</a> or from your folder</li>
  <li>2. Open Teams from a web browser and press F12 to open developer tools</li>
  <li>3. Click on any Teams assignment (this will make sure the token is loaded)</li>
  <li>4. Navigate to <code>Console</code> tab then paste and run the script. Since Chrome blocks script pasting, you may need to run <code>allow pasting</code> if prompted</li>
  <li>5. Copy the token that gets printed out and return to the program then right click to paste the token in</li>
</ul>
  <h3>
    Method 2: Manually
  </h3>
<ul>
  <li>1. Copy the script from <a href="https://github.com/Aureliustics/Teams-Assignment-Exporter/blob/main/tokenExport.js" target="_blank">here</a> or from your folder</li>
  <li>2. Open Teams from a web browser and press F12 to open developer tools</li>
  <li>3. Under <code>Network</code> tab, type in <code>graph.microsoft.com</code> in the <code>Filter</code> textbox</li>
  <li>4. Click on any Teams assignment (this will make sure the token is loaded)</li>
  <li>5. When you see <code>$value</code> get loaded, click on it and copy the <code>Authorization</code> text under <code>Request Headers</code></li>
  <li>6. Return to the program then right click to paste the token in</li>
</ul>

<h1>Features</h1>
<ul>
  <li>Creating an export folder and subsequent folders for each Team you are in</li>
  <li>Downloads all resources within an assignment (files the user submitted, feedback, score, reference material, etc.)</li>
  <li>Downloads icon of every Team.</li>
  <li>Neatly organizes files download into their designated paths ie. <code>my_work</code>, <code>reference_material</code></li>
  <li>Any resources that fail to download will have their resource link saved into <code>REQUIRES_MANUAL_DOWNLOAD.txt</code></li>
  <li>(Coming Soon) HTML viewer which you can use to select the exports folder and view your assignment history through a UI that mimics Teams</li>
  <li>(Coming Soon) Export Teams text channels</li>
  <li>(Coming Soon) UI version of the exporter</li>
</ul>

> [!NOTE]
> This uses a personal access token that is required for getting Teams data. It only accesses data you already have permission to see. Never share your token and treat it like a password.
