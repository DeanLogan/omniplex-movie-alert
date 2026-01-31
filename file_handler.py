import os
import json
from browser_handler import search_cinema
from aws_storage import add_file, get_file_from_bucket

TMP_DIRECTORY = 'tmp/'
EMAIL_LIST_FILE = 'email_list.json'
ENV_ERROR_EMAIL = 'ERROR_EMAIL'
ERROR_READING_EMAIL_LIST = 'ERROR READING EMAIL LIST'

def write_arr_to_file(arr, filename):
    filepath = TMP_DIRECTORY + filename
    with open(filepath, 'w') as f:
        for s in arr:
            f.write(s + '\n')
    add_file(filepath, filename)

def read_file_to_arr(filename):
    filepath = get_file_from_bucket(filename)
    if filepath is None:
        return []
    with open(filepath, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

def get_diff_movies(driver, location):
    movies_on_website = search_cinema(driver, location)
    movies_on_file = read_file_to_arr(location + ".txt")
    return [movie for movie in movies_on_website if movie not in movies_on_file], movies_on_website

def extract_email_info():
    filepath = get_file_from_bucket(EMAIL_LIST_FILE)
    if filepath is None:
        from email_handler import send_email
        send_email([os.environ.get(ENV_ERROR_EMAIL)], ERROR_READING_EMAIL_LIST, "Error reading email list")
        os._exit(0)
    with open(filepath) as f:
        data = json.load(f)
    locations = [location for item in data for location in item['locations']]
    locations = list(set(locations))
    return data, locations
