# Omniplex Movie Alert

This Python application is designed to keep you updated with the latest movies showing at Omniplex. It automatically scrapes the "What's On" list from the Omniplex website and sends an email notification whenever a new movie is added.

## Features

- Web scraping: The application scrapes the "What's On" list from the Omniplex website to fetch the latest movies.
- Email notifications: When a new movie is added to the list, the application sends an email notification with the details of the movie.
- AWS S3 integration: The application uses AWS S3 to store and retrieve movie lists for different cinema locations.
- Docker support: The application can be easily containerized using Docker, making it portable and easy to deploy, look within the raspberry pi folder for this.

## Getting Started

To get started with the Omniplex Movie Alert application, you need to set up a few things:

1. **AWS Account**: The application uses AWS S3 for storage. You need to set up an AWS account and configure it in a `.env` file.
2. **Email Account**: The application sends email notifications from a specified email account. You need to provide the details of this account in the `.env` file.
3. **Docker**: The application uses Docker for deployment. Make sure Docker is installed and running on your machine. Then you can find the docker compose file and the Dockerfile within the raspberry-pi folder.

Once you have these set up, you can run the application using Docker Compose: `docker-compose`

## Files

- `movie_alerts.py`: This is the main script that handles web scraping, file reading and writing, and email sending.
- `test.py`: This script is used for testing the functionality of the movie alerts application.
- `Dockerfile`: This file is used to build a Docker image for the application.
- `docker-compose.yml`: This file is used to define and run multi-container Docker applications.
- `requirements.txt`: This file lists the Python dependencies required for the application.
- `raspberry-pi/`: This directory contains scripts for running the movie alerts application on a docker, it is named "rasberry-pi" as, you guessed it, this is how I am hosting the code.
- `lambda-trials/`: This directory contains files related to attempting to run the code on AWS Lambda. The package folder for this is included within the gitignore as they are quite large along with the webdrivers, so for this repo only code that creates the zip file and the venv are included.
- `tmp/`: This directory contains text files downloaded from the S3 bucket. These files represent movie lists for different cinema locations.
- `.env`: This file needs to be created locally. It should contain your AWS account details and the email account from which emails will be sent.
- `venv/`: This directory contains a Python virtual environment where the project's dependencies are installed. This directory needs to be created locally.