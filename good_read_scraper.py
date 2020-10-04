import random
import time
import json
import os
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

"""Sets up MongoDB Atlas connection by pulling files from .env file"""
USER = os.getenv('USER')
DB_PASSWORD = os.getenv('PASSWORD')
DB_NAME = os.getenv('DATABASENAME')
client = MongoClient(
    "mongodb+srv://" + USER + ":" + DB_PASSWORD+"@assignment-2-goodreads.bpcru.mongodb.net/"+DB_NAME+"?retryWrites=true&w=majority")
db = client.get_database(DB_NAME)
author_collection = db['Authors']
book_collection = db['Books']
author_and_book_collection = db['Authors_and_Books']


class ComplexEncoder(json.JSONEncoder):
    """ Format complex json object"""
    """ Used from https://docs.python.org/2/library/json.html"""

    def default(self, obj):
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


book_jsons = []
author_jsons = []


def convert_to_json_book_obj(book_meta):
    """
    Formats the given information of the book into a json object
    """
    book_object = {
        'book_url': book_meta.get('book_url'),
        'title': book_meta.get('title'),
        'book_id': book_meta.get('book_id'),
        'ISBN': book_meta.get('ISBN'),
        'author': book_meta.get('author'),
        'author_url': book_meta.get('author_url'),
        'rating': book_meta.get('rating'),
        'rating_count': book_meta.get('rating_count'),
        'review_count': book_meta.get('review_count'),
        'image_url': book_meta.get('image_url'),
        'similar_books': book_meta.get('similar_books')
    }
    book_jsons.append(book_object)

    # print(json.dumps(bookObject, indent=4))


def convert_to_json_author_obj(author_meta):
    """
    Converts the author data to a json object
    """
    author_object = {
        'name': author_meta.get('name'),
        'author_url': author_meta.get('author_url'),
        'author_id': author_meta.get('author_id'),
        'rating': author_meta.get('rating'),
        'rating_count': author_meta.get('rating_count'),
        'review_count': author_meta.get('review_count'),
        'image_url': author_meta.get('image_url'),
        'related_authors': author_meta.get('related_authors'),
        'author_books': author_meta.get('author_books')
    }
    author_jsons.append(author_object)
    # print(json.dumps(authorJson, indent=4))


def add_to_db():
    """Add json files to 3 different collections; Author, Book, and Author_and_Books"""
    with open('authors.json') as f_authors:
        author_data = json.load(f_authors)
    if isinstance(author_data, list):
        author_collection.insert_many(author_data)
        author_and_book_collection.insert_many(author_data)
    else:
        author_collection.insert_one(author_data)
        author_and_book_collection.insert_one(author_data)
    # author_collection.insert_many(author_data)
    print('Authors have been added to goodReadsData database')
    with open('books.json') as f_books:
        book_data = json.load(f_books)
    if isinstance(book_data, list):
        book_collection.insert_many(book_data)
        author_and_book_collection.insert_many(book_data)
    else:
        book_collection.insert_one(book_data)
        author_and_book_collection.insert_many(book_data)
    # book_collection.insert_many(book_data)
    print('Books have been added to goodReadsData database')


def write_to_json_files():
    """ Write all collected data to json files at once"""
    print('books ' + str(len(book_jsons)))
    print('authors ' + str(len(author_jsons)))
    with open("authors.json", "w") as author_file:
        # author_file.write(json.dump(authorJsons, indent=4))
        json.dump(author_jsons, author_file, cls=ComplexEncoder, indent=4)
        author_file.close()
    with open("books.json", "w") as book_file:
        json.dump(book_jsons, book_file, cls=ComplexEncoder, indent=4)
        book_file.close()


def grab_book_title(soup, book_dict):
    """Gets the book title. Enters None for value if not available"""
    try:
        book_title = soup.find(id='bookTitle').text  # Gets the bookTitle
        book_title = book_title.strip().strip('\n')
        book_dict['title'] = book_title
    except AttributeError:
        book_dict['title'] = None


def grab_author_and_id(soup, book_dict):
    """Gets the book's author and id . Enters None for value if not available"""
    try:
        # Gets the author div
        author = soup.find('div', class_='authorName__container')
        author_name = author.text  # Gets the author name
        book_dict['author'] = author_name.strip('\n')

        author_URL = author.a.get('href')  # Gets the author page url
        book_dict['author_url'] = author_URL
    except AttributeError:
        book_dict['author'] = None
        book_dict['author_url'] = None


