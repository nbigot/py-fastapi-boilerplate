# Readme

This is a template for a FastAPI project.


## Overview

This project template is designed to help you quickly set up and start developing a web application using FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.


## Features

- **FastAPI**: Leverages the FastAPI framework for building APIs quickly and efficiently.
- **Pydantic**: Utilizes Pydantic for data validation and settings management.
- **JWT Authentication**: Includes support for JSON Web Tokens (JWT) for secure authentication.
- **Database Support**: Provides integration with PostgreSQL and MySQL databases.
- **Linting and Formatting**: Uses ruff for code linting and formatting.


## Getting Started

### Poetry

To add dependencies, use the following commands:

```sh
$ poetry add fastapi pydantic pyjwt requests jinja2 python-dateutil PyYAML jsonschema python-json-logger
$ poetry add boto3 pandas psycopg2 mysql pymysql redis pika
$ poetry add pytest mock fakeredis freezegun pytest-cov pytest-benchmark pipdeptree ruff flake8 black isort python-semantic-release
```


## PostgreSQL

To run a PostgreSQL database using Docker, use the following command:

```sh
$ docker run --rm --name postgres -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
```

### Lint

Using ruff for linting and formatting:

```sh
$ ruff check
$ ruff check --fix
$ ruff format
```

## Configuration

Configuration settings for the project are managed using environment variables and can be found in the app/config/config.yaml file. This includes settings for AWS, FastAPI, logging, authentication, and database connections.


## Testing

Run tests using pytest:

```sh
$ pytest
```
