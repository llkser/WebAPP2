from flask import render_template, flash, redirect, Response, session, url_for, request, g
from sqlalchemy import *
from app import app, db, models
from .models import User, Bookshelf, Book
from flask.helpers import make_response

@app.route("/", methods=['GET','POST'])
def bookstore():
    Bookstore=Book.query.order_by('BookName').all()
    if 'username' in session:
        return render_template('bookstore.html',
                sidebar=1,
                username=session['username'],
                authority=session['authority'],
                Bookstore=Bookstore
        )
    else:
        return render_template('bookstore.html',
                sidebar=1,
                Bookstore=Bookstore
        )

@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method=='GET':
        if request.cookies.get('username') and request.cookies.get('password'):
            username=request.cookies.get('username')
            password=request.cookies.get('password')
            user=User.query.filter(User.UserName==username, User.Password==password).first()
            if user:
                session['username']=username
                session['authority']=user.Authority
                session.permanent=True
                return redirect('/')
        else:
            return render_template('signin.html')
    else:
        username=request.form.get('username')
        password=request.form.get('password')
        if username and password:
            remembered=request.form.get('remembered')
            user=User.query.filter(User.UserName==username, User.Password==password).first()
            if user:
                session['username']=username
                session['authority']=user.Authority
                session.permanent=True
                if remembered=='on':
                    Bookstore=Book.query.order_by('BookName').all()
                    resp = make_response(render_template('bookstore.html',
                            sidebar=1,
                            username=session['username'],
                            authority=session['authority'],
                            Bookstore=Bookstore
                    ))
                    resp.set_cookie('username', username)
                    resp.set_cookie('password', password)
                    return resp
                return redirect('/')
            else:
                if User.query.filter(User.UserName==username).first():
                    return render_template('signin.html',
                            warning='Incorrect Password!'
                    )
                else:
                    return render_template('signin.html',
                            warning='Username not found!'
                    )
        else:
            return render_template('signin.html',
                            warning='Data can not be empty!'
                    )

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html')
    else:
        username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        if username and password and email:
            if len(password)<8:
                return render_template('signup.html',
                    warning='Password can not be less than 8 letters!'
                )
            else:
                if User.query.count():
                    maxID = User.query.order_by(desc('UserID')).first().UserID
                else:
                    maxID=0
                user = User(UserID=maxID+1, 
                    UserName=username, 
                    Password=password, 
                    Email=email, 
                    Phonenumber="",
                    QQnumber="",
                    Avater="",
                    Authority=0)
                db.session.add(user)
                db.session.commit()
                return redirect('/')
        else:
            return render_template('signup.html',
                    warning='Data can not be empty!'
            )

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        session.pop('authority')
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404