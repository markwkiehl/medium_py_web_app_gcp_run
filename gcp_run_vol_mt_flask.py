#
#   Written by:  Mark W Kiehl
#   http://mechatronicsolutionsllc.com/
#   http://www.savvysolutions.info/savvycodesolutions/

# Copyright (C) Mechatroinc Solutions LLC 2025
# License:  MIT


# Define the script version in terms of Semantic Versioning (SemVer)
# when Git or other versioning systems are not employed.
__version__ = "0.0.0"
from pathlib import Path
print("'" + Path(__file__).stem + ".py'  v" + __version__)
# v0.0.0    Initial release


"""
This script will be packaged into a container and configured to run as a Cloud Run Service.

A Cloud Storage volume mount is used to create a bridge between the Cloud Storage bucket
and the Cloud Run container's file system.
Volume mounts allow a container (this script) to access files stored in persistent disks or NFS shares as if they were local.
The feature leverages Cloud Storage FUSE to provide this file system interface.  


Gunicorn
Gunicorn is a WSGI (Web Server Gateway Interface)  server and is designed to handle concurrent requests efficiently.
MIT license
https://rest-apis-flask.teclado.com/docs/deploy_to_render/docker_with_gunicorn/



FLASK
Flask is built on two core components: Werkzeug, a WSGI web application library, and Jinja2, a template engine. 
Flask handles the backend logic, while the HTML framework handles the frontend presentation and styling.

The @app.route() decorator is a Python function that Flask provides to associate a URL pattern with a function. The decorator takes the URL path as its first argument and optionally, methods (like GET, POST) as another. When Flask receives a request, it matches the URL against these patterns and invokes the associated function.

https://flask.palletsprojects.com/en/stable/




PIP INSTALL

google-cloud-storage
google-cloud-run
flask
gunicorn

"""

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpful tools

def savvy_get_os(verbose=False):
    """
    Returns the following OS descriptions depending on what OS the Python script is running in:
        "Windows"
        "Linux"
        "macOS"

    os_name = savvy_get_os()
    """

    import platform

    if platform.system() == "Windows":
        return "Windows"
    elif platform.system() == "Linux":
        return "Linux"
    elif platform.system() == "Darwin":
        return "macOS"
    else:
        raise Exception("Unknown OS: ", platform.system())


def gcp_json_credentials_exist(verbose=False):
    """
    Returns TRUE if the Application Default Credentials (ADC) file "application_default_credentials.json" is found.

    Works with both Windows and Linux OS.

    https://cloud.google.com/docs/authentication/application-default-credentials#personal
    """

    from pathlib import Path

    if savvy_get_os() == "Windows":
        # Windows: %APPDATA%\gcloud\application_default_credentials.json
        path_gcloud = Path(Path.home()).joinpath("AppData\\Roaming\\gcloud")
        if not path_gcloud.exists():
            if verbose: print("WARNING:  Google CLI folder not found: " + str(path_gcloud))
            #raise Exception("Google CLI has not been installed!")
            return False
        if verbose: print(f"path_gcloud: {path_gcloud}")
        path_file_json = path_gcloud.joinpath("application_default_credentials.json")
        if not path_file_json.exists() or not path_file_json.is_file():
            if verbose: print("WARNING: Application Default Credential JSON file missing: "+ str(path_file_json))
            #raise Exception("File not found: " + str(path_file_json))
            return False
        
        if verbose: print(str(path_file_json))
        return True
    else:
        # Linux, macOS: 
        # $HOME/.config/gcloud/application_default_credentials.json
        # //root/.config/gcloud/application_default_credentials.json
        path_gcloud = Path(Path.home()).joinpath(".config/gcloud/")
        if not path_gcloud.exists():
            if verbose: 
                print("Path.home(): ", str(Path.home()))
                print("WARNING:  Google CLI folder not found: " + str(path_gcloud))
            # WARNING:  Google CLI folder not found: /.config/gcloud
            #raise Exception("Google CLI has not been installed!")
            return False
        if verbose: print(f"path_gcloud: {path_gcloud}")

        path_file_json = path_gcloud.joinpath("application_default_credentials.json")
        if not path_file_json.exists() or not path_file_json.is_file():
            if verbose: print("WARNING: Application Default Credential JSON file missing: "+ str(path_file_json))
            # /root/.config/gcloud/application_default_credentials.json
            #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='$HOME/.config/gcloud/application_default_credentials.json'
            #raise Exception("File not found: " + str(path_file_json))
            return False
        
        if verbose: print(str(path_file_json))
        # /root/.config/gcloud/application_default_credentials.json
        return True


