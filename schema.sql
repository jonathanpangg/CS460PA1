CREATE DATABASE IF NOT EXISTS photoDatabase;
USE photoDatabase;
DROP TABLE IF EXISTS RegisteredUsers CASCADE;
DROP TABLE IF EXISTS UnregisteredUsers CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;

CREATE TABLE RegisteredUsers (
    userID INTEGER NOT NULL,
    firstName CHAR(25) NOT NULL,
    lastName CHAR(25) NOT NULL,
    email UNIQUE CHAR(25) NOT NULL,
    dateOfBirth Date,
    hometown CHAR(25),
    gender CHAR(25),
    userPassword CHAR(25) NOT NULL,
    contributionScore INTEGER,
    PRIMARY KEY (userID, email),
		CHECK (contributionScore >= 0)
);

CREATE TABLE UnregisteredUsers (
    newUserID INTEGER NOT NULL,
    PRIMARY KEY (newUserID)
);

CREATE TABLE Friends (
    friendID INTEGER NOT NULL,
    firstName CHAR(25) NOT NULL,
    lastName CHAR(25) NOT NULL,
    FOREIGN KEY (friendID) REFERENCES RegisteredUsers(userID),
    FOREIGN KEY (firstName) REFERENCES RegisteredUsers(firstName)
    FOREIGN KEY (lastName) REFERENCES RegisteredUsers(lastName)
);

CREATE TABLE Albums (
    albumID INTEGER NOT NULL,
    albumName CHAR(25),
    ownerID CHAR(25),
    dateOfCreation Date,
    numPhotos INTEGER
    PRIMARY KEY (albumID),
		CHECK (numOfLiked >= 0)
);

CREATE TABLE Photos (
    photoID INTEGER NOT NULL,
    caption CHAR(225),
    photoData VARBINARY(66635)
    PRIMARY KEY (photoID)
);

CREATE TABLE Tags (
    tagWord CHAR(25) NOT NULL,
    PRIMARY KEY (tagWord)
);

CREATE TABLE Comments (
    commentID INTEGER NOT NULL,
    textData TEXT(65535),
    userID CHAR(25) NOT NULL,
    commentDate Date,
    PRIMARY KEY (commentID),
    FOREIGN KEY (userID) REFERENCES RegisteredUsers(userID)
);