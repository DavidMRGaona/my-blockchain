# my-blockchain

A simple tutorial for developing a blockchain application from scratch in Python.

## Instructions to run

Clone the project,

```sh
$ git clone https://github.com/DavidMRGaona/my-blockchain.git
```

Install the dependencies,

```sh
$ cd python_blockchain_app
$ pip install -r requirements.txt
```

Start a blockchain node server,

```sh
$ export FLASK_APP=node_server.py
$ flask run --port 8000
```

### For windows users
```
set LANG=C.UTF-8
set FLASK_APP=node_server.py
flask run --port 8000
```
One instance of our blockchain node is now up and running at port 8000.


Run the application on a different terminal session,

```sh
$ python run_app.py
```

### For windows users
```
set LANG=C.UTF-8
set FLASK_APP=run_app.py
flask run --port 8000
```

The application should be up and running at [http://localhost:5000](http://localhost:5000).