def grab_book_rating(soup, book_dict):
    """Gets the book rating. Enters None for value if not available"""
    try:
        # Gets div with all book meta data
        book_meta = soup.find('div', id='bookMeta')
        rating = book_meta.find(
            'span', itemprop="ratingValue").text  # gets rating
        book_dict['rating'] = rating.strip().strip('\n')
    except AttributeError:
        book_dict['rating'] = None


def grab_book_rating_review_count(soup, book_dict):
    """Gets the count of the books ratings and reviews. Enters None for value if not available"""
    try:
        book_meta = soup.find('div', id='bookMeta')
        rating_count_and_reviews = book_meta.find_all(
            'a', class_="gr-hyperlink")  # gets rating count and reviews in a list
        # number of ratings is found first
        rating_count = rating_count_and_reviews[0].text
        rating_count = ''.join(filter(str.isdigit, rating_count))

        book_dict['rating_count'] = rating_count
        # number of reviews is found second
        rating_reviews = rating_count_and_reviews[1].text
        rating_reviews = ''.join(filter(str.isdigit, rating_reviews))
        book_dict['review_count'] = rating_reviews
    except AttributeError:
        book_dict['rating_count'] = None
        book_dict['review_count'] = None


def grab_book_image_url(soup, book_dict):
    """Gets the image url for the book. Enters None for value if not available"""
    try:
        image = soup.find('div', class_="bookCoverPrimary")

        image_url = image.a.get('href')  # get cover image linkk

        book_dict['image_url'] = image_url
    except AttributeError:
        book_dict['image_url'] = None


def grab_similar_books(soup, book_dict):
    """Gets all similar books in a list. Enters None for value if not available"""
    try:
        related_books_list = soup.find_all('li', class_="cover")
        related_books_list_links = []
        for book in related_books_list:
            # returns a list of all books related to current book
            related_books_list_links.append(book.a.get('href'))

        book_dict['similar_books'] = related_books_list_links
        return related_books_list
    except AttributeError:
        book_dict['similar_books'] = None


def grab_book_isbn(soup, book_dict):
    """Gets ISBN for book if available. Enters None for value if not available"""
    try:
        isbnContainers = soup.find_all('div', class_="clearFloats")
        isbn = isbnContainers[1].find('div', class_="infoBoxRowItem").text
        book_dict['ISBN'] = isbn.strip().strip(
            '\n').replace(" ", '').replace("\n", "")
    except AttributeError:
        book_dict['ISBN'] = None
    except IndexError:
        book_dict['ISBN'] = None


def scrape_book_info(url):
    """
    Scraper for the book information.
    Then sent to convertToJsonBookObj
    returns the list of all similar books
    """
    time.sleep(1.0)
    headers = {
        'User-Agent': 'My User Agent 18',
        # This is another valid field
    }
    page = requests.get(url, headers=headers).text
    # with open('tempPage.html',  errors='ignore') as html_file:
    #    soup = BeautifulSoup(html_file, 'lxml')
    soup = BeautifulSoup(page, 'lxml')
    book_dict = dict()
    """url and book id is immediatley parsed from inputted url"""
    book_dict['book_url'] = url
    book_dict['book_id'] = ''.join(filter(str.isdigit, url))

    """Retrieves individual components for the book json object"""
    grab_book_title(soup, book_dict)
    grab_author_and_id(soup, book_dict)
    grab_book_rating(soup, book_dict)
    grab_book_rating_review_count(soup, book_dict)
    grab_book_image_url(soup, book_dict)
    grab_book_isbn(soup, book_dict)
    all_related_books = grab_similar_books(soup, book_dict)

    """Sends the dict object to be converted to a json object"""
    convert_to_json_book_obj(book_dict)
    return all_related_books


def get_author_url(url):
    """
    Retrieves only the author page url
    """
    time.sleep(1.0)
    headers = {
        'User-Agent': 'My User Agent 9.0',
        # This is another valid field
    }
    page = requests.get(url, headers=headers).text
    # with open('tempPage.html',  errors='ignore') as html_file:
    #    soup = BeautifulSoup(html_file, 'lxml')
    soup = BeautifulSoup(page, 'lxml')
    author = soup.find('div', class_='authorName__container')
    authorURL = author.a.get('href')  # Gets the author page url
    return authorURL


