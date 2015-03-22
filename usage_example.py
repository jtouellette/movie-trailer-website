from movieentry import MovieEntry
import fresh_tomatoes

# Create a movie entry with the minimum amount of information required, which is the movie's title and
# URL to its YouTube.  Fill in the rest automatically.

movie_one = MovieEntry(title='Safety Not Guaranteed',
                       trailer_url='https://youtu.be/73jSnAs7mq8')

# Create a movie entry by manually using only the minimum amount of data needed to display properly, without
# attempting to fill in the rest.

movie_two = MovieEntry(title='History of Future Folk',
                       trailer_url='https://youtu.be/fZrDALCsKwI',
                       poster_url='http://ia.media-imdb.com/images/M/MV5BNzA3MDI3MzAxMl5BMl5BanBnXkFtZTcwNDY2Mjc0OQ@@._V1_SX300.jpg',
                       get_missing_info=False)

# Create a movie entry by manually setting all movie properties when the class is constructed.

movie_three = MovieEntry(title='Knights of Badassdom',
                         trailer_url='https://youtu.be/tOsGwkUR7Lk',
                         poster_url='http://ia.media-imdb.com/images/M/MV5BMjMyNzAyNzUzMF5BMl5BanBnXkFtZTgwOTQ0NDMyMTE@._V1_SX300.jpg',
                         plot='''
                                Live-action role players conjure up a demon from Hell by mistake and they must deal
                                with the consequences.
                              ''',
                         year=2013,
                         actors='D.R. Anderson, W. Earl Brown, Michael Carpenter, Kevin Connell',
                         directors='Joe Lynch',
                         get_missing_info=False)

# Create a movie with the minimum required information, then fill in the rest later manually.

movie_four = MovieEntry(title='Serenity',
                        trailer_url='https://youtu.be/JY3u7bB7dZk',
                        get_missing_info=False)

movie_four.poster_image_url = 'http://ia.media-imdb.com/images/M/MV5BMTI0NTY1MzY4NV5BMl5BanBnXkFtZTcwNTczODAzMQ@@._V1_SX300.jpg'
movie_four.plot = 'The crew of the ship Serenity tries to evade an assassin sent to recapture one of their number who is telepathic.'
movie_four.actors = 'Nathan Fillion, Gina Torres, Alan Tudyk, Morena Baccarin'
movie_four.year = 2005

# Oops, we don't know the director for Serenity. Retrieve it from OMDB.

movie_four.get_missing_info()

# MovieEntry objects must be pass to the Fresh Tomatoes script as a list:

my_movie_list = [movie_one, movie_two, movie_three, movie_four]

# Display the page.

fresh_tomatoes.open_movies_page(movies=my_movie_list)