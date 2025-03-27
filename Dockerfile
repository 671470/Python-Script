# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and any other necessary files
COPY migrate.py /app/migrate.py
COPY .env /app/.env # If you are still using .env

# Install any dependencies (if needed)
RUN pip install requests PyGithub python-gitlab python-dotenv
