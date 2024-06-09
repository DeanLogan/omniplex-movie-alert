import asyncio
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
import time
import os

os.environ['PYPPETEER_HOME'] = 'path/to/your/chromium/directory'

async def fetch_movies(location):
    session = AsyncHTMLSession()
    url = 'https://www.omniplex.ie/whatson'
    response = await session.get(url)

    # Enable JavaScript rendering
    await response.html.arender()

    # Interact with the dropdown to select the location
    dropdown_script = f"""
        document.getElementById('homeSelectCinema').value = '{location}';
        document.getElementById('homeSelectCinema').dispatchEvent(new Event('change'));
    """
    await response.html.page.evaluate(dropdown_script)
    time.sleep(2)  # Wait for the JavaScript to update the content
    updated_html =  response.html.content

    # Parse the updated HTML
    soup = BeautifulSoup(updated_html, 'html.parser')
    movies_on_website = []
    elements = soup.find_all(class_="OMP_inlineBlock")
    h3_elements = [element for element in elements if element.name == 'h3']
    for element in h3_elements:
        if element.text.strip():
            movies_on_website.append(element.text.strip())

    return movies_on_website

async def search_cinema(location):
    movies = await fetch_movies(location)
    return movies

# Example usage
location = 'carrickfergus'
movies = asyncio.run(search_cinema(location))
print(movies)