#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from flask import Flask, g, abort, send_from_directory, session, redirect, url_for, request, make_response, flash, render_template, current_app, jsonify
from flask.ext.restful import Resource, Api, fields, marshal, reqparse
from functools import wraps, update_wrapper
from library import *
import sys
__author__ = 'shunghsiyu'


my_errors = {
    'CannotCancelReservationError': {
        'message': 'Reader does not have an active reservation for that copy.',
        'status': 409
    },
    'CopyNotAvailableError': {
        'message': 'The copy has either been borrowed or reserved by another reader.',
        'status': 409
    },
    'CannotReturnCopyError': {
        'message': 'Reader does not have an active borrow for that copy.',
        'status': 409
    },
    'AddBookError': {
        'message': 'There is already a book with the same ISBN in the database or the publisher does not exist',
        'status': 400
    },
    'ValueError': {
        'message': 'The date format does not match YYYY-MM-DD and cannot be parsed',
        'status': 400
    },
    'OverBorrowError': {
        'message': 'A reader cannot borrow more than 10 books',
        'status': 409
    },
    'OverReserveError': {
        'message': 'A reader cannot reserve more than 10 books',
        'status': 409
    }
}


app = Flask(__name__)


class MyApi(Api):
    def __init__(self, *args, **kwargs):
        super(MyApi, self).__init__(*args, **kwargs)

    def unauthorized(self, response):
        """ Given a response, change it to ask for credentials """

        realm = current_app.config.get("HTTP_BASIC_AUTH_REALM", "flask-restful")
        challenge = u"{0} realm=\"{1}\"".format("Newauth", realm)

        response.headers['WWW-Authenticate'] = challenge
        return response

api = MyApi(app, errors=my_errors)
marshall_fields = {}


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


