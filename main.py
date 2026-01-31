from dotenv import load_dotenv
from browser_handler import initialize_browser
from file_handler import extract_email_info, get_diff_movies, write_arr_to_file
from email_handler import format_email_body, send_all_user_emails, location_cache

TXT_EXTENSION = '.txt'

def process_location(driver, location):
    diff_movies, movies_on_website = get_diff_movies(driver, location)
    if diff_movies:
        load_dotenv()
        location_cache[location] = format_email_body(driver, location, diff_movies)
        write_arr_to_file(movies_on_website, location + TXT_EXTENSION)

def process_all_locations(driver, locations):
    print("checking locations: ", locations)
    for location in locations:
        process_location(driver, location)

def main():
    driver = initialize_browser()
    
    try:
        email_list, locations = extract_email_info()
        process_all_locations(driver, locations)
        driver.close()
        send_all_user_emails(email_list)
    finally:
        print("finished")

if __name__ == '__main__':
    main()
