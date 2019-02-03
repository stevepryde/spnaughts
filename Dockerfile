FROM python:3.7

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY Pipfile /app
RUN pip install pipenv
RUN pipenv install

WORKDIR /app
COPY . /app

CMD pipenv run python rabbit_worker.py