# UAH-Theatre

## Release Notes:

### UAH Theatre Inventory 1.0.0

#### New Features:

* A functional inventory system
* Create items
* Edit/Update items
* Delete items
* Search items

#### Bug Fixes:

* None. It’s the first stable release!

#### Known Bugs:

* None, so far.


### UAH Theatre Inventory 1.0.1a

#### New Features:

* Admin functionalities
* Verify newly registered users
* Disable verified users
* Delete registered users
* Create new colors
* Edit/Update current colors
* Create new eras (time periods)
* Edit/Update current eras

#### Bug Fixes:

* None. The inventory system from the first release is fine.

#### Known Bugs:

* Regular user accounts can access administrator routes/functions. We should disable that.


## Install Guide:

### Pre-requisites: 

The application is run remotely through the web hosting solution Heroku. A web browser and internet access is necessary to manage the installation, as are a free Github account (https://github.com/join) and a free Heroku account (https://signup.heroku.com/). A web browser and internet access are also required to use the application.

### Dependencies: 

The application is entirely web-hosted, so it is not dependant on any locally installed libraries or software. No local installation is necessary to use the application. However, if you wish to make changes to the code or update the version that is running on Heroku, you will need to have Git (https://desktop.github.com/) and Heroku (https://devcenter.heroku.com/articles/heroku-cli) installed. For both installations, simply find the installer for your system (Windows/Mac/Linux) on that page, download it, and run it.

### Download Instructions: 

All of the code for the project is available at https://github.com/zehro/UAH-Theatre.

### Build Instructions: 

The build process is managed by Heroku. If the source code on Heroku has changed, a build request will automatically be added to the task queue. It normally takes less than 3 minutes for the build to complete and all changes to be deployed.

### Application Installation: 

As the application is hosted entirely on the web, no installation is necessary to use the application, just access it through a web browser on any device.

### Run Instructions: 

The application can be accessed through the live hosting site (https://uah-inventory.herokuapp.com/). For developer testing, run the command ‘flask run’ in the root directory (UAH-Theater) of the project, and go to localhost:5000 to view it.


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
