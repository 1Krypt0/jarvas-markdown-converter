# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

ENV POETRY_HOME="/usr/local" \
  POETRY_NO_INTERACTION=1 \
  POETRY_VERSION="1.8.4" \
  POETRY_VIRTUALENVS_IN_PROJECT=true

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg exiftool && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION
RUN $POETRY_HOME/bin/poetry --version


# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

RUN $POETRY_HOME/bin/poetry install

# Copy the rest of the app
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8080

# Command to run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

