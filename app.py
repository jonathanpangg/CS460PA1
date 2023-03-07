import flask, uuid
from flask import Flask, flash, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
from datetime import date
import flask_login

#for image uploading 
import os, base64

mysql = MySQL()
app = Flask(__name__, template_folder= 'templates')
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'J@1323002448232j'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from RegisteredUsers")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from RegisteredUsers")
	return cursor.fetchall()

# class registeredUser(mysql.app):
# 	userID = mysql.Column(mysql.Integer, primary_key = True)
# 	firstName = mysql.Column(mysql.CHAR(25))
# 	lastName = mysql.Column(mysql.CHAR(25))
# 	email = mysql.Column(mysql.VARCHAR(255), primary_key = True)
# 	dateofBirth = mysql.Column(mysql.Date)
# 	hometown = mysql.Column(mysql.CHAR(25))
# 	gender = mysql.Column(mysql.CHAR(25))
# 	userPassword = mysql.Column(mysql.VARCHAR(25))
# 	contributionScore = mysql.Column(mysql.Integer)
	

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT userPassword FROM RegisteredUsers WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['userPassword'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='userPassword' name='userPassword' id='userPassword' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT userPassword FROM RegisteredUsers WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['userPassword'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file
	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('loggedOut.html', message='Logged out')

@app.route('/friends', methods=['GET', 'POST'])
@flask_login.login_required
def friends():
    flask.user = flask_login.current_user.get_id()
    cursor = conn.cursor()
    if request.method == 'GET':
        try:
            cursor.execute("SELECT friendEmail FROM Friends WHERE userEmail = '{0}'".format(flask.user))
            return render_template('friends.html', data = cursor.fetchall())
        except:
            return render_template('friends.html', data = 'You have no friends :)')
    # post request for adding friends
    else:
        friendID = request.form['caption']
        cursor.execute("INSERT INTO Friends(userEmail, friendEmail) VALUES ('{0}', '{1}')".format(flask.user, friendID))
        conn.commit()
        return flask.redirect(flask.url_for('friends'), code = 303)
    
@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		c1 = conn.cursor()
		c1.execute("SELECT COUNT(*) FROM RegisteredUsers")
		userID = c1.fetchone()[0]
		
		firstName = request.form.get('firstName')
		lastName = request.form.get('lastName')
		email=request.form.get('email')
		dateOfBirth =request.form.get('dateOfBirth')
		hometown =request.form.get('hometown')
		gender=request.form.get('gender')
		userPassword=request.form.get('userPassword')	
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO RegisteredUsers (userID, firstName, lastName, email, dateOfBirth, hometown, gender, userPassword) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')"
		       .format(userID, firstName, lastName, email, dateOfBirth, hometown, gender, userPassword)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		flash("This email has already been used. Please login with that email or create a new account using a different email")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid, tag):    
	cursor = conn.cursor()
	if tag == None:
		cursor.execute("SELECT photoData, photoID, caption, tagWord FROM Photos WHERE userID = '{0}'".format(uid))
	else:
		listOfTags = tag.split(', ')
		selectStatement = "tagWord LIKE "
		for i in range(0, len(listOfTags)):
			if i + 1 == len(listOfTags):
				selectStatement += '\'%' + listOfTags[i] + '%\''
			else: 
				selectStatement += '\'%' + listOfTags[i] + '%\' OR tagWord LIKE '
		cursor.execute("SELECT photoData, photoID, caption, tagWord FROM Photos WHERE userID = '{0}' AND ({1})".format(uid, selectStatement))
	return cursor.fetchall() #NOTE return a list of tuples, [(photoData, pid, caption), ...]

def getAllPhotos(tags):
	cursor = conn.cursor()
	if tags == None:
		cursor.execute("SELECT photoData, photoID, caption, tagWord, numOfLiked, comments FROM Photos")
	else: 
		listOfTags = tags.split(', ')
		selectStatement = "tagWord LIKE "
		for i in range(0, len(listOfTags)):
			if i + 1 == len(listOfTags):
				selectStatement += '\'%' + listOfTags[i] + '%\''
			else: 
				selectStatement += '\'%' + listOfTags[i] + '%\' OR tagWord LIKE '
		cursor.execute("SELECT photoData, photoID, caption, tagWord, numOfLiked, comments FROM Photos WHERE userID = ({0})".format(selectStatement))
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM RegisteredUsers WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Albums WHERE ownerID = '{0}'".format(uid))
	return cursor.fetchall()

def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Albums")
	return cursor.fetchall()

def getUserPhotosinAlbum(albumID):
	cursor = conn.cursor()
	cursor.execute("SELECT photoData, photoID, caption, tagWord FROM Photos WHERE albumID = '{0}'".format(albumID))
	return cursor.fetchall()

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM RegisteredUsers WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

def updateContributionScore():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(*) FROM RegisteredUsers WHERE userID = '{0}'".format(uid))
	photoCount = cursor.fetchall()[0][0]
	cursor.execute("SELECT COUNT(*) FROM Comments WHERE email = '{0}'".format(flask_login.current_user.id))
	commentCount = cursor.fetchall()[0][0]
	cursor.execute("UPDATE RegisteredUsers SET contributionScore = '{0}' WHERE userID = '{1}'".format(commentCount + photoCount, uid))
	conn.commit()
	print(photoCount + commentCount)



def getMostPopularTags():
    dict = {}
    cursor = conn.cursor()
    cursor.execute("SELECT tagWord From Photos")
    
    for i in cursor.fetchall():
        list = i[0].split(", ")
        for j in list: 
            if j in dict:
                dict[j] += 1
            else:
                dict[j] = 1
    
    sortedDict = sorted(dict.items(), key=lambda x:x[1], reverse = True)
    res = []
    if len(sortedDict) < 3:
        for i in range(0, len(sortedDict)):
            res.append(sortedDict[i][0])
    else:
        res = [sortedDict[0][0], sortedDict[1][0], sortedDict[2][0]]
    return res
    
@app.route('/profile')
@flask_login.login_required
def protected():
	updateContributionScore()
	cursor = conn.cursor()
	cursor.execute("SELECT contributionScore FROM RegisteredUsers WHERE userID = '{0}'".format(getUserIdFromEmail(flask_login.current_user.id)))
	contributionScore = cursor.fetchall()[0][0]
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile", contributionScore = contributionScore)
    
#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		userID = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tag = request.form.get('tag')
		photo_data =imgfile.read()

		photoID = uuid.uuid4().int & (1<<16)-1
		cursor = conn.cursor()
		if tag != None:
			cursor.execute('''INSERT INTO Photos (photoID, userID, caption, photoData, albumID, tagWord, comments) VALUES (%s, %s, %s, %s, %s, %s, %s)''', (photoID, userID, caption, photo_data, None, tag, None))
		else:
			cursor.execute('''INSERT INTO Photos (photoID, userID, caption, photoData, albumID, tagWord, comments) VALUES (%s, %s, %s, %s, %s, %s, %s)''', (photoID, userID, caption, photo_data, None, None, None))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(userID, None), base64=base64)
		#The method is GET so we return a HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

