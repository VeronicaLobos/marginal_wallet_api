# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.6
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that Cloud Run expects.
EXPOSE 8080

# Run the application using the SHELL form of CMD to allow for
# environment variable substitution (for $PORT). The ${PORT:-8080} syntax
# uses the PORT variable if it exists, or defaults to 8080 if it doesn't.
CMD gunicorn 'main:app' --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind "0.0.0.0:${PORT:-8080}"