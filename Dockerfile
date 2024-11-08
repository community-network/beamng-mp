FROM python:3.13

WORKDIR /usr/src/app

RUN pip install poetry
COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock /poetry.lock
RUN poetry config virtualenvs.create false

RUN poetry install --only main

COPY . .

HEALTHCHECK CMD discordhealthcheck || exit 1

CMD [ "python", "./bot.py" ]
