# Raspberry Pi Scripts

This directory contains scripts for running the movie alerts application on a Raspberry Pi.

## Files

- `movie_alerts.py`: This is the main script that handles web scraping, file reading and writing, and email sending.
- `test.py`: This script is used for testing the functionality of the movie alerts application.
- `Dockerfile`: This file is used to build a Docker image for the application.
- `docker-compose.yml`: This file is used to define and run multi-container Docker applications.
- `requirements.txt`: This file lists the Python dependencies required for the application.
- `tmp/`: This directory contains text files downloaded from the S3 bucket. These files represent movie lists for different cinema locations.
- `.env`: This file needs to be created locally. It should contain your AWS account details and the email account from which emails will be sent.

Please note that the `.env` file is not included in the repository for security reasons. Make sure to create your own `.env` file with the necessary details.


## Usage

To run the movie alerts application, use the following command:

```
docker-compose up
```