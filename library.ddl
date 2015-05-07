PRAGMA FOREIGN_KEYS = 1;

CREATE TABLE "Author" (
  "authorId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT NOT NULL
);

CREATE TABLE "Branch" (
  "libId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "branch_name" TEXT UNIQUE NOT NULL,
  "location" TEXT UNIQUE NOT NULL
);

CREATE TABLE "Publisher" (
  "publisherId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT UNIQUE NOT NULL,
  "address" TEXT UNIQUE NOT NULL
);

CREATE TABLE "Book" (
  "bookId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "title" TEXT NOT NULL,
  "ISBN" TEXT UNIQUE NOT NULL,
  "publisherId" INTEGER NOT NULL REFERENCES "Publisher" ("publisherId"),
  "publishdate" DATE NOT NULL
);

CREATE INDEX "idx_book__publisherid" ON "Book" ("publisherId");

CREATE TABLE "Copy" (
  "copyId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "number" INTEGER NOT NULL,
  "bookId" INTEGER NOT NULL REFERENCES "Book" ("bookId"),
  "libId" INTEGER NOT NULL REFERENCES "Branch" ("libId")
);

CREATE INDEX "idx_copy__bookid" ON "Copy" ("bookId");

CREATE INDEX "idx_copy__libid" ON "Copy" ("libId");

CREATE TABLE "Reader" (
  "readerId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT NOT NULL,
  "address" TEXT NOT NULL,
  "phone" TEXT UNIQUE NOT NULL
);

CREATE TABLE "Borrowed" (
  "borrowId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "copyId" INTEGER NOT NULL REFERENCES "Copy" ("copyId"),
  "readerId" INTEGER NOT NULL REFERENCES "Reader" ("readerId"),
  "bDatetime" DATETIME NOT NULL,
  "rDatetime" DATETIME,
  "fine" TEXT
);

CREATE INDEX "idx_borrowed__copyid" ON "Borrowed" ("copyId");

CREATE INDEX "idx_borrowed__readerid" ON "Borrowed" ("readerId");

CREATE TABLE "Reserved" (
  "reserveId" INTEGER PRIMARY KEY AUTOINCREMENT,
  "copyId" INTEGER NOT NULL REFERENCES "Copy" ("copyId"),
  "readerId" INTEGER NOT NULL REFERENCES "Reader" ("readerId"),
  "rvDatetime" DATETIME NOT NULL,
  "isReserved" BOOLEAN NOT NULL
);

CREATE INDEX "idx_reserved__copyid" ON "Reserved" ("copyId");

CREATE INDEX "idx_reserved__readerid" ON "Reserved" ("readerId");

CREATE TABLE "Wrote" (
  "authorId" INTEGER NOT NULL REFERENCES "Author" ("authorId"),
  "bookId" INTEGER NOT NULL REFERENCES "Book" ("bookId"),
  PRIMARY KEY ("authorId", "bookId")
);

CREATE INDEX "idx_wrote__bookid" ON "Wrote" ("bookId");

CREATE VIEW "AverageFine" AS
  SELECT R.readerId, AVG(B.fine)
  FROM Reader R, Borrowed B
  WHERE R.readerId = B.readerId
  GROUP BY R.readerId;

CREATE VIEW "MostBorrowed" AS
  SELECT C.libId, B.bookId, COUNT(*) AS Times
  FROM Book B, Copy C, Borrowed R
  WHERE R.copyId = C.copyId
    AND C.bookId = B.bookId
  GROUP BY C.libId, B.bookId
  ORDER BY Times DESC;

CREATE VIEW "FrequentBorrower" AS
  SELECT C.libId, R.readerId, COUNT(*) AS Times
  FROM Borrowed B, Reader R, Copy C
  WHERE B.readerId = R.readerId
    AND B.copyId = C.copyId
  GROUP BY C.libId, R.readerId
  ORDER BY C.libId, Times DESC;