def reader_login_required_html(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'reader_id' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login_reader'))
    return wrap


def reader_login_required_json(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'reader_id' in session:
            return func(*args, **kwargs)
        else:
            return abort(401)
    return wrap


def reader_id_same(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        reader_id = kwargs.get('reader_id', None)
        if reader_id is not None:
            if 'admin' in session:
                pass
            elif 'reader_id' in session and int(session['reader_id']) == reader_id:
                pass
            else:
                abort(403)
        return func(*args, **kwargs)
    return wrap


def admin_login_required_html(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'admin' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login_admin'))
    return wrap


def admin_login_required_json(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'admin' in session:
            return func(*args, **kwargs)
        else:
            return abort(401)
    return wrap


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = start(app.config['DB_PATH'])
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class LibraryResource(Resource):
    method_decorators = [reader_login_required_json]
    model = None
    envelope = None
    resource_fields = None
    uri_fields = None

    def _get(self, identity):
        with app.app_context():
            if identity is not None:
                return marshal(self._get_one(identity),
                               self.resource_fields)
            else:
                return marshal(self._get_all(),
                               self.uri_fields,
                               envelope=self.envelope)

    def _get_one(self, identity):
        resource = self.model.get(get_db(), identity)
        if resource:
            return resource
        else:
            abort(404)

    def _get_all(self):
        collection = self.model.get_all(get_db())
        return collection


marshall_fields['AuthorUri'] = {
    'author_id': fields.Integer,
    'name': fields.String,
    'uri': fields.Url('authorresource')
}

marshall_fields['BookUri'] = {
    'book_id': fields.Integer,
    'title': fields.String,
    'ISBN': fields.String(attribute='isbn'),
    'publisher_id': fields.Integer,
    'publish_date': fields.String(attribute=lambda book: book.publish_date.strftime('%Y-%m-%d')),
    'uri': fields.Url('bookresource')
}

marshall_fields['BranchUri'] = {
    'lib_id': fields.Integer,
    'name': fields.String,
    'location': fields.String,
    'uri': fields.Url('branchresource')
}

marshall_fields['PublisherUri'] = {
    'publisher_id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
    'uri': fields.Url('publisherresource')
}

marshall_fields['ReaderUri'] = {
    'reader_id': fields.Integer,
    'name': fields.String,
    'uri': fields.Url('readerresource')
}

marshall_fields['CopyUri'] = {
    'copy_id': fields.Integer,
    'book_id': fields.Integer,
    'lib_id': fields.Integer,
    'number': fields.Integer,
    'uri': fields.Url('copyresource')
}

marshall_fields['BorrowUri'] = {
    'borrow_id': fields.Integer,
    'b_datetime': fields.DateTime(dt_format='iso8601'),
    'r_datetime': fields.DateTime(dt_format='iso8601'),
    'fine': fields.String,
    'uri': fields.Url('borrowresource')
}

marshall_fields['ReserveUri'] = {
    'reserve_id': fields.Integer,
    'rv_datetime': fields.DateTime(dt_format='iso8601'),
    'is_reserved': fields.Boolean,
    'uri': fields.Url('reserveresource')
}


marshall_fields['Author'] = {
    'author_id': fields.Integer,
    'name': fields.String,
    'uri': fields.Url('authorresource')
}


class AuthorResource(LibraryResource):
    model = Authors
    envelope = 'authors'
    resource_fields = marshall_fields['Author']
    uri_fields = marshall_fields['AuthorUri']

    def get(self, author_id=None):
        return self._get(author_id)

    def post(self, author_id=None):
        if author_id is not None:
            abort(405)
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args(strict=True)
        with app.app_context():
            return marshal(self.model.add(get_db(), args['name']),
                           self.resource_fields), 201


marshall_fields['BranchMostBorrowed'] = {
    'book': fields.Nested(marshall_fields['BookUri'],
                          attribute=lambda t: t['book']),
    'times': fields.Integer(attribute=lambda t: t['times'])
}

marshall_fields['BranchFrequentBorrower'] = {
    'reader': fields.Nested(marshall_fields['ReaderUri'],
                            attribute=lambda t: t['reader']),
    'times': fields.Integer(attribute=lambda t: t['times'])
}

marshall_fields['Branch'] = {
    'lib_id': fields.Integer,
    'name': fields.String,
    'location': fields.String,
    'most_borrowed': fields.Nested(marshall_fields['BranchMostBorrowed'],
                                   attribute=lambda branch: branch.most_borrowed_books()),
    'frequent_borrower': fields.Nested(marshall_fields['BranchFrequentBorrower'],
                                       attribute=lambda branch: branch.frequent_borrowers()),
    'uri': fields.Url('branchresource')
}


class BranchResource(LibraryResource):
    model = Branches
    envelope = 'branches'
    resource_fields = marshall_fields['Branch']
    uri_fields = marshall_fields['BranchUri']

    def get(self, lib_id=None):
        return self._get(lib_id)


marshall_fields['CopySimple'] = {
    'copy_id': fields.Integer,
    'number': fields.Integer,
    'branch': fields.Nested(marshall_fields['Branch'],
                            attribute=lambda copy: copy.get_branch()),
    'is_reserved': fields.Boolean(attribute=lambda copy: copy.reserver() is not None),
    'is_borrowed': fields.Boolean(attribute=lambda copy: copy.borrower() is not None),
    'is_available': fields.Boolean(attribute=lambda copy: not copy.borrower() and not copy.reserver()),
    'uri': fields.Url('copyresource')
}

marshall_fields['Book'] = {
    'book_id': fields.Integer,
    'title': fields.String,
    'ISBN': fields.String(attribute='isbn'),
    'publisher': fields.Nested(marshall_fields['PublisherUri'],
                               attribute=lambda book: book.get_publisher()),
    'publish_date': fields.String(attribute=lambda book: book.publish_date.strftime('%Y-%m-%d')),
    'copies': fields.Nested(marshall_fields['CopySimple'], attribute=lambda book: book.get_copies()),
    'authors': fields.Nested(marshall_fields['AuthorUri'] ,attribute=lambda book: book.get_authors()),
    'uri': fields.Url('bookresource')
}


class BookResource(LibraryResource):
    model = Books
    envelope = 'books'
    resource_fields = marshall_fields['Book']
    uri_fields = marshall_fields['Book']

    def get(self, book_id=None):
        return self._get(book_id)

    def post(self, book_id=None):
        if book_id is not None:
            abort(405)
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('ISBN', type=str, required=True)
        parser.add_argument('publisher_id', type=int, required=True)
        parser.add_argument('publish_date', type=str, required=True)
        args = parser.parse_args(strict=True)
        publish_date = datetime.strptime(args['publish_date'], '%Y-%m-%d')
        with app.app_context():
            book = self.model.add(get_db(), args['title'],
                                  args['ISBN'], args['publisher_id'],
                                  publish_date)
            return marshal(book, self.resource_fields), 201

    def _get_all(self):
        parser = reqparse.RequestParser()
        parser.add_argument('book_id', type=int)
        parser.add_argument('title', type=str)
        parser.add_argument('publisher_name', type=str)
        args = parser.parse_args()
        books = self.model.get_all(get_db(), args['book_id'],
                                   args['title'],
                                   args['publisher_name'])
        return books


marshall_fields['Publisher'] = {
    'publisher_id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
    'books': fields.Nested(marshall_fields['BookUri'],
                           attribute=lambda publisher: publisher.get_books()),
    'uri': fields.Url('publisherresource')
}


class PublisherResource(LibraryResource):
    model = Publishers
    envelope = 'publishers'
    resource_fields = marshall_fields['Publisher']
    uri_fields = marshall_fields['PublisherUri']

    def get(self, publisher_id=None):
        return self._get(publisher_id)


marshall_fields['Reader'] = {
    'reader_id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
    'phone': fields.String,
    'reserves': fields.Nested(marshall_fields['ReserveUri'],
                              attribute=lambda reader: reader.get_reserves()),
    'borrows': fields.Nested(marshall_fields['BorrowUri'],
                             attribute=lambda reader: reader.get_borrows()),
    'uri': fields.Url('readerresource')
}


class ReaderResource(LibraryResource):
    model = Readers
    envelope = 'readers'
    resource_fields = marshall_fields['Reader']
    uri_fields = marshall_fields['ReaderUri']

    def get(self, reader_id=None):
        return self._get(reader_id)

    def _get(self, reader_id):
        if reader_id is not None:
            if 'admin' in session:
                pass
            elif 'reader_id' in session and int(session['reader_id']) == reader_id:
                pass
            else:
                abort(403)
            with app.app_context():
                return marshal(self._get_one(reader_id),
                               self.resource_fields)
        else:
            with app.app_context():
                return marshal(self._get_all(),
                               self.uri_fields,
                               envelope=self.envelope)

    def post(self, reader_id=None):
        if reader_id is not None:
            abort(405)
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('address', type=str, required=True)
        parser.add_argument('phone', type=str, required=True)
        args = parser.parse_args(strict=True)
        with app.app_context():
            return marshal(self.model.add(get_db(), args['name'],
                                          args['address'],
                                          args['phone']),
                           self.resource_fields), 201


marshall_fields['Copy'] = {
    'copy_id': fields.Integer,
    'number': fields.Integer,
    'book': fields.Nested(marshall_fields['Book'],
                          attribute=lambda copy: copy.get_book()),
    'branch': fields.Nested(marshall_fields['Branch'],
                            attribute=lambda copy: copy.get_branch()),
    'is_reserved': fields.Boolean(attribute=lambda copy: copy.reserver() is not None),
    'is_borrowed': fields.Boolean(attribute=lambda copy: copy.borrower() is not None),
    'is_available': fields.Boolean(attribute=lambda copy: not copy.borrower() and not copy.reserver()),
    'uri': fields.Url('copyresource')
}


class CopyResource(LibraryResource):
    model = Copies
    envelope = 'copies'
    resource_fields = marshall_fields['Copy']
    uri_fields = marshall_fields['CopyUri']

    def get(self, copy_id=None):
        return self._get(copy_id)

    def post(self, copy_id=None):
        if copy_id is not None:
            abort(405)
        parser = reqparse.RequestParser()
        parser.add_argument('book_id', type=int, required=True)
        parser.add_argument('lib_id', type=int, required=True)
        args = parser.parse_args(strict=True)
        with app.app_context():
            copy = self.model.add(get_db(), args['book_id'],
                                  args['lib_id'])
            return marshal(copy, self.uri_fields), 201


marshall_fields['Borrow'] = {
    'borrow_id': fields.Integer,
    'copy': fields.Nested(marshall_fields['Copy'],
                          attribute=lambda borrow: borrow.get_copy()),
    'reader': fields.Nested(marshall_fields['ReaderUri'],
                            attribute=lambda borrow: borrow.get_reader()),
    'b_datetime': fields.DateTime(dt_format='iso8601'),
    'r_datetime': fields.DateTime(dt_format='iso8601'),
    'fine': fields.String,
    'uri': fields.Url('borrowresource')
}


class BorrowResource(LibraryResource):
    model = Borrows
    envelope = 'borrows'
    resource_fields = marshall_fields['Borrow']
    uri_fields = marshall_fields['BorrowUri']

    def get(self, borrow_id=None):
        return self._get(borrow_id)


marshall_fields['Reserve'] = {
    'reserve_id': fields.Integer,
    'copy': fields.Nested(marshall_fields['Copy'],
                          attribute=lambda reserve: reserve.get_copy()),
    'reader': fields.Nested(marshall_fields['ReaderUri'],
                            attribute=lambda reserve: reserve.get_reader()),
    'rv_datetime': fields.DateTime(dt_format='iso8601'),
    'is_reserved': fields.Boolean,
    'uri': fields.Url('reserveresource')
}


class ReserveResource(LibraryResource):
    model = Reserves
    envelope = 'reserves'
    resource_fields = marshall_fields['Reserve']
    uri_fields = marshall_fields['ReserveUri']

    def get(self, reserve_id=None):
        return self._get(reserve_id)


class ReaderActionResource(Resource):
    resource_field = None
    method_decorators = [reader_id_same]

    def post(self, reader_id):
        with app.app_context():
            reader = Readers.get(get_db(), reader_id)
            if reader is None:
                abort(404)
            parser = reqparse.RequestParser()
            parser.add_argument('copy_id', type=int, required=True)
            args = parser.parse_args()
            copy = Copies.get(get_db(), args['copy_id'])
            if copy is None:
                abort(400)
            to_return = self.action(reader, copy)
            return marshal(to_return,
                           self.resource_field), 201

    def action(self, reader, copy):
        pass


class CopyCheckoutResource(ReaderActionResource):
    resource_field = marshall_fields['Borrow']

    def action(self, reader, copy):
        return reader.checkout(copy)


class CopyReturnResource(ReaderActionResource):
    resource_field = marshall_fields['Borrow']

    def action(self, reader, copy):
        return reader.retrn(copy)


class CopyReserveResource(ReaderActionResource):
    resource_field = marshall_fields['Reserve']

    def action(self, reader, copy):
        return reader.reserve(copy)


class CopyCancelResource(ReaderActionResource):
    resource_field = marshall_fields['Reserve']

    def action(self, reader, copy):
        return reader.cancel(copy)


class AverageFineResource(Resource):
    resource_field = {
        'reader': fields.Nested(marshall_fields['ReaderUri'],
                                attribute=lambda t: t['reader']),
        'fine': fields.Float(attribute=lambda t: t['fine'])
    }
    envelope = 'results'

    def get(self):
        with app.app_context():
            return marshal(Readers.average_fine(get_db()),
                           self.resource_field,
                           envelope=self.envelope)


api.add_resource(AuthorResource, '/api/authors/', '/api/authors/<int:author_id>')
api.add_resource(BookResource, '/api/books/', '/api/books/<int:book_id>')
api.add_resource(BranchResource, '/api/branches/', '/api/branches/<int:lib_id>')
api.add_resource(PublisherResource, '/api/publishers/', '/api/publishers/<int:publisher_id>')
api.add_resource(ReaderResource, '/api/readers/', '/api/readers/<int:reader_id>')
api.add_resource(CopyResource, '/api/copies/', '/api/copies/<int:copy_id>')
api.add_resource(BorrowResource, '/api/borrows/', '/api/borrows/<int:borrow_id>')
api.add_resource(ReserveResource, '/api/reserves/', '/api/reserves/<int:reserve_id>')
api.add_resource(CopyCheckoutResource, '/api/readers/<int:reader_id>/checkout')
api.add_resource(CopyReturnResource, '/api/readers/<int:reader_id>/return')
api.add_resource(CopyReserveResource, '/api/readers/<int:reader_id>/reserve')
api.add_resource(CopyCancelResource, '/api/readers/<int:reader_id>/cancel')
api.add_resource(AverageFineResource, '/api/readers/average_fine')


@app.route('/api/info')
@reader_login_required_json
def info():
    return jsonify(reader_id=session['reader_id'])


@app.route('/js/<path:path>')
def js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def css(path):
    return send_from_directory('css', path)


@app.route('/partial/<path:path>')
def partial(path):
    return send_from_directory('partial', path)


@app.route('/login_reader', methods=['GET', 'POST'])
@nocache
def login_reader():
    if request.method == 'POST':
        reader = None
        if 'reader_id' in request.form:
            with app.app_context():
                reader = Readers.get(get_db(), request.form['reader_id'])
        if reader:
            session['reader_id'] = request.form['reader_id']
            return redirect(url_for('reader'))
        flash('That reader ID does not exist!')
        return render_template('login_reader.html')
    elif 'reader_id' in session:
        return redirect(url_for('reader'))
    else:
        return render_template('login_reader.html')


@app.route('/reader_logout')
@nocache
def reader_logout():
    if 'reader_id' in session:
        session.pop('reader_id')
    return redirect(url_for('index'))


@app.route('/reader')
@reader_login_required_html
@nocache
def reader():
    return app.send_static_file('reader.html')


@app.route('/login_admin', methods=['GET', 'POST'])
@nocache
def login_admin():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            if request.form['username'] == 'admin' and request.form['password'] == 'adminadmin':
                session['admin'] = True
                return redirect(url_for('admin'))
        flash('That username/password combination does not exist!')
        return render_template('login_admin.html')
    elif 'admin' in session:
        return redirect(url_for('admin'))
    else:
        return render_template('login_admin.html')


@app.route('/admin_logout')
@nocache
def admin_logout():
    if 'admin' in session:
        session.pop('admin')
    return redirect(url_for('index'))


@app.route('/admin')
@admin_login_required_html
@nocache
def admin():
    return app.send_static_file('admin.html')


@app.route('/about')
def about():
    return app.send_static_file('about.html')


@app.route('/')
@app.route('/index')
def index():
    return app.send_static_file('index.html')


app.secret_key = 'thisisaSECRET'


def run(db_path='library.db', debug=False):
    app.config['DB_PATH'] = db_path
    if debug:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False)


if __name__ == '__main__':
    to_debug = len(sys.argv) > 1
    run(debug=to_debug)