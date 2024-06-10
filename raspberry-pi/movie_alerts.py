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
    # getting location dropdown
    select_dropdown_option(driver, 'homeSelectCinema', location)
    elements = driver.find_elements(by=By.CLASS_NAME, value="OMP_inlineBlock")
    h3_elements = [element for element in elements if element.tag_name == 'h3']
    movies_on_website = []
    for element in h3_elements:
        if element.text != '':
            movies_on_website.append(element.text)
    return movies_on_website

def select_dropdown_option(driver, select_id, option_id):
    select_element = driver.find_element(By.ID, select_id)
    option_element = select_element.find_element(By.ID, option_id)
    option_element.click()

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

def format_movie_title_to_link(movie_title):
    try:
        if movie_title.endswith(')'):
            movie_title = movie_title[:-1] + '-'
        movie_title = movie_title.replace(" & ", " ")
        movie_title = movie_title.replace("'", "-")
        movie_title = movie_title.replace(":", "")
        movie_title = movie_title.replace(")", "")
        movie_title = movie_title.replace("(", "")
        movie_title = movie_title.replace(" ", "-").lower()
    except Exception as e:
        send_email(["deanlogan42@gmail.com"], "ERROR IN MOVIE TITLE LINK", f"{movie_title}<br></br><br></br><br></br>Error: {e}")
    return movie_title

#### Reading and Writing to File Functions ####

def get_diff_movies(driver, location):
    movies_on_website = search_cinema(driver, location)
    print(movies_on_website)
    movies_on_file = read_file_to_arr(location+".txt")
    print(movies_on_file)
    return [movie for movie in movies_on_website if movie not in movies_on_file], movies_on_website

def write_arr_to_file(arr, filename):
    with open(filename, 'w') as f:
        for s in arr:
            f.write(s + '\n')

def read_file_to_arr(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

#### Email Functions ####

def send_email(recipients, subject, body):
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465) # use Gmail's SMTP server
    sender = os.environ.get('EMAIL_GMAIL') # sender email
    password = os.environ.get('APP_PASSWORD_GMAIL')
    smtp.login(sender, password)
    for recipient in recipients:
        message = MIMEText(body, 'html')
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = recipient
        smtp.sendmail(sender, recipient, message.as_string())
    smtp.quit()

def format_email_body(driver, location, movies):
    body = "<div>\n"
    body += "<h2>New movies at " + location + "</h2>\n"
    for movie in movies:
        movie_info = get_movie_info(driver, location, movie)
        body += "<div>\n"
        body += "<h3><a href="+movie_info["link"]+">" + movie_info["title"] + "</a></h3>\n"
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
    print("starting")
    # opens browser in headless mode and navigates to omniplex website to click on cookie consent
    options = FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get('https://www.omniplex.ie/whatson')
    print("wating for cookie consent")
    wait_and_click(driver, By.XPATH, '//*[@id="acceptAll"]')
    # check locations for new movies
    locations = ["larne"]
    body = ""
    print("checking locations: ", locations)
    for location in locations:
        diff_movies, movies_on_website = get_diff_movies(driver, location)
        if diff_movies:
            load_dotenv()
            body += format_email_body(driver, location, diff_movies)
            # write_arr_to_file(movies_on_website, location+".txt")
    driver.close()
    if body:
        recipients = [os.environ.get('EMAIL_GMAIL')]
        send_email(recipients, "🎬 Movie Updates: " + datetime.now().strftime('%d %b %Y') + " 🎬", body)

if __name__ == '__main__':
    main()