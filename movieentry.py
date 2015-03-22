import re
import sys
from datetime import date

import fresh_tomatoes

try:
    import requests
except ImportError:
    print('WARNING! Unable to import the \'requests\' module.\n\tAdvancedMovieEntry objects will not be able to lookup '
          'movie information on the Open Movie Database.\n\tFor more information, see http://docs.python-requests.org/'
          'en/latest/.')

try:
    import bleach
except ImportError:
    print('WARNING! Unable to import the \'bleach\' module.\n\tAdvancedMovieEntry objects use this module to sanitize '
          'HTML output to prevent script injection.\n\tThe module is not required, but you will be trusting your data '
          'to not be malicious.\n\tFor more information, see http://docs.python-requests.org/en/latest/.')


class MovieEntry(object):

    movie_info = {}

    def __init__(self, title, trailer_url, poster_url=None, plot=None, year=None, actors=None,
                 directors=None, get_missing_info=True):

        self.bleach_available = True if 'bleach' in sys.modules else False
        self.requests_available = True if 'requests' in sys.modules else False

        self.movie_info = {'title': None,
                           'trailer_youtube_url': None,
                           'trailer_youtube_id': None,
                           'poster_image_url': None,
                           'plot': None,
                           'year': None,
                           'actors': None,
                           'directors': None}

        self.title = title
        self.trailer_youtube_url = trailer_url

        if poster_url:
            self.poster_image_url = poster_url

        if plot:
            self.plot = plot

        if year:
            self.year = year

        if actors:
            self.actors = actors

        if directors:
            self.directors = directors

        if get_missing_info and self.requests_available:
            self.get_missing_info()

    def __str__(self):
        return str(self.movie_info)

    def clean_output(self, content):

        # If the 'bleach' module is available, use the clean function to make sure the output content is HTML-safe.
        # If it is not available, the content will be trusted as is.

        if self.bleach_available:
            return bleach.clean(content)
        else:
            return content

    def get_missing_info(self):

        # Attempt to fill in any missing information by retrieving it from the Online Movie Database (OMDB) API.
        # Information provided previously by the user will not be over-written. A movie title must be provided for
        # the search to work, and it cannot retrieve a trailer URL.

        if not self.requests_available:
            pass

        if not self.movie_info['title']:
            pass

        # Replace spaces in the title with '+' to format the proper API URL.

        api_title = self.movie_info['title'].lower()
        spaces = re.compile(r'\s')
        api_title = re.sub(spaces, '+', api_title)

        # Attempt the API request.

        try:
            good_response = False

            api_url = 'http://www.omdbapi.com/?t={title}&y=&plot=short&r=json'.format(title=api_title)

            omdb_request = requests.get(api_url)

            if omdb_request.status_code == 200:         # A successful response from OMDB will include a 200 status
                omdb_response = omdb_request.json()     # code and a 'Response' value of True per the API.

                if omdb_response['Response'] == 'True':
                    good_response = True

                if not good_response:
                    print('WARNING! The OMDB API did not find a valid entry for \'%s\'.' % self.movie_info['title'])
                    return

        except KeyError:
            print('WARNING! The OMDB API did not return the expected content for \'%s\'.' % self.movie_info['title'])
            return

        except ValueError:
            print('WARNING! Unable to connect with the OMDB API at %s .' % api_url)
            return

        except:
            print('WARNING! Unable to open an HTTP connection. Are you online?')
            return

        # Identify missing movie information items and replace them with the OMDB response if present.

        if not self.movie_info['plot'] and 'Plot' in omdb_response:
            self.plot = omdb_response['Plot']

        if not self.movie_info['year'] and 'Year' in omdb_response:
            self.year = omdb_response['Year']

        if not self.movie_info['poster_image_url'] and 'Poster' in omdb_response:
            self.poster_image_url = omdb_response['Poster']

        if not self.movie_info['actors'] and 'Actors' in omdb_response:
            self.actors = omdb_response['Actors']

        if not self.movie_info['directors'] and 'Director' in omdb_response:
            self.directors = omdb_response['Director']

    def html(self):

        # Generates the HTML required to display the movie based on the information available.

        plot_content = "<li>{plot}<br/><br/></li>".format(plot=self.plot) if self.plot else ''

        year_content = "<li><strong>Released: </strong>{year}</li>".format(year=self.year) if self.year else ''

        starring_content = "<li><strong>Starring: </strong>{actors}</li>".format(actors=self.generate_name_string(self.actors)) if self.actors else ''

        director_content = "<li><strong>Directed By: </strong>{directors}</li>".format(directors=self.generate_name_string(self.directors)) if self.directors else ''

        tile_content = '''
        <div class="col-md-6 col-lg-4 movie-tile text-center col-md-height col-lg-height" data-trailer-youtube-id="{trailer_youtube_id}" data-toggle="modal" data-target="#trailer">
        <img src="{poster_image_url}" width="220" height="342">
        <h2>{movie_title}</h2>
        <div align="left">
            <ul class="list-unstyled">
                {plot_content}
                {starring_content}
                {director_content}
                {year_content}
            </ul>
        </div>
        </div>
        '''.format(trailer_youtube_id=self.trailer_youtube_id,
                   poster_image_url=self.poster_image_url,
                   movie_title=self.title,
                   plot_content=plot_content,
                   year_content=year_content,
                   starring_content=starring_content,
                   director_content=director_content)

        return tile_content

    # TITLE Property, Setter, and Validation
    # --------------------------------------

    @property
    def title(self):
        return self.clean_output(self.movie_info['title'])

    @title.setter
    def title(self, proposed_title):
        self.movie_info['title'] = self.validate_title(proposed_title)

    def validate_title(self, proposed_title):

        # Ensure that the title is between 1 and 50 characters and does not contain any illegal characters.

        title_filter = re.compile(r'^[A-Za-z0-9 :\'!\.,"-]{1,50}$')

        title_search = re.search(title_filter, proposed_title)

        if title_search:
            return title_search.group(0)
        else:
            print('WARNING! The proposed title \'%s\' is not valid.' % proposed_title)
            return None

    # TRAILER_YOUTUBE_URL and ID Properties, Setters, and Validation
    # --------------------------------------------------------------

    @property
    def trailer_youtube_url(self):
        return self.clean_output(self.movie_info['trailer_youtube_url'])

    @property
    def trailer_youtube_id(self):
        return self.clean_output(self.movie_info['trailer_youtube_id'])

    @trailer_youtube_url.setter
    def trailer_youtube_url(self, proposed_url):
        (self.movie_info['trailer_youtube_url'], youtube_id) = self.validate_youtube_url_extract_id(proposed_url)
        if not self.movie_info['trailer_youtube_id'] and youtube_id:
            self.trailer_youtube_id = youtube_id

    @trailer_youtube_id.setter
    def trailer_youtube_id(self, proposed_id):
        self.movie_info['trailer_youtube_id'] = self.validate_youtube_id(proposed_id)

    def validate_youtube_url_extract_id(self, proposed_url):

        # Validate that the provided URL has a YouTube video ID.  If so, extract that ID from the URL string. Returns
        # a tuple including the URL if its okay and the ID.

        youtube_id_match = re.search(r'(?<=v=)[^&#]+', proposed_url)
        youtube_id_match = youtube_id_match or re.search(r'(?<=be/)[^&#]+', proposed_url)

        trailer_youtube_id = youtube_id_match.group(0) if youtube_id_match else None

        if trailer_youtube_id:
            return proposed_url, trailer_youtube_id
        else:
            print('WARNING! The YouTube URL \'%s\' does not appear valid. It does not contain a valid YouTube ID.')
            return None, None

    def validate_youtube_id(self, proposed_id):

        # Ensure that the proposed YouTube ID consists of 11 alpha-numeric characters.  Otherwise, return None.

        id_filter = re.compile(r'^(\w){11}$')

        id_search = re.search(id_filter, proposed_id)

        if id_search:
            if id_search.group(0) == proposed_id:
                return proposed_id

        print('WARNING! The YouTube id \'%s\' is not valid. It should be 11 alpha-numeric characters.' % proposed_id)
        return None

    # POSTER_URL Property, Setter, and Validation
    # -------------------------------------------

    @property
    def poster_image_url(self):
        return self.clean_output(self.movie_info['poster_image_url'])

    @poster_image_url.setter
    def poster_image_url(self, proposed_url):
        self.movie_info['poster_image_url'] = self.validate_poster_url(proposed_url)

    def validate_poster_url(self, proposed_url):

        # Ensure that the URL is valid. It must begin with http or https and end in a valid image extension.

        image_filter = '^(http|https)://.+\.(png|gif|jpg|jpeg|tif)$'
        image_search = re.search(image_filter, proposed_url)

        if image_search:
            return image_search.group(0)
        else:
            print('WARNING! The poster image URL \'%s\' does not appear valid. It should start with http or https and '
                  'end with a valid image file extension (jpeg, jpg, gif, png, or tif).')
            return None

    # PLOT Property, Setter, and Validation
    # -------------------------------------

    @property
    def plot(self):
        return self.clean_output(self.movie_info['plot'])

    @plot.setter
    def plot(self, proposed_plot):
        self.movie_info['plot'] = self.validate_plot(proposed_plot)

    def validate_plot(self, proposed_plot):

        # Ensure that the provided plot is not empy and less than 300 characters without any invalid characters.

        plot_filter = re.compile(r'^[\w\s\d\.!\,\&-:"\'\\\/\?]{1,300}$')
        plot_search = re.search(plot_filter, proposed_plot)

        if plot_search:
            return plot_search.group(0)
        else:
            print('WARNING! The supplied plot contains illegal characters, or is longer than 300 characters.')
            return None

    # YEAR Property, Setter, and Validation
    # -------------------------------------

    @property
    def year(self):
        return self.clean_output(self.movie_info['year'])

    @year.setter
    def year(self, proposed_year):
        self.movie_info['year'] = self.validate_year(proposed_year)

    def validate_year(self, proposed_year):

        # Ensure that the supplied year is convertible to an integer and between 1900 and two years for now (to handle
        # future releases appropriately).

        try:
            int_year = int(proposed_year)
        except ValueError:
            print('WARNING! The provided year cannot be converted to an integer.')
            return None

        if 1900 <= int_year <= date.today().year + 2:
            return int_year
        else:
            print('WARNING! The move year must be after 1900 and before 2020.')
            return None

    # ACTORS Property, Setter, and Validation
    # ---------------------------------------

    @property
    def actors(self):
        if self.movie_info['actors']:
            return [self.clean_output(name) for name in self.movie_info['actors']]
        else:
            return None

    @actors.setter
    def actors(self, proposed_actors):
        self.movie_info['actors'] = self.validate_name_list(proposed_actors)

    # DIRECTORS Property, Setter, and Validation
    # ------------------------------------------

    @property
    def directors(self):
        if self.movie_info['directors']:
            return [self.clean_output(name) for name in self.movie_info['directors']]
        else:
            return None

    @directors.setter
    def directors(self, proposed_directors):
        self.movie_info['directors'] = self.validate_name_list(proposed_directors)

    def validate_name_list(self, proposed_actors):

        # Takes a string containing a coma separated list of names and splits it into an array of names after verifying
        # that each name is between 1 and 50 valid characters.

        raw_actor_list = proposed_actors.split(',')
        filtered_actor_list = []

        # Validate individual names.

        actor_filter = re.compile(r'[\w\s\'.]{1,50}')

        for actor in raw_actor_list:
            actor_search = re.search(actor_filter, actor.strip())
            if actor_search:
                filtered_actor_list.append(actor_search.group(0))
            else:
                print('WARNING! The name \'%s\' has illegal characters.' % actor)

        # If the list is not empty, return it, otherwise return None.

        if filtered_actor_list:
            return filtered_actor_list
        else:
            return None

    def generate_name_string(self, name_list):
        name_string = ', '.join(name_list)
        return name_string


if __name__ == '__main__':

    movies = [MovieEntry(title='Safety Not Guaranteed', trailer_url='https://youtu.be/73jSnAs7mq8'),
              MovieEntry(title='History of Future Folk', trailer_url='https://youtu.be/fZrDALCsKwI'),
              MovieEntry(title='Knights of Badassdom', trailer_url='https://youtu.be/tOsGwkUR7Lk'),
              MovieEntry(title='Serenity', trailer_url='https://youtu.be/JY3u7bB7dZk'),
              MovieEntry(title='Why Don\'t You Play in Hell', trailer_url='https://youtu.be/sI3KaCUKqFY'),
              MovieEntry(title='The Princess Bride', trailer_url='https://youtu.be/VYgcrny2hRs'),
              MovieEntry(title='Glory', trailer_url='https://youtu.be/5NieVt4D75I')]

    fresh_tomatoes.open_movies_page(movies)