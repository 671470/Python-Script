# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install Git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy the Python script and any other necessary files
COPY migrate.py /app/migrate.py

# Install any dependencies (if needed)
RUN pip install requests PyGithub python-gitlab python-dotenv
