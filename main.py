import os
import time
import smtplib
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

#### Web Scraping Functions ####

def search_cinema(driver, location):
    driver.get('https://www.omniplex.ie/whatson')
    # click cookie agreement
    wait_and_click(driver, By.XPATH, '//*[@id="acceptAll"]')
    # getting location dropdown
    select_dropdown_option(driver, 'homeSelectCinema', location)
    elements = driver.find_elements(by=By.CLASS_NAME, value="OMP_inlineBlock")
    h3_elements = [element for element in elements if element.tag_name == 'h3']
    movies_on_website = []
    for element in h3_elements:
        if element.text != '':
            movies_on_website.append(element.text)
    return movies_on_website

def get_movie_info(driver, location, movie_title):
    movie_info = {
        "title": movie_title,
        "dates": [],
        "img": "",
        "link": "",
    }
    movie_title_link = format_movie_title_to_link(movie_title)
    movie_info["link"] = 'https://www.omniplex.ie/whatson/movie/showtimes/'+movie_title_link
    driver.get(movie_info["link"])
    select_dropdown_option(driver, 'homeSelectCinema', location)
    wait_and_click(driver, By.XPATH, '/html/body/div[9]/div[1]/div/div/div/div/div/a[8]/span')
    dates = driver.find_elements(by=By.CSS_SELECTOR, value=".picker__day.picker__day--infocus:not([aria-disabled='true'])")
    available_dates = []
    for date in dates:
        dateObj = datetime.fromtimestamp(int(date.get_attribute('data-pick')) / 1000)
        available_dates.append(dateObj.strftime('%d %b %Y'))
    movie_info["dates"] = available_dates
    img_element = driver.find_element(By.CLASS_NAME, 'OMP_imageRounded')
    movie_info["img"] = img_element.get_attribute('src')
    return movie_info

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

def format_movie_title_to_link(movie_title):
    movie_title = movie_title.replace(" ", "-").lower()
    movie_title = movie_title.replace(":", "")
    movie_title = movie_title.replace(")", "-")
    movie_title = movie_title.replace("(", "")
    return movie_title

#### Reading and Writing to File Functions ####

def get_diff_movies(driver, location):
    movies_on_website = search_cinema(driver, location)
    movies_on_file = read_file_to_arr("movie_list_"+location+".txt")
    return [movie for movie in movies_on_website if movie not in movies_on_file]

def write_arr_to_file(arr, filename):
    with open(filename, 'w') as f:
        for s in arr:
            f.write(s + '\n')

def read_file_to_arr(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

#### Email Functions ####

def send_email(recipient, body):
    sender = os.environ.get('EMAIL_GMAIL') # sender email
    password = os.environ.get('APP_PASSWORD_GMAIL')
    message = MIMEText(body, 'html')
    message['Subject'] = "🎬 Movie Updates for " + datetime.now().strftime('%d %b %Y') + " 🎬"
    message['From'] = sender
    message['To'] = recipient
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465) # use Gmail's SMTP server
    smtp.login(sender, password)
    smtp.sendmail(sender, recipient, message.as_string())
    smtp.quit()

def format_email_body(driver, location, movies):
    body = "<div>\n"
    body += "<h2>New movies at " + location + "</h2>\n"
    for movie in movies:
        movie_info = get_movie_info(driver, location, movie)
        body += "<div>\n"
        body += "<a href="+movie_info["link"]+"><h3>" + movie_info["title"] + "</h3></a>\n"
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
    body += "</div>\n"
    return body

def main():
    options = FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    location = "carrickfergus"
    diff_movies = get_diff_movies(driver, location)
    if diff_movies:
        load_dotenv()
        body = format_email_body(driver, location, diff_movies)
        send_email(os.environ.get('RECIPIENT'), body)
        # write_arr_to_file(diff_movies, "movie_list_"+location+".txt")
    driver.close()

if __name__ == '__main__':
    main()