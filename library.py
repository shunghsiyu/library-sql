#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime
from decimal import Decimal
from __builtin__ import tuple
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

    @classmethod
    def get_authors_of(cls, conn, book_id):
        query = """
                SELECT A.authorId, A.name
                FROM Author A, Wrote W
                WHERE A.authorId = W.authorId
                  AND W.bookId = ?
                """
        values = (book_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        authors = [Author(conn, row[0], row[1]) for row in rows]

        return authors

    @classmethod
    def get_all(cls, conn):
        query = """
                SELECT *
                FROM Author
                """

        try:
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        authors = [Author(conn, row[0], row[1]) for row in rows]

        return authors


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
            raise AddBookError

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
        except sqlite3.Error:
            raise

        book = None
        if row:
            book = Book.create_from_books(conn, row)

        return book

    @classmethod
    def get_all(cls, conn, book_id=None, title=None, publisher_name=None, publisher_id=None):
        query = """
                SELECT *
                FROM {}
                  WHERE B.bookId IS NOT NULL
                """
        tables = ['Book B']
        values = []

        if book_id:
            query+= ' AND bookId = ?'
            values.append(book_id)
        if title:
            query+= ' AND title LIKE ?'
            values.append('%'+title+'%')
        if publisher_name:
            tables.append('Publisher P')
            query+= ' AND B.publisherId = P.publisherId'
            query+= ' AND P.name LIKE ?'
            values.append('%'+publisher_name+'%')
        if publisher_id:
            query+= ' AND B.publisherId = ?'
            values.append(publisher_id)

        try:
            c = conn.cursor()
            c.execute(query.format(','.join(tables)), tuple(values))
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        books = [Book.create_from_books(conn, row) for row in rows]

        return books


class Book(object):

    def __init__(self, conn, book_id, title, isbn, publisher_id,
                 publish_date):
        self.conn = conn
        self.book_id = book_id
        self.title = title
        self.isbn = isbn
        self.publisher_id = publisher_id
        if isinstance(publish_date, basestring):
            publish_date = datetime.strptime(publish_date,
                                             date_format)
        self.publish_date = publish_date

    def get_authors(self):
        return Authors.get_authors_of(self.conn, self.book_id)

    def get_publisher(self):
        publisher = Publishers.get(self.conn, self.publisher_id)
        return publisher

    def get_copies(self):
        copies = Copies.get_copies_of(self.conn, self.book_id)
        return copies

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
            reader = Reader.create_from_readers(conn, row)

        return reader

    @classmethod
    def get_all(cls, conn):
        query = """
                SELECT *
                FROM Reader
                """
        try:
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        readers = [Reader.create_from_readers(conn, row)
                   for row in rows]

        return readers

    @classmethod
    def average_fine(cls, conn):
        query = """
                SELECT *
                FROM AverageFine
                """

        try:
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
        except sqlite3.Error:
            raise

        result = [dict(reader=Readers.get(conn, row[0]), fine=row[1])
                  for row in rows]

        return result


class Reader(object):

    @classmethod
    def create_from_readers(cls, conn, row):
        return Reader(conn, row[0], row[1], row[2], row[3])

    def __init__(self, conn, reader_id, name, address, phone):
        self.conn = conn
        self.reader_id = reader_id
        self.name = name
        self.address = address
        self.phone = phone

    def reserve(self, copy):
        return Reserves.add(self.conn, copy, self)

    def cancel(self, copy):
        return Reserves.cancel(self.conn, copy, self)

    def checkout(self, copy):
        return Borrows.add(self.conn, copy, self)

    def retrn(self, copy):
        return Borrows.retrn(self.conn, copy, self)

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

    @classmethod
    def get_copies_of(cls, conn, book_id):
        query = """
                SELECT *
                FROM Copy
                  WHERE bookId = ?
                """
        values = (book_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        copies = [Copy.create_from_copies(conn, row)
                  for row in rows]

        return copies

    @classmethod
    def get_all(cls, conn, book_id=None, lib_id=None, number=None, available=None):
        query = """
                SELECT C.copyId, C.number, C.bookId, C.libId
                FROM {}
                WHERE C.copyId IS NOT NULL
                """
        tables = ['Copy C']
        values = []

        if available is True:
            query += """  AND NOT EXISTS (SELECT R.copyId
                                         FROM Reserved R
                                         WHERE C.copyId = R.copyID
                                           AND R.isReserved = ?

                                         UNION

                                         SELECT B.copyId
                                         FROM Borrowed B
                                         WHERE C.copyId = B.copyId
                                           AND B.rDatetime IS NULL)
                     """
            values.append(True)
        elif available is False:
            query += """  AND NOT EXISTS (SELECT R.copyId
                                          FROM Reserved R
                                          WHERE C.copyId = R.copyID
                                            AND R.isReserved = ?

                                          UNION

                                          SELECT B.copyId
                                          FROM Borrowed B
                                          WHERE C.copyId = B.copyId
                                            AND B.rDatetime IS NOT NULL)
                          AND EXISTS (SELECT B.copyId
                                      FROM Borrowed B
                                      WHERE C.copyId = B.copyId

                                      UNION

                                      SELECT R.copyId
                                      FROM Reserved R
                                      WHERE C.copyId = R.copyId)
                     """
            values.append(False)
        if book_id:
            query += '  AND C.bookId = ?'
            values.append(book_id)
        if lib_id:
            query += '  AND C.libId = ?'
            values.append(lib_id)
        if number:
            query += '  AND C.number = ?'
            values.append(number)

        try:
            c = conn.cursor()
            c.execute(query.format(','.join(tables)), tuple(values))
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        copies = [Copy.create_from_copies(conn, row)
                  for row in rows]

        return copies


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

    def get_book(self):
        return Books.get(self.conn, self.book_id)

    def get_branch(self):
        return Branches.get(self.conn, self.lib_id)

    def borrower(self):
        return Borrows.get_active_borrower(self.conn, self)

    def reserver(self):
        return Reserves.get_active_reserver(self.conn, self)


class Borrows(Table):
    max_borrow_days = 20
    max_active_borrows = 10

    @classmethod
    def add(cls, conn, copy, reader):

        if cls.get_num_active_borrowed_by(conn, reader) > cls.max_active_borrows:
            raise OverBorrowError

        insert = """
                 INSERT INTO
                   Borrowed (copyId, readerId, bDatetime, rDatetime)
                 VALUES (?, ?, ?, NULL);
                 """

        now = datetime.utcnow()

        with conn:
            reserve_by = copy.reserver()
            if copy.borrower():
                raise CopyNotAvailableError
            elif not reserve_by or reserve_by.reader_id == reader.reader_id:
                pass
            elif copy.reserver():
                raise CopyNotAvailableError

            values = (copy.copy_id, reader.reader_id, now)
            try:
                c = conn.cursor()
                c.execute(insert, values)
                borrow_id = c.lastrowid
                if reserve_by and reserve_by.reader_id == reader.reader_id:
                    reader.cancel(copy)
            except sqlite3.Error as e:
                raise e
            return Borrow(conn, borrow_id, copy.copy_id, reader.reader_id, now)

    @classmethod
    def get(cls, conn, borrow_id):
        query = """
                SELECT *
                FROM Borrowed
                WHERE borrowId = ?
                """
        values = (borrow_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        borrow = None
        if row:
            borrow = Borrow.create_from_borrowed(conn, row)

        return borrow

    @classmethod
    def get_all(cls, conn):
        query = """
                SELECT *
                FROM Borrowed
                """

        try:
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        borrows = [Borrow.create_from_borrowed(conn, row)
                   for row in rows]

        return borrows

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
    def get_num_active_borrowed_by(cls, conn, reader):
        query = """
                SELECT COUNT(*)
                FROM Borrowed
                WHERE readerID = ?
                  AND rDatetime IS NULL
                """
        values = (reader.reader_id,)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error:
            raise

        return row[0]

    @classmethod
    def get_active_borrower(cls, conn, copy):
        c = conn.cursor()
        query = """
                SELECT readerID
                FROM Copy C, Borrowed B
                WHERE B.copyId = C.copyId
                  AND C.copyId = ?
                  AND bookId = ?
                  AND rDatetime IS NULL
                  AND fine IS NULL
                """
        values = (copy.copy_id, copy.book_id,)

        try:
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        borrower = None
        if row:
            borrower = Readers.get(conn, row[0])

        return borrower

    @classmethod
    def retrn(cls, conn, copy, reader):
        query = """
                SELECT *
                FROM Borrowed
                WHERE copyId = ?
                  AND readerID = ?
                  AND rDatetime IS NULL
                  AND fine IS NULL
                """

        update = """
                 UPDATE Borrowed
                 SET rDatetime = ?, fine = ?
                 WHERE borrowId = ?
                 """

        now = datetime.utcnow()

        try:
            with conn:
                c = conn.cursor()
                q_values = (copy.copy_id, reader.reader_id)
                c.execute(query, q_values)
                row = c.fetchone()
                if row is None:
                    raise CannotReturnCopyError
                borrow = Borrows.get(conn, row[0])
                u_values = (now, cls._calculate_fine(borrow, now),
                            borrow.borrow_id)
                c.execute(update, u_values)
        except sqlite3.Error as e:
            raise e

        return Borrows.get(conn, row[0])

    @classmethod
    def _calculate_fine(cls, borrow, now):
        if now is None:
            raise RuntimeError('cannot calculate fine')

        date_delta = now.date() - borrow.b_datetime.date()
        day_delta = date_delta.days - Borrows.max_borrow_days
        days_overdue = day_delta if day_delta >= 0 else 0
        fine = Decimal('0.2') * days_overdue

        return str(fine)


class Borrow(object):

    def __init__(self, conn, borrow_id, copy_id, reader_id, b_datetime, r_datetime=None, fine=None):
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
        self.fine = Decimal(fine) if fine else None

    def get_copy(self):
        return Copies.get(self.conn, self.copy_id)

    def get_reader(self):
        return Readers.get(self.conn, self.reader_id)

    @classmethod
    def create_from_borrowed(cls, conn, row):
        return cls(conn, row[0], row[1], row[2], row[3], row[4], row[5])


class Reserves(Table):
    max_active_reserves = 10

    @classmethod
    def add(cls, conn, copy, reader):

        if cls.get_num_active_reserved_by(conn, reader) > cls.max_active_reserves:
            raise OverReserveError

        if copy.borrower() or copy.reserver():
            raise CopyNotAvailableError

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
    def get_all(cls, conn):
        query = """
                SELECT *
                FROM Reserved
                """

        try:
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        reserves = [Reserve.create_from_reserved(conn, row)
                    for row in rows]

        return reserves

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

        all_reserves = [Reserve.create_from_reserved(conn, row)
                        for row in rows]

        return all_reserves

    @classmethod
    def get_num_active_reserved_by(cls, conn, reader):
        query = """
                SELECT COUNT(*)
                FROM Reserved
                WHERE readerID = ?
                  AND isReserved = ?
                """
        values = (reader.reader_id, True)

        try:
            c = conn.cursor()
            c.execute(query, values)
            row = c.fetchone()
        except sqlite3.Error as e:
            raise e

        return row[0]

    @classmethod
    def get_active_reserver(cls, conn, copy):
        c = conn.cursor()
        query = """
                SELECT readerID
                FROM Copy C, Reserved R
                WHERE R.copyId = C.copyId
                  AND C.copyId = ?
                  AND bookId = ?
                  AND isReserved = ?
                """
        values = (copy.copy_id, copy.book_id, True)
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
        query = """
                SELECT *
                FROM Reserved
                WHERE copyId = ?
                  AND readerID = ?
                  AND isReserved = ?
                """

        update = """
                 UPDATE Reserved
                 SET isReserved = ?
                 WHERE reserveId = ?
                 """

        try:
            with conn:
                c = conn.cursor()
                q_values = (copy.copy_id, reader.reader_id, True)
                c.execute(query, q_values)
                row = c.fetchone()
                if row is None:
                    raise CannotCancelReservationError
                reserve = Reserves.get(conn, row[0])
                u_values = (False, reserve.reserve_id)
                c.execute(update, u_values)
        except sqlite3.Error as e:
            raise e

        return Reserves.get(conn, row[0])


class CannotCancelReservationError(Exception):
    pass


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

    def get_copy(self):
        return Copies.get(self.conn, self.copy_id)

    def get_reader(self):
        return Readers.get(self.conn, self.reader_id)

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

    @classmethod
    def get_all(cls, conn):
        query = """
                SELECT *
                FROM Publisher
                """

        try:
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        publishers = [Publisher(conn, row[0], row[1], row[2])
                      for row in rows]

        return publishers


class NoSuchPublisherError(Exception):
    pass


class Publisher(object):

    def __init__(self, conn, publisher_id, name, address):
        self.conn = conn
        self.publisher_id = publisher_id
        self.name = name
        self.address = address

    def get_books(self):
        return Books.get_all(self.conn, publisher_id=self.publisher_id)


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

    @classmethod
    def get_all(cls, conn):
        query = """
                SELECT *
                FROM Branch
                """

        try:
            c = conn.cursor()
            c.execute(query)
            rows = c.fetchall()
        except sqlite3.Error as e:
            raise e

        branches = [Branch(conn, row[0], row[1], row[2])
                    for row in rows]

        return branches


class Branch(object):

    def __init__(self, conn, lib_id, name, location):
        self.conn = conn
        self.lib_id = lib_id
        self.name = name
        self.location = location

    def frequent_borrowers(self, limit=None):
        query = """
                SELECT readerId, Times
                FROM FrequentBorrower
                WHERE libId = ?
                """
        values = [self.lib_id]

        if limit:
            query += ' LIMIT ?'
            values.append(limit)

        try:
            c = self.conn.cursor()
            c.execute(query, tuple(values))
            rows = c.fetchall()
        except sqlite3.Error:
            raise

        results = [dict(reader=Readers.get(self.conn, row[0]),
                        times=row[1])
                   for row in rows]

        return results

    def most_borrowed_books(self, limit=None):
        query = """
                SELECT bookId, Times
                FROM MostBorrowed
                  WHERE libId = ?
                """
        values = [self.lib_id]

        if limit is not None:
            query += ' LIMIT ?'
            values.append(limit)

        try:
            c = self.conn.cursor()
            c.execute(query, tuple(values))
            rows = c.fetchall()
        except sqlite3.Error:
            raise

        result = [dict(book=Books.get(self.conn, row[0]), times=row[1])
                  for row in rows]

        return result


class AddBookError(Exception):
    pass


class CopyNotAvailableError(Exception):
    pass


class CannotReturnCopyError(Exception):
    pass


class OverBorrowError(Exception):
    pass


class OverReserveError(Exception):
    pass


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
    conn.execute('PRAGMA FOREIGN_KEYS = 1;')
    return conn


if __name__ == '__main__':
    start()
