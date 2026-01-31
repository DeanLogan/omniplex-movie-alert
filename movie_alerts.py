import os
import time
import json
import smtplib
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from aws_storage import add_file, get_file_from_bucket
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions

BROWSER_TIMEOUT = 30
SLEEP_INTERVAL = 1

WHATS_ON_LINK = 'https://www.omniplex.ie/whatson'
DROPDOWN_OPTION = 'homeSelectCinema'
SHOWTIMES_PAGE = '/movie/showtimes/'

CLASS_INLINE_BLOCK = 'OMP_inlineBlock'
CLASS_IMAGE_ROUNDED = 'OMP_imageRounded'
CSS_AVAILABLE_DATES = '.picker__day.picker__day--infocus:not([aria-disabled="true"])'
XPATH_COOKIE_CONSENT = '//*[@id="acceptAll"]'

TMP_DIRECTORY = 'tmp/'
TXT_EXTENSION = '.txt'
EMAIL_LIST_FILE = 'email_list.json'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
EMAIL_FORMAT = 'html'
EMAIL_SUBJECT_PREFIX = '🎬 Movie Updates: '
EMAIL_SUBJECT_SUFFIX = ' 🎬'

DATE_FORMAT = '%d %b %Y'

ENV_EMAIL = 'EMAIL_GMAIL'
ENV_PASSWORD = 'APP_PASSWORD_GMAIL'
ENV_ERROR_EMAIL = 'ERROR_EMAIL'

ERROR_INVALID_LOCATION = 'INVALID LOCATION'
ERROR_MOVIE_TITLE_LINK = 'ERROR IN MOVIE TITLE LINK'
ERROR_READING_EMAIL_LIST = 'ERROR READING EMAIL LIST'

movie_cache = {} # cache for storing the movie info for each movie
location_cache = {} # cache for storing the email body for each of the locations

#### Web Scraping Functions ####

def _navigate_to_cinema_page(driver, location):
    driver.get(WHATS_ON_LINK)
    select_dropdown_option(driver, DROPDOWN_OPTION, location)

def _extract_movie_titles(driver):
    elements = driver.find_elements(by=By.CLASS_NAME, value=CLASS_INLINE_BLOCK)
    h3_elements = [element for element in elements if element.tag_name == 'h3']
    movies_on_website = []
    for element in h3_elements:
        if element.text != '':
            movies_on_website.append(element.text)
    return movies_on_website

def search_cinema(driver, location):
    _navigate_to_cinema_page(driver, location)
    return _extract_movie_titles(driver)

def select_dropdown_option(driver, select_id, option_id):
    select_element = driver.find_element(By.ID, select_id)
    try:
        option_element = select_element.find_element(By.ID, option_id)
        option_element.click()
    except NoSuchElementException as e:
        send_email([os.environ.get(ENV_ERROR_EMAIL)], ERROR_INVALID_LOCATION, f"Error: {e}")
        driver.close()
        os._exit(0)

def _navigate_to_movie_page(driver, location, movie_url):
    driver.get(movie_url)
    select_dropdown_option(driver, DROPDOWN_OPTION, location)

def _extract_available_dates(driver):
    dates = driver.find_elements(by=By.CSS_SELECTOR, value=CSS_AVAILABLE_DATES)
    available_dates = []
    for date in dates:
        timestamp = int(date.get_attribute('data-pick')) / 1000
        date_obj = datetime.fromtimestamp(timestamp)
        available_dates.append(date_obj.strftime(DATE_FORMAT))
    return available_dates

def _extract_movie_image_url(driver):
    try:
        img_element = driver.find_element(By.CLASS_NAME, CLASS_IMAGE_ROUNDED)
        return img_element.get_attribute('src')
    except Exception:
        return None

def get_movie_info(driver, location, movie_title):
    if movie_title in movie_cache:
        return movie_cache[movie_title]
    
    movie_info = {
        "title": movie_title,
        "dates": [],
        "img": "",
        "link": "",
    }
    movie_title_link = format_movie_title_to_link(movie_title)
    movie_info["link"] = WHATS_ON_LINK + SHOWTIMES_PAGE + movie_title_link
    
    _navigate_to_movie_page(driver, location, movie_info["link"])
    
    movie_info["dates"] = _extract_available_dates(driver)
    movie_info["img"] = _extract_movie_image_url(driver)
    
    if movie_info["img"] is None:
        return None
    
    movie_cache[movie_title] = movie_info
    return movie_info

def wait_and_click(driver, by, value):
    while True:
        try:
            button = driver.find_element(by, value)
            button.click()
            break
        except NoSuchElementException:
            time.sleep(1)

