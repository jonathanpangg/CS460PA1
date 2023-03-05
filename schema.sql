CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Photos CASCADE;
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

CREATE TABLE Albums (
    albumID INTEGER NOT NULL,
    albumName CHAR(25),
    ownerID INTEGER NOT NULL,
    dateOfCreation Date,
    numPhotos INTEGER,
    numOfLiked INTEGER,
    FOREIGN KEY (ownerID) REFERENCES RegisteredUsers(userID),
    PRIMARY KEY (albumID),
		CHECK (numOfLiked >= 0)
);

CREATE TABLE Photos (
    photoID INTEGER NOT NULL,
    userID INTEGER NOT NULL,
    caption CHAR(225),
    photoData longblob,
    albumID INTEGER NOT NULL,
    tagWord CHAR(25),
    FOREIGN KEY (albumID) REFERENCES Albums(albumID),
    PRIMARY KEY (photoID),
    FOREIGN KEY (userID) REFERENCES RegisteredUsers(userID)
);

CREATE TABLE Tags (
    tagWord CHAR(25),
    photoID INTEGER NOT NULL,
    FOREIGN KEY (photoID) REFERENCES Photos(photoID)
);

CREATE TABLE Comments (
    commentID INTEGER NOT NULL,
    textData TEXT(65535),
    userID INTEGER NOT NULL,
    commentDate Date,
    PRIMARY KEY (commentID),
    FOREIGN KEY (userID) REFERENCES RegisteredUsers(userID)
);

-- To get first and last name, use a select statement with registered user and friend id
CREATE TABLE Friends (
	userEmail VARCHAR(225) NOT NULL,
    friendEmail VARCHAR(225) NOT NULL,
	FOREIGN KEY (userEmail) REFERENCES RegisteredUsers(email),
    FOREIGN KEY (friendEmail) REFERENCES RegisteredUsers(email),
		CHECK (userEmail <> friendEmail)
);