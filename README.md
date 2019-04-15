# flask_batch_download

A small Flask app (microservice) for generating and downloading a large number of PDF reports from the JSReport server.

## Prerequisites
* Python 3;
* PostgreSQL;
* JSReport account.

## Development
```sh
$ cp flask_app/config.temp.py flask_app/config.py
```
Configure credentials in ```config.py```. To start the server, run:
```sh
$ export FLASK_APP=flask_app/app.py
$ flask run
```
The app runs on http://127.0.0.1:5000.

## Run with Docker
* [Docker](https://docs.docker.com/)

```sh
$ docker build -t flask_batch_download .
$ docker run -p 5000:5000 -d flask_batch_download
```