def scrape_total_books(url):
    """
    Get all the urls for the total amount of books to scrape
    """
    time.sleep(1.0)
    list_of_books = list()

    page = requests.get(url).text
    # with open('tempPage.html',  errors='ignore') as html_file:
    #    soup = BeautifulSoup(html_file, 'lxml')
    soup = BeautifulSoup(page, 'lxml')

    related_books_list = soup.find_all('li', class_="cover")
    for book in related_books_list:
        # returns a list of all books related to current book
        list_of_books.append(book.a.get('href'))
    return list_of_books


def scrape_total_authors(url):
    """
    Gets all the urls for the total amount of author pages to scrape
    """

    list_of_authors = list()

    full_url = 'https://www.goodreads.com'+url

    page = requests.get(full_url).text

    similar_authors_soup = BeautifulSoup(page, 'lxml')
    relatedAuthors = similar_authors_soup.find_all(
        'div', class_="listWithDividers__item")  # get list of all related authors

    for item in relatedAuthors:

        list_of_authors.append(item.a.get('href'))

    return list_of_authors


def grab_author_name(author_soup, author_dict):
    """Gets the Author name. Enters None for value if not available"""
    try:
        author_name = author_soup.find('h1', class_="authorName").text
        author_dict['name'] = author_name.strip('\n')
    except AttributeError:
        author_dict['name'] = None


def grab_author_rating_reviews(author_soup, author_dict):
    """Gets the Author ratings and reviews along with the count. Enters None for value if not available"""
    try:
        author_meta = author_soup.find(
            'div', class_="hreview-aggregate")  # get author meta data
        author_avg_rating = author_meta.find(
            'span', class_="average").text  # get author avg star rating
        author_dict['rating'] = author_avg_rating

        author_num_rating = author_meta.find(
            'span', class_="votes").text  # get author number of ratings
        author_dict['rating_count'] = author_num_rating.strip().strip('\n')

        author_num_reviews = author_meta.find(
            'span', class_="count").text  # get author number of reviews
        author_dict['review_count'] = author_num_reviews.strip().strip('\n')
    except AttributeError:
        author_dict['rating'] = None
        author_dict['rating_count'] = None
        author_dict['review_count'] = None


def grab_author_image_url(author_soup, author_dict):
    """Gets the Author image url. Enters None for value if not available"""

    try:
        author_img = author_soup.find(
            'div', class_="leftContainer authorLeftContainer")
        author_img_link = author_img.img.get('src')  # get author image link
        author_dict['image_url'] = author_img_link
    except AttributeError:
        author_dict['image_url'] = None


def grab_author_books(author_soup, author_dict):
    """Gets the Author books. Enters None for value if not available"""
    try:
        table = author_soup.find('table', class_="stacked tableList")
        # table data with the title
        table_body = table.find_all('td', width="100%")
        author_books = []  # list to add titles to
        for cell in table_body:
            # get title of the book in the cell
            title = cell.find('a', class_="bookTitle").text
            title = title.lstrip("\n")  # strip the leading \n
            # strip the trailing \n and then append to list
            author_books.append(title.rstrip("\n"))
        author_dict['author_books'] = author_books
    except AttributeError:
        author_dict['author_books'] = None
    return author_books


def scrape_author_info(url):
    """
    Scraper for the author page
    Then sent to convertToJsonAuthorObj
    """

    headers = {
        'User-Agent': 'User Agent 30',
        # This is another valid field
    }
    page2 = requests.get(url, headers=headers).text

    author_soup = BeautifulSoup(page2, 'lxml')
    author_dict = dict()
    """Retrieves individual components for the author dict object"""
    grab_author_name(author_soup, author_dict)
    grab_author_rating_reviews(author_soup, author_dict)
    grab_author_image_url(author_soup, author_dict)
    all_author_books = grab_author_books(author_soup, author_dict)
    """Gets the seperate link for the similar authors page"""
    author_meta = author_soup.find(
        'div', class_="hreview-aggregate")  # get author meta data
    try:
        author_related = author_meta.find_all('a')
        author_related_link = author_related[1].get(
            'href')  # link to page of related authors
        scrape_similar_authors(author_related_link, author_dict)
    except IndexError:
        author_dict['related_authors'] = None
        author_dict['author_url'] = None
        author_dict['author_id'] = None
    except AttributeError:
        author_dict['related_authors'] = None
        author_dict['author_url'] = None
        author_dict['author_id'] = None
    """Send author dict object to be converted into a json object"""
    convert_to_json_author_obj(author_dict)
    return all_author_books


