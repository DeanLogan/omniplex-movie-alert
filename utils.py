import os

ENV_ERROR_EMAIL = 'ERROR_EMAIL'
ERROR_MOVIE_TITLE_LINK = 'ERROR IN MOVIE TITLE LINK'

def format_movie_title_to_link(movie_title):
    try:
        if movie_title.endswith(')'):
            movie_title = movie_title[:-1] + '-'
        
        movie_title = movie_title.replace(" & ", " ")
        movie_title = movie_title.replace("'", "-")
        movie_title = movie_title.replace(":", "")
        movie_title = movie_title.replace("%", "")
        movie_title = movie_title.replace("?", "-")
        movie_title = movie_title.replace(" - ", " ")
        movie_title = movie_title.replace(")", "")
        movie_title = movie_title.replace(",", "")
        movie_title = movie_title.replace("(", "")
        movie_title = movie_title.replace(" ", "-").lower()
    except Exception as e:
        from email_handler import send_email
        send_email([os.environ.get(ENV_ERROR_EMAIL)], ERROR_MOVIE_TITLE_LINK, f"{movie_title}<br></br><br></br><br></br>Error: {e}")
    return movie_title
