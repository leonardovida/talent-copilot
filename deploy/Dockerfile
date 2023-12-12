FROM python:3.11.6-slim-bullseye as prod
RUN apt-get update && apt-get install -y \
  gcc \
  poppler-utils \
  && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.7.1

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN poetry install --only main
# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copying actual application
COPY . /app/src/
RUN poetry install --only main

CMD ["/usr/local/bin/python", "-m", "cv_copilot"]

FROM prod as dev

RUN apt-get update && apt-get install -y \
  poppler-utils \
  && rm -rf /var/lib/apt/lists/*

RUN poetry install
