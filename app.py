import flask
from flask import Flask, flash, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
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
		print("Here1")
		cursor.execute("SELECT photoData, photoID, caption, tagWord FROM Photos WHERE userID = '{0}'".format(uid))
	else:
		print("Here2")
		cursor.execute("SELECT photoData, photoID, caption, tagWord FROM Photos WHERE userID = '{0}' AND tagWord = '{1}'".format(uid, tag))
	return cursor.fetchall() #NOTE return a list of tuples, [(photoData, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT userID FROM RegisteredUsers WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM RegisteredUsers WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")
    
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

		c1 = conn.cursor()
		c1.execute("SELECT COUNT(*) FROM Photos")
		photoID = c1.fetchone()[0]
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Photos (photoID, userID, caption, photoData, tagWord) VALUES (%s, %s, %s, %s, %s)", (photoID, userID, caption, photo_data, tag))
		cursor.execute("INSERT INTO Tags (tagWord, photoID) VALUES ('{0}', '{1}')".format(tag, photoID))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(userID, tag), base64=base64)
		#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

#default page
@app.route("/", methods=['GET'])
def hello():
	if User().is_authenticated == True:
		return render_template('loggedOut.html', message='Welecome to Photoshare')
	return render_template('hello.html', message='Welecome to Photoshare')

@app.route("/photos", methods = ['GET', 'POST'])
def photos():
	if User() is None:
		print("Need to show all photos")
	else :
		userID = getUserIdFromEmail(flask_login.current_user.id)
		if request.method == 'POST':
			tag = request.form.get('tagWord')
			photo = getUsersPhotos(userID, tag)
			return render_template('photos.html', photos = photo, getTag = tag, base64=base64)
		else:
			photo = getUsersPhotos(userID, None)
			return render_template('photos.html', photos = photo, getTag = None, base64=base64)

@app.route("/albums")
def allAlbums():
 	return render_template('albums.html', messages = "These are all the public albums!")

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
