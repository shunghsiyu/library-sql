#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from datetime import datetime
from library import *
import sqlite3
import unittest

__author__ = 'shunghsiyu'


class LibrarySQL(unittest.TestCase):
    db_path = ':memory:'
    create_script = 'library.ddl'
    conn = None

    def setUp(self):
        self.conn = start(self.db_path, self.create_script)

    def tearDown(self):
        self.conn.close()

    def test_add_get_authors(self):
        name = "An Author"
        Authors.add(self.conn, name)
        author_id = 1
        author = Authors.get(self.conn, author_id)

        self.assertIsNotNone(author)
        self.assertEqual(author.author_id, author_id)
        self.assertEqual(author.name, name)

    def test_add_get_readers(self):
        name = "A Reader"
        address = "An Address"
        phone = "1234567890"
        Readers.add(self.conn, name, address, phone)
        reader_id = 1
        reader = Readers.get(self.conn, reader_id)

        self.assertIsNotNone(reader)
        self.assertEqual(reader.reader_id, reader_id)
        self.assertEqual(reader.name, name)
        self.assertEqual(reader.address, address)
        self.assertEqual(reader.phone, phone)

    def test_get_borrows_reader_empty(self):
        reader_id = self.add_reader()
        reader = Readers.get(self.conn, reader_id)
        borrows = reader.get_borrows()

        self.assertIsNotNone(borrows)
        self.assertEqual(len(borrows), 0)

    def test_get_reserves_reader_empty(self):
        reader_id = self.add_reader()
        reader = Readers.get(self.conn, reader_id)
        reserves = reader.get_reserves()

        self.assertIsNotNone(reserves)
        self.assertEqual(len(reserves), 0)

    def test_add_publishers(self):
        name = self.dummy_publisher['name']
        address = self.dummy_publisher['address']
        publisher = Publishers.add(self.conn, name, address)
        self.assertIsNotNone(publisher)
        self.assertIsNotNone(publisher.publisher_id)
        self.assertEqual(publisher.name, name)
        self.assertEqual(publisher.address, address)

    def test_add_publishers_fail(self):
        name = None
        address = self.dummy_publisher['address']
        with self.assertRaises(sqlite3.Error):
            Publishers.add(self.conn, name, address)

    def test_get_publishers(self):
        publisher_id = self.add_publisher()
        name = self.dummy_publisher['name']
        address = self.dummy_publisher['address']
        publisher = Publishers.get(self.conn, publisher_id)
        self.assertIsNotNone(publisher)
        self.assertEqual(publisher.publisher_id, publisher_id)
        self.assertEqual(publisher.name, name)
        self.assertEqual(publisher.address, address)

    def test_add_branches(self):
        name = self.dummy_branch['name']
        location = self.dummy_branch['location']
        branch = Branches.add(self.conn, name, location)
        self.assertIsNotNone(branch)
        self.assertIsNotNone(branch.lib_id)
        self.assertEqual(branch.name, name)
        self.assertEqual(branch.location, location)

    def test_add_branches_fail(self):
        name = None
        location = self.dummy_branch['location']
        with self.assertRaises(sqlite3.Error):
            Branches.add(self.conn, name, location)

    def test_get_branches(self):
        lib_id = self.add_branch()
        name = self.dummy_branch['name']
        location = self.dummy_branch['location']
        branch = Branches.get(self.conn, lib_id)
        self.assertIsNotNone(branch)
        self.assertEqual(branch.lib_id, lib_id)
        self.assertEqual(branch.name, name)
        self.assertEqual(branch.location, location)

    def test_add_books(self):
        title = self.dummy_book['title']
        isbn = self.dummy_book['ISBN']
        publisher_id = self.add_publisher()
        publish_date = self.dummy_book['publisher_date']
        book = Books.add(self.conn, title, isbn, publisher_id,
                         publish_date)
        self.assertIsNotNone(book)
        self.assertIsNotNone(book.book_id)
        self.assertEqual(book.title, title)
        self.assertEqual(book.isbn, isbn)
        self.assertEqual(book.pubisher_id, publisher_id)
        self.assertEqual(book.publish_date, publish_date)

    def test_add_books_fail(self):
        title = self.dummy_book['title']
        isbn = self.dummy_book['ISBN']
        publisher_id = -1
        publish_date = self.dummy_book['publisher_date']
        with self.assertRaises(sqlite3.Error):
            Books.add(self.conn, title, isbn, publisher_id,
                      publish_date)

    def test_get_books(self):
        title = self.dummy_book['title']
        isbn = self.dummy_book['ISBN']
        publisher_id = self.add_publisher()
        publish_date = self.dummy_book['publisher_date']
        book_id = self.add_book(publisher_id=publisher_id)
        book = Books.get(self.conn, book_id)
        self.assertIsNotNone(book)
        self.assertEqual(book.book_id, book_id)
        self.assertEqual(book.title, title)
        self.assertEqual(book.isbn, isbn)
        self.assertEqual(book.pubisher_id, publisher_id)
        self.assertEqual(book.publish_date, publish_date)

    def test_add_copies(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        copy = Copies.add(self.conn, book_id, lib_id)
        self.assertIsNotNone(copy)
        self.assertIsNotNone(copy.number)
        self.assertEqual(copy.book_id, book_id)
        self.assertEqual(copy.lib_id, lib_id)

    def test_get_copies(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        number = 1
        copy_id = self.add_copy(number, book_id, lib_id)
        copy = Copies.get(self.conn, copy_id)
        self.assertIsNotNone(copy)
        self.assertEqual(copy.number, number)
        self.assertEqual(copy.book_id, book_id)
        self.assertEqual(copy.lib_id, lib_id)

    def test_max_number_copies_zero(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        max_number = Copies.max_number(self.conn, book_id, lib_id)
        self.assertEqual(max_number, 0)

    def test_max_number_copies_one(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        number = 1
        self.add_copy(number, book_id, lib_id)
        max_number = Copies.max_number(self.conn, book_id, lib_id)
        self.assertEqual(max_number, 1)

    def test_is_reserved_copy_false(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        number = 1
        copy_id = self.add_copy(number, book_id, lib_id)
        copy = Copy(self.conn, copy_id, number, book_id, lib_id)
        result = copy.is_reserved()
        self.assertFalse(result)

    def test_is_borrowed_copy_false(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        number = 1
        copy_id = self.add_copy(number, book_id, lib_id)
        copy = Copy(self.conn, copy_id, number, book_id, lib_id)
        result = copy.is_borrowed()
        self.assertFalse(result)

    def test_add_borrows(self):
        start_time = datetime.utcnow()
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        number = 1
        copy_id = self.add_copy(number, book_id, lib_id)
        copy = Copies.get(self.conn, copy_id)
        reader_id = self.add_reader()
        name = self.dummy_reader['name']
        address = self.dummy_reader['address']
        phone = self.dummy_reader['phone']
        reader = Reader(self.conn, reader_id, name, address, phone)
        borrow = Borrows.add(self.conn, copy, reader)
        self.assertIsNotNone(borrow)
        self.assertEqual(borrow.copy_id, copy_id)
        self.assertTrue(start_time < borrow.b_datetime)
        self.assertTrue(borrow.b_datetime < datetime.utcnow())
        self.assertIsNone(borrow.r_datetime)

    def test_add_reserves(self):
        start_time = datetime.utcnow()
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        number = 1
        copy_id = self.add_copy(number, book_id, lib_id)
        copy = Copies.get(self.conn, copy_id)
        reader_id = self.add_reader()
        reader = Readers.get(self.conn, reader_id)
        reserve = Reserves.add(self.conn, copy, reader)
        self.assertIsNotNone(reserve)
        self.assertEqual(reserve.copy_id, copy.copy_id)
        self.assertTrue(start_time < reserve.rv_datetime)
        self.assertTrue(reserve.rv_datetime < datetime.utcnow())
        self.assertTrue(reserve.is_reserved)

    def test_reserve_get_reserves_reader(self):
        start_time = datetime.utcnow()
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        number = 1
        copy_id = self.add_copy(number, book_id, lib_id)
        copy = Copies.get(self.conn, copy_id)
        reader_id = self.add_reader()
        reader = Readers.get(self.conn, reader_id)
        reader.reserve(copy)
        reserves = reader.get_reserves()
        self.assertIsNotNone(reserves)
        self.assertEqual(len(reserves), 1)
        reserve = reserves[0]
        self.assertIsNotNone(reserve)
        self.assertEqual(reserve.copy_id, copy.copy_id)
        self.assertTrue(start_time < reserve.rv_datetime)
        self.assertTrue(reserve.rv_datetime < datetime.utcnow())
        self.assertTrue(reserve.is_reserved)

    def test_cancel_reader(self):
        reader = Readers.get(self.conn, self.add_reader())
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        copy = Copies.add(self.conn, book_id, lib_id)
        reserve = \
            Reserves.add(self.conn, copy, reader)
        reader.cancel(copy)
        reserve = Reserves.get(self.conn, reserve.reserve_id)
        self.assertIsNotNone(reserve)
        self.assertFalse(reserve.is_reserved)

    def test_borrow_get_borrows_reader(self):
        start_time = datetime.utcnow()
        reader = Readers.get(self.conn, self.add_reader())
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        copy = Copies.add(self.conn, book_id, lib_id)
        reader.checkout(copy)
        checkouts = reader.get_borrows()
        self.assertIsNotNone(checkouts)
        self.assertEqual(len(checkouts), 1)
        checkout = checkouts[0]
        self.assertIsNotNone(checkout)
        self.assertEqual(checkout.copy_id, copy.copy_id)
        self.assertTrue(start_time < checkout.b_datetime)
        self.assertTrue(checkout.b_datetime < datetime.utcnow())
        self.assertIsNone(checkout.r_datetime)
        fine = checkout.calculate_fine()
        self.assertIsNotNone(fine)
        self.assertTrue(fine.is_nan())

    def test_retrn_reader(self):
        start_time = datetime.utcnow()
        reader = Readers.get(self.conn, self.add_reader())
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        lib_id = self.add_branch()
        copy = Copies.add(self.conn, book_id, lib_id)
        borrow = Borrows.add(self.conn, copy, reader)
        b_datetime = borrow.b_datetime
        reader.retrn(copy)
        checkouts = reader.get_borrows()
        self.assertIsNotNone(checkouts)
        self.assertEqual(len(checkouts), 1)
        checkout = checkouts[0]
        self.assertIsNotNone(checkout)
        self.assertEqual(checkout.copy_id, copy.copy_id)
        self.assertTrue(start_time < checkout.b_datetime)
        self.assertTrue(checkout.b_datetime == b_datetime)
        self.assertTrue(checkout.b_datetime < datetime.utcnow())
        self.assertIsNotNone(checkout.r_datetime)
        self.assertTrue(start_time < checkout.r_datetime)
        self.assertTrue(checkout.r_datetime < datetime.utcnow())
        fine = checkout.calculate_fine()
        self.assertIsNotNone(fine)
        self.assertEqual(fine, Decimal('0'))

    def test_search_title_books_empty(self):
        publisher_id = self.add_publisher()
        self.add_book(publisher_id=publisher_id)
        books = Books.search_title(self.conn, "A Random Title")
        self.assertIsNotNone(books)
        self.assertEqual(len(books), 0)

    def test_search_title_books_found(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        books = Books.search_title(self.conn,
                                   self.dummy_book['title'])
        book = Books.get(self.conn, book_id)
        self.assertIsNotNone(books)
        self.assertEqual(len(books), 1)
        self.assertIsNotNone(book)
        self.assertEqual(books[0].book_id, book.book_id)
        self.assertEqual(books[0].title, book.title)
        self.assertEqual(books[0].isbn, book.isbn)
        self.assertEqual(books[0].pubisher_id, book.pubisher_id)
        self.assertEqual(books[0].publish_date, book.publish_date)

    def test_search_publisher_name_books_empty(self):
        publisher_id = self.add_publisher()
        self.add_book(publisher_id=publisher_id)
        books = Books.search_publisher_name(self.conn,
                                            "A Random Publisher")
        self.assertIsNotNone(books)
        self.assertEqual(len(books), 0)

    def test_search_publisher_name_books_found(self):
        publisher_id = self.add_publisher()
        book_id = self.add_book(publisher_id=publisher_id)
        books = Books.\
            search_publisher_name(self.conn,
                                  self.dummy_publisher['name'])
        book = Books.get(self.conn, book_id)
        self.assertIsNotNone(books)
        self.assertEqual(len(books), 1)
        self.assertIsNotNone(book)
        self.assertEqual(books[0].book_id, book.book_id)
        self.assertEqual(books[0].title, book.title)
        self.assertEqual(books[0].isbn, book.isbn)
        self.assertEqual(books[0].pubisher_id, book.pubisher_id)
        self.assertEqual(books[0].publish_date, book.publish_date)

    dummy_reader = {'name': 'A Reader',
                    'address': 'An Address',
                    'phone': '1234567890'}

    def add_reader(self, name=dummy_reader['name'],
                   address=dummy_reader['address'],
                   phone=dummy_reader['phone']):
        with self.conn as conn:
            c = conn.cursor()
            c.execute("""
                      INSERT INTO Reader (name, address, phone)
                      VALUES (?, ?, ?)
                      """, (name, address, phone))
        return c.lastrowid

    dummy_branch = {'name': 'A Branch',
                    'location': 'A Branch Location'}

    def add_branch(self, branch_name=dummy_branch['name'],
                   location=dummy_branch['location']):
        with self.conn as conn:
            c = conn.cursor()
            c.execute("""
                      INSERT INTO Branch (branch_name, location)
                      VALUES (?, ?)
                      """, (branch_name, location))
        return c.lastrowid

    dummy_publisher = {'name': 'A Publisher',
                       'address': 'A Publisher Address'}

    def add_publisher(self, name=dummy_publisher['name'],
                      address=dummy_publisher['address']):
        with self.conn as conn:
            c = conn.cursor()
            c.execute("""
                      INSERT INTO Publisher (name, address)
                      VALUES (?, ?)
                      """, (name, address))
        return c.lastrowid

    dummy_book = {'title': 'A Book',
                  'ISBN': '123-457-1576',
                  'publisher_id': 1,
                  'publisher_date': datetime(2015, 1, 1)}

    def add_book(self, title=dummy_book['title'],
                 isbn=dummy_book['ISBN'],
                 publisher_id=dummy_book['publisher_id'],
                 publish_date=dummy_book['publisher_date']):
        with self.conn as conn:
            c = conn.cursor()
            c.execute("""
                      INSERT INTO
                        Book (title, ISBN, publisherId, publishdate)
                      VALUES (?, ?, ?, ?)
                      """, (title, isbn, publisher_id,
                            publish_date.strftime(date_format)))
        return c.lastrowid

    def add_copy(self, number, book_id, lib_id):
        with self.conn as conn:
            c = conn.cursor()
            c.execute("""
                      INSERT INTO Copy (number, bookId, libId)
                      VALUES (?, ?, ?)
                      """, (number, book_id, lib_id))
            copy_id = c.lastrowid
        return copy_id

if __name__ == '__main__':
    unittest.main()
