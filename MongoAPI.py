import os
import json
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from pymongo import MongoClient
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from bson import json_util
load_dotenv()


app = Flask(__name__)
USER = os.getenv('USER')
DB_PASSWORD = os.getenv('PASSWORD')
DB_NAME = os.getenv('DATABASENAME')

app.config['MONGO_DBNAME'] = "goodReadsData"
app.config['MONGO_URI'] = "mongodb+srv://" + USER + ":" + DB_PASSWORD + \
    "@assignment-2-goodreads.bpcru.mongodb.net/" + \
    DB_NAME+"?retryWrites=true&w=majority"

mongo = PyMongo(app)


@app.route('/')
def index():
    """Opens Main Page"""
    return render_template('index.html')


@app.route('/allBooks')
def seeAllBooks():
    """Returns all Books"""
    book_entries = mongo.db.Books
    all_books = list(book_entries.find())
    return render_template('seeAllBooks.html', all_books=all_books), 200


@app.route('/allAuthors')
def seeAllAuthors():
    """Return all Authors"""
    author_entries = mongo.db.Authors
    all_authors = list(author_entries.find())
    return render_template('seeAllAuthors.html', all_authors=all_authors), 200


@app.route('/mongo/books', methods=['GET'])
def get_books_data():
    """Get data for books.
        Retrieves only the book title for query.
    """
    entry = mongo.db.Books
    output = list()
    look_up_type = None
    if 'title' in request.args:
        look_up_type = 'title'
        if len(request.args['title']) <= 2:
            return render_template('error.html', message="Must enter characters"), 400
        value = request.args['title'].strip('"')
        title = entry.find({'title': {'$regex': value}})
        if title:
            for book in title:
                output.append({'title': book['title']})
    elif 'related_books' in request.args:
        look_up_type = 'similar_books'
        if len(request.args['related_books']) <= 2:
            return render_template('error.html', message="Must enter characters"), 400
        value = request.args['related_books'].strip('"')
        related_books = entry.find(
            {'similar_books': {'$regex': value}})
        if related_books:
            for related in related_books:
                for link in related['similar_books']:
                    if value in link:
                        output.append(({'similar_books': link}))
    elif 'author' in request.args:
        look_up_type = 'author'
        if len(request.args['author']) <= 2:
            return render_template('error.html', message="Must enter characters"), 400
        value = request.args['author'].strip('"')
        authors = entry.find({'author': {'$regex': value}})
        if authors:
            for name in authors:
                output.append({'author': name['author']})
    if len(output) == 0:
        return render_template('error.html', message="No Entries Found"), 400
    return render_template('gottenBooks.html', output=output, look_up_type=look_up_type), 200


@app.route('/mongo/authors', methods=['GET'])
def get_author_data():
    """Get data for authors
        Retrieves only author names for query
    """
    entry = mongo.db.Authors
    output = list()
    look_up_type = None
    if 'name' in request.args:
        look_up_type = 'name'
        print(request.args)
        if len(request.args['name']) <= 2:
            return render_template('error.html', message="Must enter characters"), 400
        value = request.args['name'].strip('"')
        name = entry.find({'name': {'$regex': value}})
        if name:
            for author in name:
                output.append({'name': author['name']})
    elif 'booktitle' in request.args:
        look_up_type = 'related_books'
        if len(request.args['booktitle']) <= 2:
            return render_template('error.html', message="Must enter characters"), 400
        value = request.args['booktitle'].strip('"')
        related_books = entry.find(
            {'author_books': {'$regex': value}})
        if related_books:
            for related in related_books:
                for title in related['author_books']:
                    if value in title:
                        output.append(({'related_books': title}))
    if len(output) == 0:
        return render_template('error.html', message="No Entries Found"), 400
    return render_template('gottenAuthors.html', output=output, look_up_type=look_up_type), 200


@app.route('/mongo/books', methods=['POST'])
def post_book_data():
    """Post data for books
        Sets all other values to None if values are not provided
    """
    data = None
    if request.get_json() is None:
        data = request.form.to_dict()
        print(data)
    else:
        data = request.get_json()

    if data is None or data == {} or all(value == '' for value in data.values()):
        return render_template('error.html', message='Please Enter Information'), 400
    data.get('book_url', None)
    data.get('title', None)
    data.get('book_id', None)
    data.get('ISBN', None)
    data.get('author', None)
    data.get('author_url', None)
    data.get('rating', None)
    data.get('rating_count', None)
    data.get('review_count', None)
    data.get('image_url', None)
    data.get('similar_books', None)
    if isinstance(data, list):
        mongo.db.Books.insert_many(data)
    else:
        mongo.db.Books.insert_one(data)
    print(data)
    return render_template('post_book.html', output=data), 200


