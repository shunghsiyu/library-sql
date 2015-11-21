SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE IF NOT EXISTS `Author` (
  `authorId` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS `Branch` (
  `libId` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `branch_name` VARCHAR(255) UNIQUE NOT NULL,
  `location` VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `Publisher` (
  `publisherId` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) UNIQUE NOT NULL,
  `address` VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `Book` (
  `bookId` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `ISBN` VARCHAR(255) UNIQUE NOT NULL,
  `publisherId` INTEGER NOT NULL,
  `publishDate` DATE NOT NULL
);

ALTER TABLE `Book` ADD CONSTRAINT `fk_book__publisherId` FOREIGN KEY (`publisherId`) REFERENCES `Publisher` (`publisherId`);

CREATE TABLE IF NOT EXISTS `Copy` (
  `copyId` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `number` INTEGER NOT NULL,
  `bookId` INTEGER NOT NULL,
  `libId` INTEGER NOT NULL
);

ALTER TABLE `Copy` ADD CONSTRAINT `fk_copy__bookId` FOREIGN KEY (`bookId`) REFERENCES `Book` (`bookId`);

ALTER TABLE `Copy` ADD CONSTRAINT `fk_copy__libId` FOREIGN KEY (`libId`) REFERENCES `Branch` (`libId`);

CREATE TABLE IF NOT EXISTS `Reader` (
  `readerId` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `Borrowed` (
  `borrowId` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `copyId` INTEGER NOT NULL,
  `readerId` INTEGER NOT NULL,
  `bdatetime` DATETIME NOT NULL,
  `rdatetime` DATETIME,
  `fine` DOUBLE
);

ALTER TABLE `Borrowed` ADD CONSTRAINT `fk_borrowed__copyId` FOREIGN KEY (`copyId`) REFERENCES `Copy` (`copyId`);

ALTER TABLE `Borrowed` ADD CONSTRAINT `fk_borrowed__readerId` FOREIGN KEY (`readerId`) REFERENCES `Reader` (`readerId`);

CREATE TABLE IF NOT EXISTS `Reserved` (
  `reserveid` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `copyId` INTEGER NOT NULL,
  `readerId` INTEGER NOT NULL,
  `rvdatetime` DATETIME NOT NULL,
  `isreserved` BOOLEAN NOT NULL
);

ALTER TABLE `Reserved` ADD CONSTRAINT `fk_reserved__copyId` FOREIGN KEY (`copyId`) REFERENCES `Copy` (`copyId`);

ALTER TABLE `Reserved` ADD CONSTRAINT `fk_reserved__readerId` FOREIGN KEY (`readerId`) REFERENCES `Reader` (`readerId`);

CREATE TABLE IF NOT EXISTS `Wrote` (
  `authorId` INTEGER NOT NULL,
  `bookId` INTEGER NOT NULL,
  PRIMARY KEY (`authorId`, `bookId`)
);

ALTER TABLE `Wrote` ADD CONSTRAINT `fk_wrote__authorId` FOREIGN KEY (`authorId`) REFERENCES `Author` (`authorId`);

ALTER TABLE `Wrote` ADD CONSTRAINT `fk_wrote__bookId` FOREIGN KEY (`bookId`) REFERENCES `Book` (`bookId`);

CREATE VIEW `AverageFine` AS
  SELECT R.readerId, AVG(B.fine)
  FROM Reader R LEFT OUTER JOIN Borrowed B ON R.readerId = B.readerId
  GROUP BY R.readerId;

CREATE VIEW `MostBorrowed` AS
  SELECT C.libId, B.bookId, COUNT(*) AS Times
  FROM Book B, Copy C, Borrowed R
  WHERE R.copyId = C.copyId
    AND C.bookId = B.bookId
  GROUP BY C.libId, B.bookId
  ORDER BY Times DESC;

CREATE VIEW `FrequentBorrower` AS
  SELECT C.libId, R.readerId, COUNT(*) AS Times
  FROM Borrowed B, Reader R, Copy C
  WHERE B.readerId = R.readerId
    AND B.copyId = C.copyId
  GROUP BY C.libId, R.readerId
  ORDER BY C.libId, Times DESC;