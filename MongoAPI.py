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
    return render_template('index.html')


@app.route('/allBooks')
def seeAllBooks():
    book_entries = mongo.db.Books
    all_books = list(book_entries.find())
    return render_template('seeAllBooks.html', all_books=all_books)


@app.route('/allAuthors')
def seeAllAuthors():
    author_entries = mongo.db.Authors
    all_authors = list(author_entries.find())
    return render_template('seeAllAuthors.html', all_authors=all_authors)


@app.route('/mongo/books/<string:value>', methods=['GET'])
def get_books_data(value):
    """Get data for books"""
    attrib_and_value = value.split("=")
    attrib_and_value[1] = attrib_and_value[1].strip('"')
    if len(attrib_and_value) != 2:
        return render_template('error.html', message='Input format is not correct')
    entry = mongo.db.Authors_and_Books
    output = list()

    if attrib_and_value[0] == 'title':
        title = entry.find({'title': {'$regex': attrib_and_value[1]}})
        if title:
            for book in title:
                output.append({'title': book['title']})
    elif attrib_and_value[0] == 'related_books':
        related_books = entry.find(
            {'similar_books': {'$regex': attrib_and_value[1]}})
        if related_books:
            for related in related_books:
                for link in related['similar_books']:
                    if value in link:
                        output.append(({'similar_books': link}))
    elif attrib_and_value[0] == 'author':
        author = entry.find({'name': {'$regex': attrib_and_value[1]}})
        if author:
            for name in author:
                output.append({'name': name['name']})

    return jsonify({'result': output})


@app.route('/mongo/authors/<string:value>', methods=['GET'])
def get_author_data(value):
    """Get data for authors"""
    attrib_and_value = value.split("=")
    attrib_and_value[1] = attrib_and_value[1].strip('"')
    if len(attrib_and_value) != 2:
        return render_template('error.html', message='Input format is not correct')
    entry = mongo.db.Authors_and_Books
    output = list()

    if attrib_and_value[0] == 'name':
        name = entry.find({'name': {'$regex': attrib_and_value[1]}})
        if name:
            for author in name:
                output.append({'name': author['name']})
    elif attrib_and_value[0] == 'booktitle':
        related_books = entry.find(
            {'author_books': {'$regex': attrib_and_value[1]}})
        if related_books:
            for related in related_books:
                for title in related['author_books']:
                    if attrib_and_value[1] in title:
                        output.append(({'related_books': title}))

    return jsonify({'result': output})


@app.route('/mongo/books', methods=['POST'])
def post__book_data():
    """Post data for books"""
    data = request.get_json()
    if data is None or data == {}:
        return render_template('error.html', message='Input format is not correct')
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
        mongo.db.Authors_and_Books.insert_many(data)
    else:
        mongo.db.Authors_and_Books.insert_one(data)

    return jsonify({'result': 'Entry has been successfully added'})


@app.route('/mongo/authors', methods=['POST'])
def post__author_data():
    """Post data for books"""
    data = request.get_json()
    if data is None or data == {}:
        return render_template('error.html', message='Input format is not correct')

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
        mongo.db.Authors_and_Books.insert_many(data)
    else:
        mongo.db.Authors_and_Books.insert_one(data)

    return jsonify({'result': 'Entry has been successfully added'})


@app.route('/mongo/books/<string:value>', methods=['PUT'])
def update_book(value):
    """Update data for books"""
    attrib_and_value = value.split("=")
    attrib_and_value[1] = attrib_and_value[1].strip('"')
    if len(attrib_and_value) != 2:
        return render_template('error.html', message='Input format is not correct')
    data = request.get_json()
    filter = {attrib_and_value[0]: attrib_and_value[1]}
    new_values = {'$set': data}
    mongo.db.Authors_and_Books.update_one(filter, new_values)
    return jsonify({'result': "Successfully Updated"})


@app.route('/mongo/authors/<string:value>', methods=['PUT'])
def update_author(value):
    """Update data for books"""
    attrib_and_value = value.split("=")
    attrib_and_value[1] = attrib_and_value[1].strip('"')
    if len(attrib_and_value) != 2:
        return render_template('error.html', message='Input format is not correct')
    data = request.get_json()
    filter = {attrib_and_value[0]: attrib_and_value[1]}
    new_values = {'$set': data}
    mongo.db.Authors_and_Books.update_one(filter, new_values)
    return jsonify({'result': "Successfully Updated"})


@app.route('/mongo/book/<string:value>', methods=['DELETE'])
def delete_book(value):
    """Delete data for books"""
    attrib_and_value = value.split("=")
    attrib_and_value[1] = attrib_and_value[1].strip('"')
    if len(attrib_and_value) != 2:
        return render_template('error.html', message='Input format is not correct')
    entry = mongo.db.Authors_and_Books
    elem_to_delete = entry.find_one({attrib_and_value[0]: attrib_and_value[1]})
    mongo.db.Authors_and_Books.delete_one(elem_to_delete)
    return jsonify({'result': 'Entry has been successfully deleted'})


@app.route('/mongo/author/<string:value>', methods=['DELETE'])
def delete_author(value):
    """Delete data for books"""
    attrib_and_value = value.split("=")
    attrib_and_value[1] = attrib_and_value[1].strip('"')
    if len(attrib_and_value) != 2:
        return render_template('error.html', message='Input format is not correct')
    entry = mongo.db.Authors_and_Books
    elem_to_delete = entry.find_one({attrib_and_value[0]: attrib_and_value[1]})
    mongo.db.Authors_and_Books.delete_one(elem_to_delete)
    return jsonify({'result': 'Entry has been successfully deleted'})


if __name__ == '__main__':
    app.run(debug=True)
