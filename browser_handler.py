import re
from typing import List
from datetime import datetime
from utils import format_movie_title_to_link, get_request

OMNIPLEX_HOME = 'https://www.omniplexcinemas.co.uk'
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
omniplex_showtime_page = None

def _form_cinema_url(location: str, date_obj: datetime) -> str:
    return OMNIPLEX_HOME + SHOWTIMES_PAGE + location + FILTER_DATE_QUERY_PARAM + date_obj.strftime(FILTER_DATE_FORMAT)

def _extract_available_dates(omniplex_page: str) -> List[datetime]:
    allowed_dates_str = re.search(r'const allowedDatesTimestamps = (.*?)]', omniplex_page).group(1)
    allowed_dates_str = allowed_dates_str.strip(OPEN_SQAURE_BRACKET)
    allowed_dates = allowed_dates_str.split(COMMA)
    return [datetime.fromtimestamp(int(date) / 1000) for date in allowed_dates]

def _extract_movie_list_from_div(omniplex_page: str) -> List[str]:
    movie_matches = re.findall(r'<a class="p-3 block" href="([^"]+)">([^<]+)</a>',omniplex_page)
    return [{"link": OMNIPLEX_HOME+href, "title": title} for href, title in movie_matches]

def search_cinema(location: str) -> List[str]:
    pages = []

    todays_date = datetime.now()
    todays_link = _form_cinema_url(location, todays_date)
    omniplex_showtime_page = get_request(todays_link)

    pages.append(omniplex_showtime_page)

    movies = _extract_movie_list_from_div(omniplex_showtime_page)
    return [movie["title"] for movie in movies]

def movies_for_all_dates(location):
    all_pages = []
    dates = _extract_available_dates(omniplex_showtime_page)
    for i in range(1, len(dates)):
        date_url = _form_cinema_url(location, dates[i])
        all_pages.append(get_request(date_url))
    return all_pages

def _extract_times_from_per_movie_div(page: str):
    movie_list_div = re.findall(
        r'<div id="perf_" class="showTimeBox bg-ompGray-times p-2 col-span-1 rounded-xl">(.*?)</div>',
        page,
        re.DOTALL
    ).group(1)
    print(movie_list_div)

def _extract_movie_image_url():
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