def get_chat_history_file_path():
    """
    path_file = get_chat_history_file_path()
    """
    import os
    from pathlib import Path

    adc_json_file_found = gcp_json_credentials_exist()
    #print(f"adc_json_file_found: {adc_json_file_found}")

    history = ""

    if adc_json_file_found:
        # Not running in Google Cloud Run
        path = Path(Path.cwd())
        #path = Path.home()
    
    else:
        # Running in Google Cloud Run
        # Get the Google Storage bucket mount path from the OS environment variable, or assign a default.
        path = os.environ.get('MOUNT_PATH', '/mnt/storage')
        print(f"bucket_mount_path: {path}")

        # Create the folder 'bucket_mount_path' if it doesn't exist using pathlib
        path = Path(path)
        #print(f"path_bucket_mount.is_dir(): {path_bucket_mount.is_dir()}")
        if not path.is_dir:  path.mkdir()
        if not path.is_dir: raise Exception(f"Unable to create folder {path}")

    # Define the text filename to write/read to.
    path_file = path.joinpath("chat_history.txt")
    #print(f"path_file: {path_file}")
    #if path_file.is_file():  path_file.unlink()     # Delete the file if it already exists
    #if path_file.is_file(): raise Exception(f"Unable to delete file {path_file}")

    return path_file



def write_chat_history(query:str="", response:str=""):
    """
    Writes (appends) the query & response chat history to a text file.

    """
    from markupsafe import Markup, escape

    # Escape anything bad that might be in query
    query = escape(query)

    path_file = get_chat_history_file_path()

    with open(file=path_file, mode="a", encoding='utf-8') as f:
        f.write(query + "\n")
        f.write(response + "\n")



def get_chat_history():
    """
    Returns the chat history (if any).

    chat_history = get_chat_history()
    """
    from markupsafe import Markup, escape

    path_file = get_chat_history_file_path()

    history = ""

    if not path_file.is_file(): return history

    with open(file=path_file, mode="r", encoding='utf-8') as f:
        i = 0
        for line in f.readlines():
            i += 1
            if i % 2 == 0:
                # line # even  (response line)
                history += Markup(f"<p><font color='blue'>{line.strip()}</font></p>")
            else:
                # line # odd  (query line)
                history += Markup(f"<p>{line.strip()}</p>")
    
    #print(f"history: {history}")
    return history





# ---------------------------------------------------------------------------
# Flask

from flask import Flask, render_template, request, url_for
from markupsafe import escape

app = Flask(__name__)  # Create a Flask instance

def get_app_info():
    info = ""
    info += f"OS: {savvy_get_os()}\n"
    adc_json_file_found = gcp_json_credentials_exist()
    info += f"Application Default Credentials (ADC) file 'application_default_credentials.json found: {str(adc_json_file_found)}\n"
    path_file = get_chat_history_file_path()
    info += f"path_file: {path_file}\n"
    return info

    

# Define a basic route and a function that will be called when accessing the root URL
@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Inspect the contents of the index.html file to see what render_template() does.

    """

    # Check the generated URL
    #print(f"home url_for: {url_for('static', filename='css/skeleton.css')}") 

    user_input = ""
    chat_history = ""
    if request.method == 'POST':
        # The user has clicked the "Submit" button on the index.html page.
        user_input = escape(request.form.get('user_input'))
        llm_response = "I don't know"
        write_chat_history(user_input, llm_response)
        chat_history = get_chat_history()
        print(f"chat_history: {chat_history}")
        return render_template('index.html', query=user_input, chat_history=chat_history, app_info=get_app_info())

    # No form submission from index.html.  Just display the page index.html
    return render_template('index.html', query="", chat_history="", app_info=get_app_info())


@app.route('/index.html')
def index():
    """
    Refreshes the web page back to index.html without any form submission. 
    """

    path_file = get_chat_history_file_path()
    #print(f"path_file: {path_file}")
    # Delete the file if it exists
    if path_file.is_file():  path_file.unlink()     

    return render_template('index.html', query="", chat_history="", app_info=get_app_info())



if __name__ == '__main__':
    pass

    # If running Flask built-in server (not Gunicorn), then the next line must be uncommented. If using Gunicorn, disable (comment out) the next line.
    #app.run(host='0.0.0.0', port=5000)