def format_movie_title_to_link(movie_title):
    try:
        if movie_title.endswith(')'):
            movie_title = movie_title[:-1] + '-'
        movie_title = movie_title.replace(" & ", " ")
        movie_title = movie_title.replace("'", "-")
        movie_title = movie_title.replace(":", "")
        movie_title = movie_title.replace("%", "")
        movie_title = movie_title.replace("?", "-")
        movie_title = movie_title.replace(" - ", " ")
        movie_title = movie_title.replace(")", "")
        movie_title = movie_title.replace(",", "")
        movie_title = movie_title.replace("(", "")
        movie_title = movie_title.replace(" ", "-").lower()
    except Exception as e:
        send_email([os.environ.get(ENV_ERROR_EMAIL)], ERROR_MOVIE_TITLE_LINK, f"{movie_title}<br></br><br></br><br></br>Error: {e}")
    return movie_title

#### Reading and Writing to File Functions ####

def get_diff_movies(driver, location):
    movies_on_website = search_cinema(driver, location)
    movies_on_file = read_file_to_arr(location+".txt")
    return [movie for movie in movies_on_website if movie not in movies_on_file], movies_on_website

def write_arr_to_file(arr, filename):
    filepath = TMP_DIRECTORY+filename
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

#### Email Functions ####

def send_email(recipients, subject, body):
    smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) # use Gmail's SMTP server
    sender = os.environ.get(ENV_EMAIL) # sender email
    password = os.environ.get(ENV_PASSWORD) # sender app password
    smtp.login(sender, password)
    for recipient in recipients:
        message = MIMEText(body, EMAIL_FORMAT)
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = recipient
        smtp.sendmail(sender, recipient, message.as_string())
    smtp.quit()

def format_email_body(driver, location, movies):
    body = "<div>\n"
    body += "<h2>New movies at " + location + "</h2>\n"
    for movie in movies:
        movie_info = get_movie_info(driver, location, movie)
        if movie_info != None:
            body += "<div>\n"
            body += "<h3><a href="+movie_info["link"]+">" + movie_info["title"] + "</a></h3>\n"
            body += "<table style='width: 100%; margin-bottom: 20px;'>\n"
            body += "<tr>\n"
            body += "<td style='vertical-align: top; width:160px;'>\n"
            body += '<img src="' + movie_info["img"] + '" alt="' + movie_info["title"] + '" style="width: 150px; height: 225px;">\n'
            body += "</td>\n"
            body += "<td style='vertical-align: top; padding-left: 0;'>\n"
            body += '<ul style="margin: 0; padding: 0; list-style-type: none;">\n'
            for date in movie_info["dates"]:
                body += "<li>" + date + "</li>\n"
            body += "</ul>\n"
            body += "</td>\n"
            body += "</tr>\n"
            body += "</table>\n"
            body += "</div>\n"
        else:
            body += "<div>\n"
            body += "<h3>Unable to access info for " + movie + "</h3>\n"
            body += "</div>\n"
    body += "</div>\n"
    return body

#### Cache Functions ####

def extract_email_info():
    filepath = get_file_from_bucket(EMAIL_LIST_FILE)
    if filepath is None:
        send_email([os.environ.get(ENV_ERROR_EMAIL)], ERROR_READING_EMAIL_LIST, "Error reading email list")
        os._exit(0)
    with open(filepath) as f:
        data = json.load(f)
    locations = [location for item in data for location in item['locations']]
    locations = list(set(locations))
    return data, locations

def _setup_chrome_driver():
    options = ChromeOptions()
    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(BROWSER_TIMEOUT)
    return driver

def _initialise_browser():
    driver = _setup_chrome_driver()
    driver.get(WHATS_ON_LINK)
    wait_and_click(driver, By.XPATH, XPATH_COOKIE_CONSENT)
    return driver

def _process_location(driver, location):
    diff_movies, movies_on_website = get_diff_movies(driver, location)
    if diff_movies:
        load_dotenv()
        location_cache[location] = format_email_body(driver, location, diff_movies)
        write_arr_to_file(movies_on_website, location + TXT_EXTENSION)

def _process_all_locations(driver, locations):
    for location in locations:
        _process_location(driver, location)

def _build_email_body_for_user(user_locations):
    body = ""
    for location in user_locations:
        if location in location_cache and location_cache[location] != "":
            body += location_cache[location]
    return body

def _send_user_email(user_email, user_locations):
    body = _build_email_body_for_user(user_locations)
    if body:
        subject = EMAIL_SUBJECT_PREFIX + datetime.now().strftime(DATE_FORMAT) + EMAIL_SUBJECT_SUFFIX
        send_email([user_email], subject, body)
    else:
        print("no email to send to: " + user_email)

def _send_all_user_emails(email_list):
    for item in email_list:
        _send_user_email(item['email'], item['locations'])

if __name__ == '__main__':
    driver = _initialise_browser()
    try:
        email_list, locations = extract_email_info()
        _process_all_locations(driver, locations)
        driver.close()
        _send_all_user_emails(email_list)
    finally:
        print("finished")