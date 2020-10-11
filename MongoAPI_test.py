from flask_testing import TestCase
import MongoAPI


class MyTest(TestCase):

    def create_app(self):
        app = MongoAPI.app
        app.config['TESTING'] = True
        return app

    def test_greeting(self):
        self.app.get('/')
        self.assert_template_used('index.html')
        self.assert_context("greeting", "hello")

    def test_see_all_books(self):
        self.app.get('/allbooks')
        self.assert_template_used('seeAllBooks.html')

    def test_see_all_authors(self):
        self.app.get('/allAuthors')
        self.assert_template_used('seeAllAuthors.html')

    def test_get_books(self):
        self.app.get('/mongo/books')
        self.assert_template_used('gottenBooks.html')

    def test_get_authors(self):
        self.app.get('/mongo/authors')
        self.assert_template_used('gottenAuthors.html')

    def test_post_books(self):
        self.app.get('/mongo/books')
        self.assert_template_used('post_book.html')

    def test_post_authors(self):
        self.app.get('/mongo/authors')
        self.assert_template_used('post_author.html')

    def test_update_books(self):
        self.app.get('/mongo/books')
        self.assert_template_used('updated_book.html')

    def test_updated_authors(self):
        self.app.get('/mongo/authors')
        self.assert_template_used('updated_author.html')

    def test_delete_book(self):
        self.app.get('/mongo/books')
        self.assert_template_used('deleted_book.html')

    def test_delete_author(self):
        self.app.get('/mongo/authors')
        self.assert_template_used('deleted_author.html')
