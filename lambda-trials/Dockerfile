# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the movie_alerts.py file into the container
COPY movie_alerts.py .
COPY aws_storage.py .
COPY geckodriver .

# Set the command to run when the container starts
CMD ["python", "movie_alerts.py"]