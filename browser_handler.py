import re
from typing import Dict
from typing import List
from datetime import datetime
from utils import format_movie_title_to_link, get_request
from concurrent.futures import ThreadPoolExecutor, as_completed

OMNIPLEX_HOME = 'https://www.omniplexcinemas.co.uk'
DROPDOWN_OPTION = 'homeSelectCinema'
SHOWTIMES_PAGE = '/cinema/showtimes/'
FILTER_DATE_QUERY_PARAM = "?action=processFilters&filterDate="
DATE_FORMAT = '%d %b %Y'
FILTER_DATE_FORMAT = '%Y-%m-%d'
ALLOWED_DATES_REGEX = r'const allowedDatesTimestamps = \.(.*?)'
COMMA = ','
OPEN_SQAURE_BRACKET = '['
MAX_WORKERS = 15

ENV_ERROR_EMAIL = 'ERROR_EMAIL'
ERROR_INVALID_LOCATION = 'INVALID LOCATION'

movie_cache = {}
omniplex_showtime_page = {}

def _form_cinema_url(location: str, date_obj: datetime = None, date_str: str = "") -> str:
    date = date_obj.strftime(FILTER_DATE_FORMAT) if date_obj is not None else date_str
    return OMNIPLEX_HOME + SHOWTIMES_PAGE + location + FILTER_DATE_QUERY_PARAM + date

def _extract_available_dates(omniplex_page: str) -> List[datetime]:
    allowed_dates_str = re.search(r'const allowedDatesTimestamps = (.*?)]', omniplex_page).group(1)
    allowed_dates_str = allowed_dates_str.strip(OPEN_SQAURE_BRACKET)
    allowed_dates = allowed_dates_str.split(COMMA)
    return [datetime.fromtimestamp(int(date) / 1000) for date in allowed_dates]

def _extract_movie_list_from_div(omniplex_page: str) -> List[str]:
    movie_matches = re.findall(r'<a class="p-3 block" href="([^"]+)">([^<]+)</a>',omniplex_page)
    return [{"link": OMNIPLEX_HOME+href, "title": title} for href, title in movie_matches]

def _get_todays_page(location: str):
    if omniplex_showtime_page[location] is None:
        todays_date = datetime.now()
        todays_link = _form_cinema_url(location, date_obj = todays_date)
        return get_request(todays_link)
    else:
        return omniplex_showtime_page[location]

def search_cinema(location: str) -> List[str]:
    pages = []
    omniplex_showtime_page = _get_todays_page(location)
    pages.append(omniplex_showtime_page)
    movies = _extract_movie_list_from_div(omniplex_showtime_page)
    return [movie["title"] for movie in movies]

def _fetch_and_parse_date(location: str, date_obj: datetime) -> Dict:
    date_url = _form_cinema_url(location, date_obj)
    page = get_request(date_url)
    return _get_day_info(page, date_obj.strftime(FILTER_DATE_FORMAT))

def _merge_movies_into(target: Dict, source: Dict):
    for title, movie in source.items():
        if title in target:
            target[title]["times"].update(movie["times"])
        else:
            target[title] = movie

def movies_for_all_dates(location: str) -> Dict:
    omniplex_showtime_page = _get_todays_page(location)
    dates = _extract_available_dates(omniplex_showtime_page)

    movies = _get_day_info(omniplex_showtime_page, datetime.now().strftime(FILTER_DATE_FORMAT))

    with ThreadPoolExecutor(max_workers=len(dates) - 1) as executor:
        pending_dates = {
            executor.submit(_fetch_and_parse_date, location, dates[i]): dates[i]
            for i in range(1, len(dates))
        }
        for completed_date_task in as_completed(pending_dates):
            movies_for_date = completed_date_task.result()
            _merge_movies_into(movies, movies_for_date)

    return movies

def _get_day_info(page: str, date: str):
    movie_divs = page.split('<div class="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-7 xl:grid-cols-10  bg-ompYellow-light/5 shadow-lg backdrop-blur-sm p-4 rounded-lg gap-4 xl:gap-8">')
    movie_divs = movie_divs[1:]

    movies = {}
    for movie_div in movie_divs:
        title_and_url = _extract_movie_and_title(movie_div)
        title = title_and_url[0]["title"]

        showtimes_array = _extract_times_from_per_movie_div(movie_div, title)
        if title in movies:
            movies[title]["times"][date] = showtimes_array
        else:
            movies[title] = {
                "title": title,
                "link": title_and_url[0]["link"],
                "img": _extract_img(movie_div),
                "times": {date: showtimes_array}
            }
    return movies

def _extract_img(movie_div: str):
    return re.search(r'<img\s+src="([^"]+)"', movie_div).group(1)

def _extract_movie_and_title(movie_div: str):
    movie_matches = re.findall(r'<a href="([^"]+)">\s*([^<]+?)\s*</a>', movie_div)
    return [{"link": OMNIPLEX_HOME + href, "title": title} for href, title in movie_matches]

def _extract_times_from_per_movie_div(movie_div: str, movie_title: str) -> Dict:
    showtimes_div = movie_div.split(f'<a aria-label="{movie_title}')
    showtimes_div = showtimes_div[1:]
    
    showtimes = []
    for showtime_div in showtimes_div:
        showtimes.append({
            "start_time": re.search(r'<h4 class="bigText mr-1 leading-none"[^>]*>\s*(\d{2}:\d{2})\s*</h4>', showtime_div).group(1),
            "end_time": re.search(r'<p class="smallText leading-none"[^>]*>\s*-\s*(\d{2}:\d{2})\s*</p>', showtime_div).group(1),
            "screen": re.search(r'<p class="smallText">(.*?)</p>', showtime_div).group(1),
            "link": re.search(r'href="(.*?)" class="">', showtime_div).group(1),
        })
    
    return showtimes

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
    location = "antrim"
    movies = movies_for_all_dates(location)
    print(movies)