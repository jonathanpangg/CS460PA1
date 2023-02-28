CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS RegisteredUsers CASCADE;
DROP TABLE IF EXISTS UnregisteredUsers CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;

CREATE TABLE RegisteredUsers (
    userID INTEGER NOT NULL,
    firstName CHAR(25) NOT NULL,
    lastName CHAR(25) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    dateOfBirth Date,
    hometown CHAR(25),
    gender CHAR(25),
    userPassword VARCHAR(25) NOT NULL,
    contributionScore INTEGER,
    PRIMARY KEY (userID, email),
		CHECK (contributionScore >= 0)
);

CREATE TABLE UnregisteredUsers (
    newUserID INTEGER NOT NULL,
    PRIMARY KEY (newUserID)
);

CREATE TABLE Photos (
    photoID INTEGER NOT NULL,
    caption CHAR(225),
    photoData longblob,
    PRIMARY KEY (photoID)
);

CREATE TABLE Tags (
    tagWord CHAR(25) NOT NULL,
    PRIMARY KEY (tagWord)
);

CREATE TABLE Comments (
    commentID INTEGER NOT NULL,
    textData TEXT(65535),
    userID INTEGER NOT NULL,
    commentDate Date,
    PRIMARY KEY (commentID),
    FOREIGN KEY (userID) REFERENCES RegisteredUsers(userID)
);

CREATE TABLE Albums (
    albumID INTEGER NOT NULL,
    albumName CHAR(25),
    ownerID CHAR(25),
    dateOfCreation Date,
    numPhotos INTEGER,
    numOfLiked INTEGER,
    PRIMARY KEY (albumID),
		CHECK (numOfLiked >= 0)
);

CREATE TABLE Friends (
	userID INTEGER NOT NULL, 
    friendID INTEGER NOT NULL,
    firstName CHAR(25) NOT NULL,
    lastName CHAR(25) NOT NULL,
  --   PRIMARY KEY (friendID),
	FOREIGN KEY (userID) REFERENCES RegisteredUsers(userID),
    FOREIGN KEY (friendID) REFERENCES RegisteredUsers(userID),
    FOREIGN KEY (firstName) REFERENCES RegisteredUsers(firstName),
    FOREIGN KEY (lastName) REFERENCES RegisteredUsers(lastName),
		CHECK (userID <> friendID)
);