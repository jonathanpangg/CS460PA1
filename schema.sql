CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS LikedPhotos CASCADE;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS UnregisteredUsers CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS RegisteredUsers CASCADE;

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
    PRIMARY KEY (albumID),
    FOREIGN KEY (ownerID) REFERENCES RegisteredUsers(userID)
);

CREATE TABLE Photos (
    photoID INTEGER NOT NULL,
    userID INTEGER NOT NULL,
    caption CHAR(225),
    photoData longblob,
    albumID INTEGER,
    tagWord CHAR(25),
    numOfLiked INTEGER,
    comments VARCHAR(500),
    PRIMARY KEY (photoID),
    FOREIGN KEY (albumID) REFERENCES Albums(albumID),
    FOREIGN KEY (userID) REFERENCES RegisteredUsers(userID),
		CHECK (numOfLiked >= 0)
);

CREATE TABLE LikedPhotos (
	photoID INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE Comments (
    commentID INTEGER NOT NULL,
    textData VARCHAR(500),
    photoID INTEGER NOT NULL,
    email VARCHAR(255),
    ownerID INTEGER NOT NULL,
    commentDate Date,
    PRIMARY KEY (commentID),
    FOREIGN KEY (photoID) REFERENCES Photos(photoID),
    FOREIGN KEY (ownerID) REFERENCES Photos(userID)
);

-- To get first and last name, use a select statement with registered user and friend id
CREATE TABLE Friends (
	userEmail VARCHAR(225) NOT NULL,
    friendEmail VARCHAR(225) NOT NULL,
	FOREIGN KEY (userEmail) REFERENCES RegisteredUsers(email),
    FOREIGN KEY (friendEmail) REFERENCES RegisteredUsers(email),
		CHECK (userEmail <> friendEmail)
);