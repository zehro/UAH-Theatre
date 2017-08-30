# UAH-Theatre

## Set up the local server

1. Follow the instruction [here](http://flask.pocoo.org/docs/0.12/installation/#installation) to install the virtualenv and related tools
2. Clone this repository, check out to the flask-skeleton branch ```git checkout flask-skeleton```
3. cd to the repository, run the following commands one by one if it's the first time you set up the environment
(it's recommended to set up aliases for these commands. On OSX, edit the .bash_profile file and add aliases there (google how to do it))
```
virtualenv venv

. venv/bin/activate

export FLASK_APP=uah
export FLASK_DEBUG=true (recommended)

pip install -e .
flask run
```
Then navigate to localhost:5000, the app should be up.

If you already set up the environment, running these commands each time should be sufficient to get the local server up:
```
. venv/bin/activate

flask run
```

Run ```deactivate``` to exit the virtualenv.

If the flask command is not found, try running ```pip install flask``` first in your virtualenv.
To install other dependencies, run ```pip install requirements.txt```.
