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

def _get_day_info(page: str, date: str):
    movie_divs = page.split('<div class="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-7 xl:grid-cols-10  bg-ompYellow-light/5 shadow-lg backdrop-blur-sm p-4 rounded-lg gap-4 xl:gap-8">')
    movie_divs = movie_divs[1:]

    movies = {}
    for movie_div in movie_divs:
        title_and_url = _extract_movie_and_title(movie_div)
        title = title_and_url[0]["title"]

        movies[title] = {
            "title": title,
            "link": title_and_url[0]["link"],
            "img": _extract_img(movie_div),
            "times": _extract_times_from_per_movie_div(movie_div, title, date)
        }
    return movies

def _extract_img(movie_div: str):
    return re.search(r'<img\s+src="([^"]+)"', movie_div).group(1)

def _extract_movie_and_title(movie_div: str):
    movie_matches = re.findall(r'<a href="([^"]+)">\s*([^<]+?)\s*</a>', movie_div)
    return [{"link": OMNIPLEX_HOME + href, "title": title} for href, title in movie_matches]

def _extract_times_from_per_movie_div(movie_div: str, movie_title: str, date: str):
    showtimes_div = movie_div.split(f'<a aria-label="{movie_title}')
    showtimes_div = showtimes_div[1:]
    
    showtimes = []
    for showtime_div in showtimes_div:
        showtimes.append({
            "start_time": re.search(r'<h4 class="bigText mr-1 leading-none"[^>]*>\s*(\d{2}:\d{2})\s*</h4>', showtime_div).group(1),
            "end_time": re.search(r'<p class="smallText leading-none"[^>]*>\s*-\s*(\d{2}:\d{2})\s*</p>', showtime_div).group(1),
            "screen": re.search(r'<p class="smallText">(.*?)</p>', showtime_div).group(1),
            "link": re.search(r'href="(.*?)" class="">', showtime_div).group(1),
            "date": date
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


def _combine_day_info(day1, day2):
    combined = {}
    combined["title"] = day1["title"]
    combined["link"] = day1["link"]
    combined["img"] = day1["img"]
    combined["times"] = day1["times"] + day2["times"]
    return combined

if __name__ == "__main__":
    day1 = get_request("https://www.omniplexcinemas.co.uk//cinema/showtimes/antrim?action=processFilters&filterDate=2026-08-03")
    movies1 = _get_day_info(day1, "2026-08-03")
    day2 = get_request("https://www.omniplexcinemas.co.uk//cinema/showtimes/antrim?action=processFilters&filterDate=2026-08-04")
    movies2 = _get_day_info(day2, "2026-08-04")

    day_movie_info = [movies1, movies2]

    movies = {}
    for day in day_movie_info:
        for (key, value) in day.items():
            if key in movies:
                movies = _combine_day_info(movies[key], value)
            else:
                movies[key] = value
    print(movies)