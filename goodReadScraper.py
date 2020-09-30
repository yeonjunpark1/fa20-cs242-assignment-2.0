from bs4 import BeautifulSoup
import requests
import urllib
import string


def scrape():

    with open('tempPage.html',  errors='ignore') as html_file:
        soup = BeautifulSoup(html_file, 'lxml')

    bookTitle = soup.find(id='bookTitle').text  # Gets the bookTitle
    # Gets the author div
    author = soup.find('div', class_='authorName__container')
    authorURL = author.a.get('href')  # Gets the author page url
    authorName = author.text  # Gets the author name
    # Gets div with all book meta data
    bookMeta = soup.find('div', id='bookMeta')
    rating = bookMeta.find('span', itemprop="ratingValue").text  # gets rating
    ratingCount_and_reviews = bookMeta.find_all(
        'a', class_="gr-hyperlink")  # gets rating count and reviews in a list
    # number of ratings is found first
    ratingCount = ratingCount_and_reviews[0].text
    # number of reviews is found second
    ratingReviews = ratingCount_and_reviews[1].text

    image = soup.find('div', class_="bookCoverPrimary")
    #imageUrl = image.find('img', id = "coverImage")
    imageUrl = image.a.get('href')  # get cover image linkk

    relatedBooks = soup.find('div', class_="bookCarousel")
    relatedBooksList = soup.find_all('li', class_="cover")
    relatedBooksListLinks = []
    for book in relatedBooksList:
        # returns a list of all books related to current book
        relatedBooksListLinks.append(book.a.get('href'))

    print(bookTitle)
    print(authorURL)
    print(authorName)
    print(rating)
    print(ratingCount)
    print(ratingReviews)
    print(imageUrl)
    print(relatedBooksListLinks)

    with open('author_.html',  errors='ignore') as html2_file:
        authorSoup = BeautifulSoup(html2_file, 'lxml')
    authorMeta = authorSoup.find(
        'div', class_="hreview-aggregate")  # get author meta data
    authorAvgRating = authorMeta.find(
        'span', class_="average").text  # get author avg star rating
    authorNumRating = authorMeta.find(
        'span', class_="votes").text  # get author number of ratings
    authorNumReviews = authorMeta.find(
        'span', class_="count").text  # get author number of reviews
    authorImg = authorSoup.find(
        'div', class_="leftContainer authorLeftContainer")
    authorImgLink = authorImg.img.get('src')  # get author image link

    print("--------------")
    print(authorAvgRating)
    print(authorNumRating)
    print(authorNumReviews)
    print(authorImgLink)

    authorRelated = authorMeta.find_all('a')
    authorRelatedLink = authorRelated[1].get(
        'href')  # link to page of related authors
    print(authorRelated)
    print(authorRelatedLink)

    # find table of books by author
    table = authorSoup.find('table', class_="stacked tableList")
    tableBody = table.find_all('td', width="100%")  # table data with the title
    authorBooks = []  # list to add titles to
    for cell in tableBody:
        # get title of the book in the cell
        title = cell.find('a', class_="bookTitle").text
        title = title.lstrip("\n")  # strip the leading \n
        # strip the trailing \n and then append to list
        authorBooks.append(title.rstrip("\n"))

    print(authorBooks)

    with open('A_similar.html', errors="ignore") as html3_file:
        similarAuthorsSoup = BeautifulSoup(html3_file, 'lxml')

    relatedAuthors = similarAuthorsSoup.find_all(
        'div', class_="listWithDividers__item")  # get list of all related authors
    relatedAuthorLinks = []
    for item in relatedAuthors:
        # append links to author pages
        relatedAuthorLinks.append(item.a.get('href'))

    print(relatedAuthorLinks)


if __name__ == "__main__":
    scrape()
