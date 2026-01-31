import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils import format_movie_title_to_link
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions

BROWSER_TIMEOUT = 30
WHATS_ON_LINK = 'https://www.omniplex.ie/whatson'
DROPDOWN_OPTION = 'homeSelectCinema'
SHOWTIMES_PAGE = '/movie/showtimes/'
CLASS_INLINE_BLOCK = 'OMP_inlineBlock'
CLASS_IMAGE_ROUNDED = 'OMP_imageRounded'
CSS_AVAILABLE_DATES = '.picker__day.picker__day--infocus:not([aria-disabled="true"])'
XPATH_COOKIE_CONSENT = '//*[@id="acceptAll"]'
DATE_FORMAT = '%d %b %Y'
ENV_ERROR_EMAIL = 'ERROR_EMAIL'
ERROR_INVALID_LOCATION = 'INVALID LOCATION'

movie_cache = {}

def _setup_chrome_driver():
    options = ChromeOptions()
    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(BROWSER_TIMEOUT)
    return driver

def initialize_browser():
    print("starting")
    driver = _setup_chrome_driver()
    driver.get(WHATS_ON_LINK)
    print("waiting for cookie consent")
    wait_and_click(driver, By.XPATH, XPATH_COOKIE_CONSENT)
    return driver

def wait_and_click(driver, by, value):
    while True:
        try:
            button = driver.find_element(by, value)
            button.click()
            break
        except NoSuchElementException:
            time.sleep(1)

def select_dropdown_option(driver, select_id, option_id):
    select_element = driver.find_element(By.ID, select_id)
    try:
        option_element = select_element.find_element(By.ID, option_id)
        option_element.click()
    except NoSuchElementException as e:
        from email_handler import send_email
        send_email([os.environ.get(ENV_ERROR_EMAIL)], ERROR_INVALID_LOCATION, f"Error: {e}")
        driver.close()
        os._exit(0)

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
