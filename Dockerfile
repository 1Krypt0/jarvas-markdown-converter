# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment Variables for Poetry
ENV POETRY_HOME="/usr/local" \
  POETRY_NO_INTERACTION=1 \
  POETRY_VERSION="1.8.4" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  PATH="/usr/local/bin:$PATH"

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg exiftool && rm -rf /var/lib/apt/lists/*

# Install Poetry globally
RUN pip install poetry==$POETRY_VERSION && poetry --version

# Copy dependency files first for caching
COPY pyproject.toml poetry.lock ./

# Install dependencies without installing the project itself
RUN poetry install --no-root

# Copy the rest of the app
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8080

# Command to run FastAPI with Uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