def scrape_similar_authors(linkToSimilarAuthors, authord_dict_obj):
    """
    Seperate scraper for similar authors since it is on a seperate page than the author page
    Takes in the page to the similar authors page and the author dict to later be converted to json object
    Uses link 'similar authors' on author page
    """
    headers = {
        'User-Agent': 'User Agent10',
        # This is another valid field
    }
    url = 'https://www.goodreads.com'+linkToSimilarAuthors

    page = requests.get(url, headers=headers).text

    similar_authors_soup = BeautifulSoup(page, 'lxml')
    related_authors = similar_authors_soup.find_all(
        'div', class_="listWithDividers__item")  # get list of all related authors
    related_author_links = []
    for item in related_authors:
        # append links to author pages
        related_author_links.append(item.a.get('href'))
    authord_dict_obj['related_authors'] = related_author_links
    authord_dict_obj['author_url'] = related_author_links[0]
    authord_dict_obj['author_id'] = ''.join(
        filter(str.isdigit, related_author_links[0]))


def get_all_books(url):
    """
    Uses a set to remove duplicates of book urls and is later used to feed urls to scrapeBookInfo
    """
    book_set = set()
    gathered_books = scrape_total_books(url)
    for book_link in gathered_books:
        book_set.add(book_link)

    sleep_time = 3
    while len(book_set) < 200:
        sleep_time = sleep_time + .25
        time.sleep(sleep_time)
        try:
            gathered_books = scrape_total_books(
                list(book_set)[random.randint(0, len(book_set) - 1)])

            for book_link in gathered_books:
                book_set.add(book_link)
            print(str(len(book_set)) + " Books Found")
        except requests.exceptions.ConnectionError:
            print('Limit Reached')
    return book_set


def get_similar_authors_page(url):
    """ Gets the similar authors page url """
    update_num = 11
    headers = {
        'User-Agent': 'User Agent' + str(update_num),
        # This is another valid field
    }
    page2 = requests.get(url, headers=headers).text

    author_soup = BeautifulSoup(page2, 'lxml')
    author_meta = author_soup.find(
        'div', class_="hreview-aggregate")  # get author meta data
    author_related = author_meta.find_all('a')
    author_related_link = author_related[1].get(
        'href')  # link to page of related authors
    return author_related_link


def get_all_authors(url):
    """
    Uses a set to remove duplicates of author urls and is later used to feed urls to scrapeAuthorinfo
    """
    author_set = set()

    author_url = get_author_url(url)  # returns author page url
    similar_authors = get_similar_authors_page(
        author_url)  # returns the page with similar authors

    gathered_authors = scrape_total_authors(
        similar_authors)  # returns completed urls
    for author_link in gathered_authors:
        author_set.add(author_link)

    time_to_sleep = 2
    while len(author_set) < 50:
        time_to_sleep = time_to_sleep + .25
        time.sleep(time_to_sleep)
        try:
            similar_authors = get_similar_authors_page(
                list(author_set)[random.randint(0, len(author_set) - 1)])

            gathered_authors = scrape_total_authors(similar_authors)

            for author_link in gathered_authors:
                author_set.add(author_link)
            print(str(len(author_set)) + ' Authors Found')
        except requests.exceptions.ConnectionError:
            print('Limit Reached')
    return author_set


def scrape(url):
    """Main scrape function with output statements for process update to user"""
    global book_jsons
    global author_jsons
    print('Gathering Authors')
    list_of_authors = get_all_authors(url)
    print('Gathered List of Authors')

    print('Worked Hard... Gotta Sleep')
    time.sleep(10)
    print('Back to Work')

    print('Gathering Books')
    list_of_books = get_all_books(url)
    print("Gathered List of Books")

    print('Worked Hard... Gotta Sleep')
    time.sleep(10)
    print('Back to Work')

    print('Starting Author Data Collection')
    for author_url in list(list_of_authors):
        scrape_author_info(author_url)
    print('Finished Collecting Author Data')

    print('Worked Hard... Gotta Sleep')
    time.sleep(10)
    print('Back to Work')

    print('Starting Book Data Collection')
    for book_url in list(list_of_books):
        scrape_book_info(book_url)
    print('Finished Collecting Book Data')

    print("Converting Collected Data to JSON files")
    write_to_json_files()
    print("Loading JSON files to data base")
    add_to_db()


if __name__ == "__main__":
    # take input for url
    url = input("Enter URl: ")
    scrape(url)
