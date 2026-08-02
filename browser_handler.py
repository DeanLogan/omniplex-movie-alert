import os
import sys
import time
from datetime import datetime
from utils import format_movie_title_to_link

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

def _navigate_to_cinema_page(location):
    return None

def _extract_movie_titles():
    elements = driver.find_elements(by=By.CLASS_NAME, value=CLASS_INLINE_BLOCK)
    h3_elements = [element for element in elements if element.tag_name == 'h3']
    movies_on_website = []
    for element in h3_elements:
        if element.text != '':
            movies_on_website.append(element.text)
    return movies_on_website

def search_cinema(location):
    _navigate_to_cinema_page(location)
    return _extract_movie_titles()

def _extract_available_dates():
    dates = _wait_for_elements(By.CSS_SELECTOR, CSS_AVAILABLE_DATES)
    available_dates = []
    for date in dates:
        timestamp = int(date.get_attribute('data-pick')) / 1000
        date_obj = datetime.fromtimestamp(timestamp)
        available_dates.append(date_obj.strftime(DATE_FORMAT))
    return available_dates

def _extract_movie_image_url():
    try:
        img_element = driver.find_element(By.CLASS_NAME, CLASS_IMAGE_ROUNDED)
        return img_element.get_attribute('src')
    except Exception:
        return None

def get_movie_info(location, movie_title):
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
    
    _navigate_to_movie_page(location, movie_info["link"])
    
    movie_info["dates"] = _extract_available_dates()
    movie_info["img"] = _extract_movie_image_url()
    
    if movie_info["img"] is None:
        return None
    
    movie_cache[movie_title] = movie_info
    return movie_info
