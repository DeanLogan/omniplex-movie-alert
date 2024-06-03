import os
import time
import smtplib
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

def search_cinema(driver, location):
    driver.get('https://www.omniplex.ie/whatson')
    # click cookie agreement
    print("clicking cookie agreement")
    wait_and_click(driver, By.XPATH, '//*[@id="acceptAll"]')
    print("clicking cinema selection")
    select_dropdown_option(driver, 'homeSelectCinema', location)
    elements = driver.find_elements(by=By.CLASS_NAME, value="OMP_inlineBlock")
    h3_elements = [element for element in elements if element.tag_name == 'h3']
    movies_on_website = []
    for element in h3_elements:
        if element.text != '':
            movies_on_website.append(element.text)
    return movies_on_website


def get_diff_movies(driver, location):
    movies_on_website = search_cinema(driver, location)
    movies_on_file = read_file_to_arr("movie_list_"+location+".txt")
    return [movie for movie in movies_on_website if movie not in movies_on_file]

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
    option_element = select_element.find_element(By.ID, option_id)
    option_element.click()

def write_arr_to_file(arr, filename):
    with open(filename, 'w') as f:
        for s in arr:
            f.write(s + '\n')

def read_file_to_arr(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def send_email(recipient, body):
    load_dotenv()
    sender = os.environ.get('EMAIL_GMAIL') # sender email
    password = os.environ.get('APP_PASSWORD_GMAIL')
    message = MIMEText(body)
    message['Subject'] = "Movie Updates"
    message['From'] = sender
    message['To'] = recipient
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465) # use Gmail's SMTP server
    smtp.login(sender, password)
    smtp.sendmail(sender, [recipient], message.as_string())
    smtp.quit()

def format_movie_title_to_link(movie_title):
    movie_title = movie_title.replace(" ", "-").lower()
    movie_title = movie_title.replace(":", "")
    movie_title = movie_title.replace(")", "-")
    movie_title = movie_title.replace("(", "")
    return movie_title

def get_movie_dates(driver, location, movie_title):
    movie_title_link = format_movie_title_to_link(movie_title)
    driver.get('https://www.omniplex.ie/whatson/movie/showtimes/'+movie_title_link)
    select_dropdown_option(driver, 'homeSelectCinema', location)
    print("clicking date selection")
    wait_and_click(driver, By.XPATH, '/html/body/div[9]/div[1]/div/div/div/div/div/a[8]/span')
    print("clicked date selection")
    dates = driver.find_elements(by=By.CSS_SELECTOR, value=".picker__day.picker__day--infocus:not([aria-disabled='true'])")
    available_dates = []
    for date in dates:
        dateObj = datetime.fromtimestamp(int(date.get_attribute('data-pick')) / 1000)
        available_dates.append(dateObj.strftime('%d %b %Y'))
    print(available_dates)

def main():
    driver = webdriver.Firefox()
    location = "carrickfergus"
    diff_movies = get_diff_movies(driver, location)
    if diff_movies:
        get_movie_dates(driver, location, diff_movies[0])
        # write_arr_to_file(diff_movies, "movie_list_"+location+".txt")
        # send_email(os.environ.get('RECIPIENT'), "New movies available: " + ', '.join(diff_movies))
    driver.close()

if __name__ == '__main__':
    main()