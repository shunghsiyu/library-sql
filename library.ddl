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

CREATE INDEX "idx_wrote__bookid" ON "Wrote" ("bookId")