#default page
@app.route("/", methods=['GET'])
def hello():
	if flask_login.current_user.is_authenticated == False:
		return render_template('loggedOut.html', message='Welecome to Photoshare')
	
	updateContributionScore()
	cursor = conn.cursor()
	cursor.execute("SELECT contributionScore FROM RegisteredUsers WHERE userID = '{0}'".format(getUserIdFromEmail(flask_login.current_user.id)))
	contributionScore = cursor.fetchall()[0][0]
	return render_template('hello.html', message='Welecome to Photoshare', contributionScore = contributionScore)

@app.route("/photos", methods = ['GET', 'POST'])
def photos():
	if flask_login.current_user.is_authenticated == False:
		tag = request.form.get('tagWord')
		photo = getAllPhotos(tag)
		return render_template('allPhotos.html', allPhotos = photo, getTag = tag, base64=base64)
	else:
		userID = getUserIdFromEmail(flask_login.current_user.id)

		if request.method == 'POST':
			photoID = request.form # [photoID, 'Delete']
			res = ""
			val = ""
			for key in photoID.keys():
				for value in photoID.getlist(key):
					res = key
					val = value
			# delete request
			if val == "Delete":
				cursor = conn.cursor()
				cursor.execute("DELETE FROM Photos WHERE photoID = '{0}'".format(res))
				conn.commit()
				photo = getUsersPhotos(userID, None)
				return render_template('photos.html', photos = photo, getTag = None, base64=base64)
			# post request for filter by tags
			else: 
				tag = request.form.get('tagWord')
				photo = getUsersPhotos(userID, tag)
				return render_template('photos.html', photos = photo, getTag = tag, base64=base64)
		# get request for all user photos
		else:
			photo = getUsersPhotos(userID, None)
			return render_template('photos.html', photos = photo, getTag = None, base64=base64)

