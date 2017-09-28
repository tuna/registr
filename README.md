# Registr

A "simple" web-based registering tool.

## Installation

### With Docker

clone this git repo and build docker image:

```
~> sudo docker build -t tuna/registr .
```

That's all:

```
~> sudo docker images | grep registr
```

### Without Docker

See contents of `Dockerfiles` please.

## Usage

Create an empty sqlite database:

```
~> touch /path/to/registration.db
```

Then create a container with following command:

```
~> sudo docker run -it --rm --name=registr \
        -p 80:8000 \
        -v /path/to/registration.db:/data/registr.db \
        -e FLASK_BASIC_AUTH_USERNAME=username \
        -e FLASK_BASIC_AUTH_PASSWORD=password \
        -e FLASK_SECRET_KEY='A very long secret key' \
        -e "FLASK_SQLALCHEMY_DATABASE_URI=sqlite:////data/registr.db" \
        -e FLASK_BABEL_DEFAULT_LOCALE=zh_Hans_CN \
        tuna/registr
```

Options:
* `FLASK_BASIC_AUTH_USERNAME`: username for admin page
* `FLASK_BASIC_AUTH_PASSWORD`: password for admin page
* `FLASK_SECRET_KEY`: secret key used by flask in client-end session, keep it safe and unpredictable
* `FLASK_BABEL_DEFAULT_LOCALE`: default locale

## Add New Languages

Currently, we support following locales:

* zh\_Hans\_CN
* de\_DE
* ja\_JP
* nl\_NL
* en\_US

If new one is required, install dependencies in `requirements.txt` and run:

```
~> ./i18n init <locale-name>
```
