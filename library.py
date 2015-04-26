#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime, timedelta
from decimal import Decimal
import os
import sqlite3

__author__ = 'shunghsiyu'
date_format = '%Y-%m-%d'
datetime_format = '%Y-%m-%d %H:%M:%S.%f'

class Table(object):
    pass


class Authors(Table):
    @classmethod
    def add(cls, conn, name):
        insert = """
                 INSERT INTO Author (name)
                 VALUES (?)
                 """
        values = (name,)
        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
                author_id = c.lastrowid
        except sqlite3.Error:
            raise
        
        return Author(conn, author_id, name)

    @classmethod
    def get(cls, conn, author_id):
        query = """
                SELECT *
                FROM Author
                WHERE authorId = ?
                """
        values = (author_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        author = None
        if row:
            author = Author(conn, row[0], row[1])

        return author


class Author(object):

    def __init__(self, conn, author_id, name):
        self.conn = conn
        self.author_id = author_id
        self.name = name


class Books(Table):

    @classmethod
    def add(cls, conn, title, isbn, publisher_id, publish_date):
        insert = """
                 INSERT INTO
                  Book (title, ISBN, publisherId, publishdate)
                 VALUES (?, ?, ?, ?)
                 """
        assert isinstance(publish_date, datetime)
        values = (title, isbn, publisher_id,
                  publish_date.strftime(date_format))

        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
                book_id = c.lastrowid
        except sqlite3.Error:
            raise

        return Book(conn, book_id, title, isbn, publisher_id,
                    publish_date)

    @classmethod
    def get(cls, conn, book_id):
        query = """
                SELECT *
                FROM Book
                WHERE bookId = ?
                """
        values = (book_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        book = None
        if row:
            book = Book(conn, row[0], row[1], row[2], row[3],
                        row[4])

        return book

    @classmethod
    def search_title(cls, conn, title):
        query = """
                SELECT *
                FROM Book
                WHERE title = ?
                """
        values = (title,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        book = [Book.create_from_books(conn, row) for row in rows]

        return book

    @classmethod
    def search_publisher_name(cls, conn, publisher_name):
        query = """
                SELECT *
                FROM Book B, Publisher P
                WHERE B.publisherId = P.publisherId
                  AND P.name = ?
                """
        values = (publisher_name,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        book = [Book.create_from_books(conn, row) for row in rows]

        return book


class Book(object):

    def __init__(self, conn, book_id, title, isbn, publisher_id,
                 publish_date):
        self.conn = conn
        self.book_id = book_id
        self.title = title
        self.isbn = isbn
        self.pubisher_id = publisher_id
        if isinstance(publish_date, basestring):
            publish_date = datetime.strptime(publish_date,
                                             date_format)
        self.publish_date = publish_date

    @classmethod
    def create_from_books(cls, conn, row):
        return Book(conn, row[0], row[1], row[2], row[3], row[4])


class Readers(Table):

    @classmethod
    def add(cls, conn, name, address, phone):
        insert = """
                 INSERT INTO Reader (name, address, phone)
                 VALUES (?, ?, ?)
                 """
        values = (name, address, phone)

        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
                reader_id = c.lastrowid
        except sqlite3.Error as e:
            raise e

        return Reader(conn, reader_id, name, address, phone)

    @classmethod
    def get(cls, conn, reader_id):
        reader = None
        if reader_id is None:
            return reader

        query = """
                SELECT *
                FROM Reader
                WHERE readerID = ?
                """
        values = (reader_id,)
        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        if row:
            reader = Reader(conn, row[0], row[1], row[2], row[3])

        return reader


class Reader(object):

    def __init__(self, conn, reader_id, name, address, phone):
        self.conn = conn
        self.reader_id = reader_id
        self.name = name
        self.address = address
        self.phone = phone

    def reserve(self, copy):
        return Reserves.add(self.conn, copy, self)

    def cancel(self, copy):
        Reserves.cancel(self.conn, copy, self)

    def checkout(self, copy):
        return Borrows.add(self.conn, copy, self)

    def retrn(self, copy):
        Borrows.retrn(self.conn, copy, self)

    def get_borrows(self):
        return Borrows.get_all_borrowed_by(self.conn, self)

    def get_reserves(self):
        return Reserves.get_all_reserved_by(self.conn, self)


class Copies(Table):
    @classmethod
    def add(cls, conn, book_id, lib_id):
        number = cls.max_number(conn, book_id, lib_id) + 1
        insert = """
                 INSERT INTO Copy (number, bookId, libId)
                 VALUES (?, ?, ?)
                 """
        values = (number, book_id, lib_id)

        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
        except sqlite3.Error as e:
            raise e

        copy_id = c.lastrowid

        return Copy(conn, copy_id, number, book_id, lib_id)

    @classmethod
    def max_number(cls, conn, book_id, lib_id):
        query = """
                SELECT MAX(number)
                FROM Copy
                WHERE bookId = ?
                  AND libId = ?
                """
        values = (book_id, lib_id)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        if row[0]:
            max_number = int(row[0])
        else:
            max_number = 0

        return max_number

    @classmethod
    def get(cls, conn, copy_id):
        query = """
                SELECT *
                FROM Copy
                WHERE copyId = ?
                """
        values = (copy_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        copy = None
        if row:
            copy = Copy.create_from_copies(conn, row)

        return copy


class Copy(object):
    def __init__(self, conn, copy_id, number, book_id, lib_id):
        self.conn = conn
        self.copy_id = copy_id
        self.number = number
        self.book_id = book_id
        self.lib_id = lib_id

    @classmethod
    def create_from_copies(cls, conn, row):
        return cls(conn, row[0], row[1], row[2], row[3])

    def is_borrowed(self):
        return Borrows.get_borrower(self.conn, self)

    def is_reserved(self):
        return Reserves.get_active_reserver(self.conn, self)


class Borrows(Table):
    max_borrow_days = 20

    @classmethod
    def add(cls, conn, copy, reader):
        reserve_by = copy.is_reserved()
        if not reserve_by or reserve_by.reader_id == reader.reader_id:
            pass
        elif copy.is_borrowed() or copy.is_reserved():
            raise RuntimeError('Cannot borrow book')

        insert = """
                INSERT INTO Borrowed (copyId, readerId, bDatetime, rDatetime)
                VALUES (?, ?, ?, NULL);
                """
        now = datetime.utcnow()
        values = (copy.copy_id, reader.reader_id, now)
        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
                borrow_id = c.lastrowid
        except sqlite3.Error as e:
            raise e

        return Borrow(conn, borrow_id, copy.copy_id, reader.reader_id, now)

    @classmethod
    def get_all_borrowed_by(cls, conn, reader):
        query = """
                SELECT *
                FROM Borrowed
                WHERE readerID = ?
                """
        values = (reader.reader_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        all_borrows = [Borrow.create_from_borrowed(conn, row)
                       for row in rows]

        return all_borrows

    @classmethod
    def get_borrower(cls, conn, copy):
        c = conn.cursor()
        query = """
                SELECT readerID
                FROM Copy C, Borrowed B
                WHERE B.copyId = C.copyId
                  AND bookId = ?
                  AND rDatetime IS NULL
                """
        try:
            c.execute(query, (copy.book_id,))
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        borrower = None
        if row:
            borrower = Readers.get(conn, row[0])

        return borrower

    @classmethod
    def retrn(cls, conn, copy, reader):
        borrower = copy.is_borrowed()
        if not borrower or borrower.reader_id != reader.reader_id:
            raise RuntimeError('Cannot return book')

        update = """
                 UPDATE Borrowed
                 SET rDatetime = ?
                 WHERE copyId = ?
                   AND readerID = ?
                   AND rDatetime IS NULL
                 """
        values = (datetime.utcnow(), copy.copy_id, reader.reader_id)

        try:
            with conn:
                conn.execute(update, values)
        except sqlite3.Error as e:
            raise e


class Borrow(object):

    def __init__(self, conn, borrow_id, copy_id, reader_id, b_datetime, r_datetime=None):
        self.conn = conn
        self.borrow_id = borrow_id
        self.copy_id = copy_id
        self.reader_id = reader_id
        if isinstance(b_datetime, basestring):
            b_datetime = datetime.strptime(b_datetime, datetime_format)
        self.b_datetime = b_datetime
        if isinstance(r_datetime, basestring):
            r_datetime = datetime.strptime(r_datetime, datetime_format)
        self.r_datetime = r_datetime

    @classmethod
    def create_from_borrowed(cls, conn, row):
        return cls(conn, row[0], row[1], row[2], row[3], row[4])

    def calculate_fine(self):
        if self.r_datetime is None:
            return Decimal('NaN')

        date_delta = self.r_datetime.date() - self.b_datetime.date()
        assert isinstance(date_delta, timedelta)
        day_delta = date_delta.days - Borrows.max_borrow_days
        days_overdue = day_delta if day_delta >= 0 else 0
        fine = Decimal('0.2') * days_overdue

        return fine


class Reserves(Table):

    @classmethod
    def add(cls, conn, copy, reader):
        if copy.is_borrowed() or copy.is_reserved():
            raise RuntimeError('Cannot reserve book')

        insert = """
                INSERT INTO
                  Reserved (copyId, readerId, rvDatetime, isReserved)
                VALUES (?, ?, ?, ?);
                """
        now = datetime.utcnow()
        values = (copy.copy_id, reader.reader_id, now, True)
        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
                reserve_id = c.lastrowid
        except sqlite3.Error as e:
            raise e

        return Reserve(conn, reserve_id, copy.copy_id, reader.reader_id,
                       now, True)

    @classmethod
    def get(cls, conn, reserve_id):
        query = """
                SELECT *
                FROM Reserved
                WHERE reserveId = ?
                """
        values = (reserve_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error:
            raise

        reserve = None
        if row:
            reserve = Reserve.create_from_reserved(conn, row)

        return reserve

    @classmethod
    def get_all_reserved_by(cls, conn, reader):
        query = """
                SELECT *
                FROM Reserved
                WHERE readerID = ?
                """
        values = (reader.reader_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        all_borrows = [Reserve.create_from_reserved(conn, row)
                       for row in rows]

        return all_borrows

    @classmethod
    def get_active_reserver(cls, conn, copy):
        c = conn.cursor()
        query = """
                SELECT readerID
                FROM Copy C, Reserved R
                WHERE R.copyId = C.copyId
                  AND bookId = ?
                  AND isReserved = ?
                """
        values = (copy.copy_id, True)
        try:
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        reserver = None
        if row:
            reserver = Readers.get(conn, row[0])

        return reserver

    @classmethod
    def cancel(cls, conn, copy, reader):
        reserver = copy.is_reserved()
        if not reserver or reserver.reader_id != reader.reader_id:
            raise RuntimeError('Cannot cancel reservation')

        update = """
                 UPDATE Reserved
                 SET isReserved = ?
                 WHERE copyId = ?
                   AND readerID = ?
                   AND isReserved = ?
                 """
        values = (False, copy.copy_id, reader.reader_id, True)

        try:
            with conn:
                conn.execute(update, values)
        except sqlite3.Error as e:
            raise e


class Reserve(object):

    def __init__(self, conn, reserve_id, copy_id, reader_id,
                 rv_datetime, is_reserved=True):
        self.conn = conn
        self.reserve_id = reserve_id
        self.copy_id = copy_id
        self.reader_id = reader_id
        if isinstance(rv_datetime, basestring):
            rv_datetime = datetime.strptime(rv_datetime,
                                            datetime_format)
        self.rv_datetime = rv_datetime
        self.is_reserved = is_reserved

    @classmethod
    def create_from_reserved(cls, conn, row):
        return cls(conn, row[0], row[1], row[2], row[3], row[4])


class Publishers(Table):

    @classmethod
    def add(cls, conn, name, address):
        insert = """
                 INSERT INTO Publisher (name, address)
                 VALUES (?, ?)
                 """
        values = (name, address)

        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
                publisher_id = c.lastrowid
        except sqlite3.Error as e:
            raise e

        return Publisher(conn, publisher_id, name, address)

    @classmethod
    def get(cls, conn, publisher_id):
        query = """
                SELECT *
                FROM Publisher
                WHERE publisherId = ?
                """
        values = (publisher_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        publisher = None
        if row:
            publisher = Publisher(conn, row[0], row[1], row[2])

        return publisher


class Publisher(object):

    def __init__(self, conn, publisher_id, name, address):
        self.conn = conn
        self.publisher_id = publisher_id
        self.name = name
        self.address = address


class Branches(Table):

    @classmethod
    def add(cls, conn, branch_name, location):
        insert = """
                 INSERT INTO Branch (branch_name, location)
                 VALUES (?, ?)
                 """
        values = (branch_name, location)

        try:
            with conn:
                c = conn.cursor()
                c.execute(insert, values)
                lib_id = c.lastrowid
        except sqlite3.Error:
            raise

        return Branch(conn, lib_id, branch_name, location)

    @classmethod
    def get(cls, conn, lib_id):
        query = """
                SELECT *
                FROM Branch
                WHERE libId = ?
                """
        values = (lib_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        branch = None
        if row:
            branch = Branch(conn, row[0], row[1], row[2])

        return branch


class Branch(object):

    def __init__(self, conn, lib_id, name, location):
        self.conn = conn
        self.lib_id = lib_id
        self.name = name
        self.location = location


def create_tables(conn, create_script):
    c = conn.cursor()
    script = open(create_script).read()
    c.executescript(script)
    conn.commit()


def start(db_path='library.db', create_script='library.ddl'):
    sqlite3.register_adapter(bool, int)
    sqlite3.register_converter("BOOLEAN", lambda v: v != '0')
    if os.path.isfile(db_path):
        conn = sqlite3.connect(db_path)
    else:
        conn = sqlite3.connect(db_path)
        create_tables(conn, create_script)

    return conn


if __name__ == '__main__':
    start()
