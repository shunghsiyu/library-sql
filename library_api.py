#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from flask import Flask, g, abort
from flask.ext.restful import Resource, Api, fields, marshal, reqparse
from library import *
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
}


app = Flask(__name__)
api = Api(app, errors=my_errors)
marshall_fields = {}


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
    'publish_date': fields.DateTime(dt_format='iso8601'),
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
    'address': fields.String,
    'phone': fields.String,
    'uri': fields.Url('readerresource')
}

marshall_fields['CopyUri'] = {
    'copy_id': fields.Integer,
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


marshall_fields['Book'] = {
    'book_id': fields.Integer,
    'title': fields.String,
    'ISBN': fields.String(attribute='isbn'),
    'publisher_id': fields.Integer,
    'publish_date': fields.DateTime(dt_format='iso8601'),
    'uri': fields.Url('bookresource')
}


class BookResource(LibraryResource):
    model = Books
    envelope = 'books'
    resource_fields = marshall_fields['Book']
    uri_fields = marshall_fields['BookUri']

    def get(self, book_id=None):
        return self._get(book_id)

    def post(self, book_id=None):
        if book_id is not None:
            abort(405)
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str)
        parser.add_argument('ISBN', type=str)
        parser.add_argument('publisher_id', type=int)
        parser.add_argument('publish_date', type=str)
        args = parser.parse_args(strict=True)
        with app.app_context():
            return marshal(self.model.add(get_db(), args['title'],
                                          args['ISBN'],
                                          args['publisher_id'],
                                          args['publish_date']),
                           self.resource_fields)

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

marshall_fields['Branch'] = {
    'lib_id': fields.Integer,
    'name': fields.String,
    'location': fields.String,
    'uri': fields.Url('branchresource')
}


class BranchResource(LibraryResource):
    model = Branches
    envelope = 'branches'
    resource_fields = marshall_fields['Branch']
    uri_fields = marshall_fields['BranchUri']

    def get(self, lib_id=None):
        return self._get(lib_id)


marshall_fields['Publisher'] = {
    'publisher_id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
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
    'book': fields.Nested(marshall_fields['BookUri'],
                          attribute=lambda copy: copy.get_book()),
    'branch': fields.Nested(marshall_fields['BranchUri'],
                            attribute=lambda copy: copy.get_branch()),
    'is_reserved': fields.Boolean(attribute=lambda copy: copy.reserver() is not None),
    'is_borrowed': fields.Boolean(attribute=lambda copy: copy.borrower() is not None),
    'uri': fields.Url('copyresource')
}


class CopyResource(LibraryResource):
    model = Copies
    envelope = 'copies'
    resource_fields = marshall_fields['Copy']
    uri_fields = marshall_fields['CopyUri']

    def get(self, copy_id=None):
        return self._get(copy_id)


marshall_fields['Borrow'] = {
    'borrow_id': fields.Integer,
    'copy': fields.Nested(marshall_fields['CopyUri'],
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
    'copy': fields.Nested(marshall_fields['CopyUri'],
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


api.add_resource(AuthorResource, '/authors/', '/authors/<int:author_id>')
api.add_resource(BookResource, '/books/', '/books/<int:book_id>')
api.add_resource(BranchResource, '/branches/', '/branches/<int:lib_id>')
api.add_resource(PublisherResource, '/publishers/', '/publishers/<int:publisher_id>')
api.add_resource(ReaderResource, '/readers/', '/readers/<int:reader_id>')
api.add_resource(CopyResource, '/copies/', '/copies/<int:copy_id>')
api.add_resource(BorrowResource, '/borrows/', '/borrows/<int:borrow_id>')
api.add_resource(ReserveResource, '/reserves/', '/reserves/<int:reserve_id>')
api.add_resource(CopyCheckoutResource, '/readers/<int:reader_id>/checkout')
api.add_resource(CopyReturnResource, '/readers/<int:reader_id>/return')
api.add_resource(CopyReserveResource, '/readers/<int:reader_id>/reserve')
api.add_resource(CopyCancelResource, '/readers/<int:reader_id>/cancel')


def run(db_path='library.db', debug=False):
    app.config['DB_PATH'] = db_path
    app.run(debug=debug)

if __name__ == '__main__':
    run(debug=False)