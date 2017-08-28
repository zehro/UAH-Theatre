# UAH-Theatre

## Set up the local server

1. Follow the instruction [here](http://flask.pocoo.org/docs/0.12/installation/#installation) to install the virtualenv and related tools
2. Clone this repository, check out to the flask-skeleton branch ```git checkout flask-skeleton```
3. cd to the repository, run the following commands one by one 
(it's recommended to set up aliases for each of these commands. On OSX, edit the .bash_profile file and add aliases there (google how to do it))
```
virtualenv venv

. venv/bin/activate

export FLASK_APP=uah
export FLASK_DEBUG=true (recommended)

flask run
```
Then navigate to localhost:5000, the app should be up.
