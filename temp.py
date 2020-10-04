from bs4 import BeautifulSoup
import json


def grab_book_isbn(soup):
    try:
        isbnContainers = soup.find_all('div', class_="clearFloats")
        isbn = isbnContainers[1].find('div', class_="infoBoxRowItem").text
        isbn.replace(" ", "")
        # print(isbn.strip().strip('\n'))
        print(json.dumps(isbn.strip().strip('\n').replace(" ", '')))
        # @book_dict['ISBN'] = isbn
    except AttributeError:
        #book_dict['ISBN'] = None
        print("couldn't find")


if __name__ == "__main__":
    with open('tempPage.html', errors='ignore') as page:
        soup = BeautifulSoup(page, 'lxml')
    grab_book_isbn(soup)
