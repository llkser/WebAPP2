from flask import render_template, flash, redirect, Response, session, url_for, request, g
from sqlalchemy import *
from app import app, db, models
from .models import User, Bookshelf, Book
from flask.helpers import make_response

@app.route("/", methods=['GET','POST'])
def bookstore():
    if request.method=='GET':
        Bookstore=Book.query.order_by('BookName').all()
        if 'username' in session:
            userID=User.query.filter(User.UserName==session['username']).first().UserID
            bookshelf=Bookshelf.query.filter(Bookshelf.UserID==userID)
            shelf=[]
            for i in bookshelf:
                bookname=Book.query.filter(Book.BookID==i.BookID).first().BookName
                shelf.append(bookname)
            return render_template('bookstore.html',
                    sidebar=1,
                    username=session['username'],
                    authority=session['authority'],
                    Bookstore=Bookstore,
                    shelf=shelf
            )
        else:
            return render_template('bookstore.html',
                    sidebar=1,
                    Bookstore=Bookstore
            )
    else:
        searchText=request.form.get('searchText')
        Bookstore=Book.query.order_by('BookName').all()
        searchContents=[]
        for book in Bookstore:
            if searchText in book.BookName or searchText in book.Writer:
                searchContents.append(book)
        if 'username' in session:
            userID=User.query.filter(User.UserName==session['username']).first().UserID
            bookshelf=Bookshelf.query.filter(Bookshelf.UserID==userID)
            shelf=[]
            for i in bookshelf:
                bookname=Book.query.filter(Book.BookID==i.BookID).first().BookName
                shelf.append(bookname)
            return render_template('bookstore.html',
                    sidebar=1,
                    username=session['username'],
                    authority=session['authority'],
                    Bookstore=searchContents,
                    shelf=shelf
            )
        else:
            return render_template('bookstore.html',
                    sidebar=1,
                    Bookstore=searchContents
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
            elif User.query.filter(User.UserName==username):
                return render_template('signup.html',
                    warning='User name already be signed up!'
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

@app.route('/add_book/<bookID>')
def add_book(bookID):
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        if Bookshelf.query.count():
            maxID = Bookshelf.query.order_by(desc('ShelfID')).first().ShelfID
        else:
            maxID=0
        shelf=Bookshelf(ShelfID=maxID+1,
            UserID=userID,
            BookID=bookID
        )
        db.session.add(shelf)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('404.html'), 404

@app.route('/myshelf')
def myshelf():
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        if userID:
            shelf=Bookshelf.query.filter(Bookshelf.UserID==userID)
            books=[]
            read={}
            favor={}
            for i in shelf:
                books.append(Book.query.filter(Book.BookID==i.BookID).first())
                read[i.BookID]=i.Read
                favor[i.BookID]=i.Favor
            return render_template('shelf.html',
                    sidebar=2,
                    username=session['username'],
                    authority=session['authority'],
                    Bookshelf=books,
                    read=read,
                    favor=favor
            )
        else:
            session.pop('username')
            session.pop('authority')
            return render_template('404.html'), 404
    else:
        return render_template('404.html'), 404

@app.route('/set_unread/<bookID>')
def set_unread(bookID):
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.BookID==bookID).first()
        shelf.Read=not shelf.Read
        db.session.commit()
        return redirect('/myshelf')
    else:
        return render_template('404.html'), 404

@app.route('/set_read/<bookID>')
def set_read(bookID):
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.BookID==bookID).first()
        shelf.Read=not shelf.Read
        db.session.commit()
        return redirect('/myshelf')
    else:
        return render_template('404.html'), 404

@app.route('/set_favor/<bookID>')
def set_favor(bookID):
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.BookID==bookID).first()
        shelf.Favor=not shelf.Favor
        db.session.commit()
        return redirect('/myshelf')
    else:
        return render_template('404.html'), 404

@app.route('/set_unfavor/<bookID>')
def set_unfavor(bookID):
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.BookID==bookID).first()
        shelf.Favor=not shelf.Favor
        db.session.commit()
        return redirect('/myshelf')
    else:
        return render_template('404.html'), 404

@app.route('/delete_shelf_book/<bookID>')
def delete_shelf_book(bookID):
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.BookID==bookID).first()
        db.session.delete(shelf)
        db.session.commit()
        return redirect('/myshelf')
    else:
        return render_template('404.html'), 404

@app.route('/profile', methods=['GET','POST'])
def profile():
    if request.method=='GET':
        if 'username' in session:
            user=User.query.filter(User.UserName==session['username']).first()
            return render_template('profile.html',
                        sidebar=6,
                        username=session['username'],
                        authority=session['authority'],
                        user=user
                )
        else:
            return render_template('404.html'), 404
    else:
        email=request.form.get('email')
        Phonenumber=request.form.get('Phonenumber')
        QQnumber=request.form.get('QQnumber')
        print(email)
        user=User.query.filter(User.UserName==session['username']).first()
        user.Email=email
        user.Phonenumber=Phonenumber
        user.QQnumber=QQnumber
        db.session.commit()

        return redirect('/profile')

@app.route('/delete_store_book/<bookID>')
def delete_store_book(bookID):
    if 'username' in session and session['authority']==1:
        book=Book.query.filter(Book.BookID==bookID).first()
        db.session.delete(book)
        db.session.commit()
        shelf=Bookshelf.query.filter(Bookshelf.BookID==bookID)
        for i in shelf:
            db.session.delete(i)
            db.session.commit()
        return redirect('/')
    else:
        return render_template('404.html'), 404

@app.route('/showRead')
def showRead():
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        if userID:
            shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.Read==1)
            books=[]
            read={}
            favor={}
            for i in shelf:
                books.append(Book.query.filter(Book.BookID==i.BookID).first())
                read[i.BookID]=i.Read
                favor[i.BookID]=i.Favor
            return render_template('shelf.html',
                    sidebar=3,
                    username=session['username'],
                    authority=session['authority'],
                    Bookshelf=books,
                    read=read,
                    favor=favor
            )
        else:
            session.pop('username')
            session.pop('authority')
            return render_template('404.html'), 404
    else:
        return render_template('404.html'), 404

@app.route('/showUnread')
def showUnread():
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        if userID:
            shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.Read==0)
            books=[]
            read={}
            favor={}
            for i in shelf:
                books.append(Book.query.filter(Book.BookID==i.BookID).first())
                read[i.BookID]=i.Read
                favor[i.BookID]=i.Favor
            return render_template('shelf.html',
                    sidebar=4,
                    username=session['username'],
                    authority=session['authority'],
                    Bookshelf=books,
                    read=read,
                    favor=favor
            )
        else:
            session.pop('username')
            session.pop('authority')
            return render_template('404.html'), 404
    else:
        return render_template('404.html'), 404

@app.route('/showFavor')
def showFavor():
    if 'username' in session:
        userID=User.query.filter(User.UserName==session['username']).first().UserID
        if userID:
            shelf=Bookshelf.query.filter(Bookshelf.UserID==userID,Bookshelf.Favor==1)
            books=[]
            read={}
            favor={}
            for i in shelf:
                books.append(Book.query.filter(Book.BookID==i.BookID).first())
                read[i.BookID]=i.Read
                favor[i.BookID]=i.Favor
            return render_template('shelf.html',
                    sidebar=5,
                    username=session['username'],
                    authority=session['authority'],
                    Bookshelf=books,
                    read=read,
                    favor=favor
            )
        else:
            session.pop('username')
            session.pop('authority')
            return render_template('404.html'), 404
    else:
        return render_template('404.html'), 404



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404