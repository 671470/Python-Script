# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install Git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
ENV PATH="/venv/bin:$PATH"

# Install dependencies within the virtual environment
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-txt

# Copy the Python script and any other necessary files
COPY migrate.py /app/migrate.py
