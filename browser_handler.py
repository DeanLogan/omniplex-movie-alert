import os
import sys
from typing import List
import re
from datetime import datetime
from utils import format_movie_title_to_link, get_request

OMNIPLEX_HOME = 'https://www.omniplexcinemas.co.uk/'
DROPDOWN_OPTION = 'homeSelectCinema'
SHOWTIMES_PAGE = '/cinema/showtimes/'
FILTER_DATE_QUERY_PARAM = "?action=processFilters&filterDate="
DATE_FORMAT = '%d %b %Y'
FILTER_DATE_FORMAT = '%Y-%m-%d'
ALLOWED_DATES_REGEX = r'const allowedDatesTimestamps = \.(.*?)'
COMMA = ','
OPEN_SQAURE_BRACKET = '['

ENV_ERROR_EMAIL = 'ERROR_EMAIL'
ERROR_INVALID_LOCATION = 'INVALID LOCATION'

movie_cache = {}

def _form_cinema_url(location: str, date_obj: datetime) -> str:
    return OMNIPLEX_HOME + SHOWTIMES_PAGE + location + FILTER_DATE_QUERY_PARAM + date_obj.strftime(FILTER_DATE_FORMAT)

def _extract_available_dates(omniplex_page: str) -> List[datetime]:
    allowed_dates_str = re.search(r'const allowedDatesTimestamps = (.*?)]', omniplex_page).group(1)
    allowed_dates_str = allowed_dates_str.strip(OPEN_SQAURE_BRACKET)
    allowed_dates = allowed_dates_str.split(COMMA)
    return [datetime.fromtimestamp(int(date) / 1000).strftime(FILTER_DATE_FORMAT) for date in allowed_dates]

def _extract_movie_titles():
    return None
    # elements = driver.find_elements(by=By.CLASS_NAME, value=CLASS_INLINE_BLOCK)
    # h3_elements = [element for element in elements if element.tag_name == 'h3']
    # movies_on_website = []
    # for element in h3_elements:
    #     if element.text != '':
    #         movies_on_website.append(element.text)
    # return movies_on_website

def search_cinema(location):
    todays_date = datetime.now()
    todays_link = _form_cinema_url(location, todays_date)
    omniplex_showtime_page = get_request(todays_link)
    dates = _extract_available_dates(omniplex_showtime_page)
    print(dates)
    return _extract_movie_titles()

def _extract_movie_image_url():
    return None
    # try:
    #     img_element = driver.find_element(By.CLASS_NAME, CLASS_IMAGE_ROUNDED)
    #     return img_element.get_attribute('src')
    # except Exception:
    #     return None

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
    movie_info["link"] = OMNIPLEX_HOME + SHOWTIMES_PAGE + movie_title_link
    
    # _navigate_to_movie_page(location, movie_info["link"])
    
    movie_info["dates"] = _extract_available_dates()
    movie_info["img"] = _extract_movie_image_url()
    
    if movie_info["img"] is None:
        return None
    
    movie_cache[movie_title] = movie_info
    return movie_info


if __name__ == "__main__":
    search_cinema("antrim")