@app.route("/allPhotos", methods = ['GET', 'POST'])
def allPhotos():
	if request.method == 'GET':
		if User() == None or flask_login.current_user.is_authenticated == False:
			return render_template('allPhotos.html', allPhotos = getAllPhotos(None), popularTags = getMostPopularTags(), auth = False, base64=base64)
		return render_template('allPhotos.html', allPhotos = getAllPhotos(None), popularTags = getMostPopularTags(), auth = True, base64=base64)
	else:
		if User() == None or flask_login.current_user.is_authenticated == False:
			return render_template('allPhotos.html', allPhotos = getAllPhotos(None), popularTags = getMostPopularTags(), auth = False, base64=base64)
	    
		photoID = request.form
		res = ""
		for key in photoID.keys():
			for value in photoID.getlist(key):
				res = key
				if value == 'Add':
					break 
			else:
				continue
			break
        
		print(photoID)
		cursor = conn.cursor()
		print(res[3:])
        
		if res[0:3] == 'Com':
			comment = request.form.get(res[3:])
			if comment != None:
				cursor.execute("SELECT comments FROM Photos WHERE photoID = '{0}'".format(res[3:]))
				oldComment = cursor.fetchall()
				newComment = ""
				for i in oldComment:
					if i[0] == None:
						newComment =  "" + "*" + comment
					else:
						newComment =  "{0}".format(i[0]) + "*" + comment
				print(newComment)
				commentID = uuid.uuid4().int & (1<<16)-1
				cursor.execute("UPDATE Photos SET comments = '{0}' WHERE photoID = '{1}'".format(newComment, res[3:])) 
				
				if flask_login.current_user.is_authenticated == False:
					cursor.execute("INSERT INTO Comments(commentID, textData, photoID, email, commentDate) VALUES ('{0}', '{1}', '{2}', '{3}', '{4})".format(commentID, comment, res[3:], -1, date.today()))
				else:
					cursor.execute("INSERT INTO Comments(commentID, textData, photoID, email, commentDate) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(commentID, comment, res[3:], flask_login.current_user.id, date.today()))
				conn.commit()
		else:
			cursor.execute("SELECT numOfLiked FROM Photos WHERE photoID = '{0}'".format(res))
			likes = cursor.fetchall()[0][0]
			cursor.execute("SELECT email FROM LikedPhotos WHERE photoID = '{0}'".format(res))
			users = cursor.fetchall()
			
			for i in users:
				if i[0] == flask_login.current_user.id:
					return render_template('allPhotos.html', allPhotos = getAllPhotos(None), popularTags = getMostPopularTags(), auth = True, base64=base64)
			if likes == None:
				likes = 1
			else:
				likes += 1
				
			cursor.execute("UPDATE Photos SET numOfLiked = '{0}' WHERE photoID = '{1}'".format(likes, res))
			cursor.execute("INSERT INTO LikedPhotos (photoID, email) VALUES ('{0}', '{1}')".format(res, flask_login.current_user.id))
			conn.commit()
		cursor.execute("SELECT photoID, textData, email, commentDate FROM Comments")
		info = cursor.fetchall()
		return render_template('allPhotos.html', allPhotos = getAllPhotos(None), popularTags = getMostPopularTags(), commentsInfo = info, auth = True, base64=base64)

@app.route('/albums', methods = ['GET', 'POST'])
def albums():
	if flask_login.current_user.is_authenticated == False:
		print("We show all albums")
		return render_template('albums.html', allAlbums = getAllAlbums())
	else:
		userID = getUserIdFromEmail(flask_login.current_user.id)
		if request.method == 'POST':
			data = request.form
			res = ""
			val = ""
			print(data)
			for key in data.keys():
				for value in data.getlist(key):
					res = key
					val = value
			if val == "Delete This Album":
				cursor = conn.cursor()
				cursor.execute("SELECT photoID FROM Photos WHERE albumID = '{0}'".format(res))
				photoIDs = cursor.fetchall()
				print(photoIDs)
				print(photoIDs[0])
				for x in photoIDs:
					cursor.execute("DELETE FROM LikedPhotos WHERE photoID = '{0}'".format(x[0]))
					cursor.execute("DELETE FROM Comments WHERE photoID = '{0}'".format(x[0]))
					cursor.execute("DELETE FROM Photos WHERE photoID = '{0}'".format(x[0]))
				cursor.execute("DELETE FROM Albums WHERE albumID = '{0}'".format(res))				
				conn.commit()
				# cursor.execute("DELETE FROM Albums WHERE albumID = '{0}'".format(res))
				# cursor.execute("DELETE FROM Photos WHERE albumID = '{0}'".format(res))
				# cursor.commit()
				flash('You have sucessfully deleted your album along with all of its photos!')
				return render_template('albums.html', myAlbums = getUsersAlbums(userID))
		return render_template('albums.html', myAlbums = getUsersAlbums(userID))

@app.route('/albums/<albumID>')
def alltheAlbums(albumID):
	return render_template('albumPictures.html', albumID = albumID, albumPictures = getUserPhotosinAlbum(albumID), base64=base64)

@app.route("/allAlbums")
def allAlbums():
	return render_template('albums.html', allAlbums = getAllAlbums())

@app.route("/newAlbum", methods = ['GET', 'POST'])
def newAlbum():
	if flask_login.current_user.is_authenticated == False:
		return render_template('unauth.html')
	else: 
		ownerID = getUserIdFromEmail(flask_login.current_user.id)
		if request.method == 'POST':
			photoID = request.form #[photoID, ADD]
			print(photoID)
			res = ""
			val = ""
			newAlbumID = uuid.uuid4().int & (1<<16)-1
			for key in photoID.keys():
				for value in photoID.getlist(key):
					res = key
					val = value
					if res == "albumName":
						albumName = val
						dateOfCreation = date.today()
						cursor = conn.cursor()
						cursor.execute('''INSERT INTO Albums (albumID, albumName, ownerID, dateOfCreation) VALUES (%s, %s, %s, %s)''', (newAlbumID, albumName, ownerID, dateOfCreation))
						conn.commit()
					if val == "Add":
						cursor = conn.cursor()
						cursor.execute("UPDATE Photos SET albumID = '{0}' WHERE photoID = '{1}'".format(newAlbumID, res))
						conn.commit()
			return render_template('albumPictures.html', albumID = newAlbumID, albumPictures = getUserPhotosinAlbum(newAlbumID), base64=base64)
			#The method is GET so we return a  HTML form to upload the a photo.
		else:
			return render_template('newAlbum.html', photos = getUsersPhotos(ownerID, None), base64=base64)

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
