# UAH-Theatre

## Setting Up the Local Server
1. Install Python 3. If you're running Linux, your distribution will provide packages you can use.
2. Follow the instructions [here](http://flask.pocoo.org/docs/0.12/installation/#installation) to install the virtualenv and related tools
3. Clone this repository.
4. Open a terminal and navigate to this repository. Run ```virtualenv venv```. This creates a virtual Python 3 environment where you can install packages specific to this app.
5. On OS X or Linux, run ```. venv/bin/activate```. On Windows, run ```. venv/Scripts/activate```. This activates the virtual environment.
6. Install necessary packages by running ```pip install -r requirements.txt```.

## Running the Local Server
1. Open a terminal and navigate to this repository.
2. If you have not done so, activate the virtual environment. On OS X or Linux, run ```. venv/bin/activate```. On Windows, run ```. venv/Scripts/activate```.
3. Run the server with ```python app.py```. The server will automatically reload any changed files, provided that they were saved without syntax errors or other problems. If the server stops for this reason, you can always start it again by re-running this command.

Run ```deactivate``` to exit the virtualenv.
