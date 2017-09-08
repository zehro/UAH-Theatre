# UAH-Theatre

## Setting Up the Local Server
1. Install Python 3. If you're running Linux, your distribution will provide packages you can use.
2. Follow the instructions [here](http://flask.pocoo.org/docs/0.12/installation/#installation) to install the virtualenv and related tools
3. Clone this repository.
4. Open a terminal and navigate to this repository. Run ```virtualenv venv```. This creates a virtual Python 3 environment where you can install packages specific to this app.
5. Run the following commands one by one
```
virtualenv venv

export FLASK_APP=uah
export FLASK_DEBUG=true (recommended)

. venv/bin/activate (OSX/Linux)
. venv/Scripts/activate (Windows)

pip install -e .
```
6. Install necessary packages by running ```pip install -r requirements.txt```.
7. Now type ```flask run```, the localhost should be up and running.

## Running the Local Server
Follow this instruction to start the local server if you have already set it up.
1. Open a terminal and navigate to this repository.
2. Run the following commands.

If there's no 'venv' in front of your username in the terminal, it means virtual env isn't activated. Run one of the following:
```
. venv/bin/activate (OSX/Linux)
. venv/Scripts/activate (Windows)
```
Then, run: ``` flask run ```. This is the command that starts the local server.

Press ctrl+C to stop the local server.

Run ```deactivate``` to exit the virtualenv.
