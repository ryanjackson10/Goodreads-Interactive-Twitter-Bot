from goodreads import client
import random
import tweepy
import time

gc = client.GoodreadsClient('', '')

# base for the bot is thanks to ykdojo, whose tutorial can be found on YouTube

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit = True)

mentions = api.mentions_timeline()

tweetID_file = 'last_seen_id.txt'

def get_last_id(file):
    f_read = open(file, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file):
    f_write = open(file, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def generateAuthors(book):
    # just the book.authors method returns a list, with incorrect punctuation if there's more than
    # one author
    list_of_authors = book.authors
    if len(list_of_authors) == 1:
        return "".join(str(author) for author in list_of_authors)
    elif len(list_of_authors) == 2:
        return " and ".join(str(author) for author in list_of_authors)
    else:
        list_of_authors.insert(-1, 'and')
        array = ", ".join(str(author) for author in list_of_authors)
        new_array = array.replace('and,', 'and', 1)
        # getting rid of superfluous comma
        return new_array

def genbook(id_number):
    try:
        possible_book = gc.book(id_number)
        isbn = possible_book.isbn
        dataset = gc.book_review_stats([str(isbn)])
        for data in dataset:
            rating_count = data['work_ratings_count']
        possible_average_rating = possible_book.average_rating
        popular_shelves = possible_book.popular_shelves
        # goodreads doesn't sort by genre, so we have to rely on user generated bookshelves
        popular_shelves_string = [str(i) for i in popular_shelves]
        if keyword in popular_shelves_string[0:30] and 100 < int(rating_count) < 20000 and float(possible_average_rating) > 4.1:
            return possible_book
        else:
            return genbook(random.randint(1, 15000))
    except Exception:
        return genbook(random.randint(1, 15000))

keyword = None # to become global in reply_to_tweets function

def reply_to_tweets():
    print('checking mentions...')

    last_seen_id = get_last_id(tweetID_file)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode = 'extended')


    genres = ['poetry', 'fantasy', 'non-fiction', 'nonfiction' 'drama', 'science'
    'history', 'fiction', 'horror', 'suspense', 'crime', 'politics', 'philosophy', 'economics']


    for mention in reversed(mentions):
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, tweetID_file)
        for i in genres:
            if i in mention.full_text.lower():
                hasKeyword = True
                global keyword
                keyword = i
                break
            else:
                hasKeyword = False
        try:
            # unfortunately goodreads doesn't sort its entries by genre, so we to randomly search
            # entries to see if readers have stored the book on a shelf with the same name as the keyword
            daily_book = genbook(random.randint(1, 150000))
            # most books after the 150,000th entry rarely have more than a few ratings, and would be wasteful
            # to look through
            book_data = gc.book_review_stats([str(daily_book.isbn)])
            daily_book_average_rating = daily_book.average_rating
            for data in book_data:
                ratings_count = data['work_ratings_count']
            daily_book_authors = generateAuthors(daily_book)
            # calling a seperate function for the authors because the daily_book.authors method returns a list
            # with poor punctuation
            if hasKeyword is True:
                api.update_status('@' + mention.user.screen_name + f' With an average rating of {daily_book_average_rating} from {ratings_count} readers, your underrated {keyword} book is \'{daily_book}\' by {daily_book_authors}!', mention.id)
            elif hasKeyword is False:
                api.update_status('@' + mention.user.screen_name + f' It like there aren\'t any genres in your tweet. Check our bio for applicable genres!', mention.id)
        except Exception:
            return reply_to_tweets()


while True:
    reply_to_tweets()
    time.sleep(120)
