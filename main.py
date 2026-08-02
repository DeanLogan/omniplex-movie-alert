from dotenv import load_dotenv
from browser_handler import search_cinema
from file_handler import extract_email_info, write_arr_to_file, read_file_to_arr
from email_handler import format_email_body, send_all_user_emails, location_cache

TXT_EXTENSION = '.txt'

def get_diff_movies(location):
    movies_on_website = search_cinema(location)
    movies_on_file = read_file_to_arr(location + ".txt")
    return [movie for movie in movies_on_website if movie not in movies_on_file], movies_on_website

def process_location(location):
    diff_movies, movies_on_website = get_diff_movies(location)
    if diff_movies:
        load_dotenv()
        location_cache[location] = format_email_body(location, diff_movies)
        write_arr_to_file(movies_on_website, location + TXT_EXTENSION)

def process_all_locations(locations):
    print("checking locations: ", locations)
    for location in locations:
        process_location(location)

def main():
    try:
        email_list, locations = extract_email_info()
        process_all_locations(locations)
        send_all_user_emails(email_list)
    finally:
        print("finished")

if __name__ == '__main__':
    main()
