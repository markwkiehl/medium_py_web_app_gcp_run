# syntax=docker/dockerfile:1

# Define a default value for the argument PY_VER
ARG PY_VER=3.12

# Define a default value for the argument PY_SCRIPT_NAME
ARG PY_SCRIPT_NAME=must_pass_as_docker_build_arg.py

# slim version of Python 3.## to minimize the size of the container and make it as lightweight as possible
FROM python:${PY_VER}-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Optimize pip
ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Expose port 8080 for both Flask and Gunicorn server
EXPOSE 8080


# CMD uses the JSON array format ["command", "arg1", "arg2", ...]

# Quick debugging test
#CMD ["echo", "test"]


# Flask built-in server (not using Gunicorn)
#CMD ["python3", "gcp_run_vol_mt_flask.py"]


# Use Gunicorn (not the Flask built-in server)
# Revise the 4th argument to specify the script filename without the .py extension, and the Flask object (typically "app").
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "gcp_run_vol_mt_flask:app"]