@app.route('/mongo/authors', methods=['POST'])
def post_author_data():
    """Post data for authors
        Sets all other values to None if values are not provided
    """
    data = None
    if request.get_json() is None:
        data = request.form.to_dict()
        print(data)
    else:
        data = request.get_json()

    if data is None or data == {} or all(value == '' for value in data.values()):
        return render_template('error.html', message='Input format is not correct'), 400

    data.get('name', None)
    data.get('author_url', None)
    data.get('author_id', None)
    data.get('rating', None)
    data.get('rating_count', None)
    data.get('review_count', None)
    data.get('image_url', None)
    data.get('related_authors', None)
    data.get('author_books', None)

    if isinstance(data, list):
        mongo.db.Authors.insert_many(data)
    else:
        mongo.db.Authors.insert_one(data)
    return render_template("post_author.html", output=data), 200


@app.route('/mongo/books', methods=['PUT'])
def update_book():
    """Update data for books
        When intercepting index error in the except, it means the requst was made in the front end and has to parse to input correctly
    """
    try:
        key = list(request.args.keys())[0]
        val = request.args[key].strip('"')
        data = request.get_json()
        filter = {key: val}
    except IndexError:
        queryVal = request.form.to_dict()
        filter_val, change_to_val = parse_filter_newValue(queryVal)
        filter = {filter_val[0]: filter_val[1]}
        data = {change_to_val[0]: change_to_val[1]}
    if all(value == '' for value in data.values()) or all(value == '' for value in filter.values()):
        print('here tho')
        return render_template('error.html', message="Please enter both fields"), 400
    new_values = {"$set": data}
    mongo.db.Books.update_one(filter, new_values, upsert=False)

    return render_template("updated_book.html", message="Book Has been updated"), 200
    # return jsonify({'result': "Successfully Updated"}), 200


@app.route('/mongo/authors', methods=['PUT'])
def update_author():
    """Update data for authors
        When intercepting index error in the except portion, it means the requst was made in the front end and has to parse to input correctly
    """
    try:
        key = list(request.args.keys())[0]
        val = request.args[key].strip('"')
        data = request.get_json()
        filter = {key: val}
    except IndexError:
        queryVal = request.form.to_dict()
        filter_val, change_to_val = parse_filter_newValue(queryVal)
        filter = {filter_val[0]: filter_val[1]}
        print(filter)
        data = {change_to_val[0]: change_to_val[1]}
        print(data)
    if all(value == '' for value in data.values()) or all(value == '' for value in filter.values()):
        return render_template('error.html', message="Please enter both fields"), 400
    new_values = {'$set': data}
    mongo.db.Authors.update_one(filter, new_values, upsert=False)
    return render_template('updated_author.html', message="Author has been Updated")


def parse_filter_newValue(queryVal):
    """Function used to parse the input from the PUT request. 
        Returns stripped and parsed input from the front-end GUI and sends the filter and new value back to PUT requests.
    """
    new_value_key = list(queryVal.keys())[0]
    change_to_val = queryVal[new_value_key].split('=')
    change_to_val[0] = change_to_val[0].strip('"')
    change_to_val[1] = change_to_val[1].strip('"')
    filt_key = list(queryVal.keys())[1]
    filter_val = queryVal[filt_key].split('=')
    filter_val[0] = filter_val[0].strip('"')
    filter_val[1] = filter_val[1].strip('"')
    return filter_val, change_to_val


@app.route('/mongo/books', methods=['DELETE'])
def delete_book():
    """Delete data for books
        When excepts IndexError, the request is coming from the front end application, and needs to parse and request data differently.
    """
    try:
        key = list(request.args.keys())[0]
        if key is None:
            return render_template("error.html", message="Please enter a correct key"), 400
        val = request.args[key].strip('"')
    except IndexError:
        queryVal = request.form.to_dict()
        key = list(queryVal.keys())[0]
        val = queryVal[key].strip('"')
    entry = mongo.db.Books
    elem_to_delete = entry.find_one({key:  val})
    if elem_to_delete is None:
        return render_template('error.html', message='No entry was found that matches query'), 400
    mongo.db.Books.delete_one(elem_to_delete)
    return render_template('deleted_book.html', message="Book Has been Deleted")


@app.route('/mongo/authors', methods=['DELETE'])
def delete_author():
    """Delete data for authors
        When excepts IndexError, the request is coming from the front end application, and needs to parse and request data differently.
    """
    try:
        key = list(request.args.keys())[0]
        val = request.args[key].strip('"')
        if key is None:
            return render_template("error.html", message="Please enter a correct key"), 400
    except IndexError:
        queryVal = request.form.to_dict()
        key = list(queryVal.keys())[0]
        val = queryVal[key].strip('"')
    entry = mongo.db.Authors
    elem_to_delete = entry.find_one({key: val})
    if elem_to_delete is None:
        return render_template('error.html', message='No entry was found that matches query'), 400
    mongo.db.Authors.delete_one(elem_to_delete)
    return render_template('deleted_author.html', message="Author Has been Deleted")
    # return jsonify({'result': 'Entry has been successfully deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)
