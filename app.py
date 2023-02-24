import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading 
import os, base64

@app.route('/register')
def register():
    return render_template('register.html', suppressed='True')