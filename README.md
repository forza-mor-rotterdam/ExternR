# ExternR
Taakapplicatie voor het versturen van mails naar externe partijen op de MOR-keten

## Meer in-depth documentatie
**Architectuur:** ...

**Back-end:** ...

**Front-end:** [frontend/README.md](docs/frontend/README.md)

## Tech Stack

[Python](https://www.python.org/), [Django](https://www.djangoproject.com/start/), [Turbo JS](https://turbo.hotwired.dev/), [Stimulus JS](https://stimulus.hotwired.dev/), [SCSS](https://sass-lang.com/)

## Get Started 🚀

To get started, install [Docker](https://www.docker.com/) and [Node(v18.18.2)](https://nodejs.org/)

### Start MOR applications

1. https://github.com/forza-mor-rotterdam/mor-core

### Clone application code

```
git clone git@github.com:forza-mor-rotterdam/ExternR.git
```

### Install, build and watch frontend code

In a new console window/tab, go to [project-root]/app/frontend,
and start front-end and watcher by typing

```bash
npm install
npm run watch
```

### Create local dns entry

In a new console window/tab, go to [project-root]/
Add '127.0.0.1 externr.mor.local' to your hosts file

### Create docker networks

```bash
docker network create externr_network
docker network create mor_bridge_network
```

### Create env variables

Create .env.local file with the content of .env:

```bash
cp ./.env .env.local
```

### Start application

Build and run containers:

```bash
docker compose up
```

### Initial data

In a new console window/tab, go to [project-root]/
```bash
docker compose exec externr_app python manage.py local_dev_init
```

By now, a webserver started with correct initial data.
You can view the website on http://externr.mor.local:8008

Go to http://externr.mor.local:8008/login/ and login in with the following credentials:
  - Email: admin@forzamor.nl
  - Password: insecure

Once authenticated, go back to http://externr.mor.local:8008, you will be redirected to http://externr.mor.local:8008/beheer/

### Code style

Pre-commit is used for formatting and linting
Make sure pre-commit is installed on your system
Go to [project-root]/

```bash
brew install pre-commit
```
and run
```bash
pre-commit install
```

To manually run the pre-commit formatting run

```bash
pre-commit run --all-files
```
Pre-commit currently runs black, flake8, autoflake, isort and some pre-commit hooks. Also runs prettier for the frontend.
